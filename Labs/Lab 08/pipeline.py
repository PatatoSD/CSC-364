from __future__ import annotations

import argparse
import queue
import random
import threading
import time
from dataclasses import dataclass, field
from typing import Optional, Union

_print_lock = threading.Lock()
VERBOSE = False

def log(msg: str) -> None:
    ts = time.strftime("%H:%M:%S")
    with _print_lock:
        print(f"{ts} [{threading.current_thread().name:<14}] {msg}")


def log_debug(msg: str):
    if VERBOSE:
        log(msg)

SENTINAL = object()

validOps = ("+", "-", "/", "*", "%")

@dataclass
class Job:
    job_id: int
    operator: str
    a: float
    b: float
    created: float = field(default_factory=time.perf_counter)

@dataclass
class Result:
    job_id: int
    operator: Optional[str]
    a: Optional[float]
    b: Optional[float]
    value: Optional[float]
    ok: bool
    stage: str
    error: Optional[str] = None
    latency: float = 0.0

class PipelineStats:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.total = 0
        self.succeeded = 0
        self.failed = 0
        self.sum_of_results = 0.0
        self.totalLatency = 0.0
        self.maxResult: Optional[float] = None
        self.minResult: Optional[float] = None
        self.by_operator: dict[str, int] = {op: 0 for op in validOps}
        self.errors_by_stage: dict[str, int] = {"validator": 0, "solver": 0}

    def record(self, result: Result) -> None:
        with self.lock:
            self.total += 1
            self.totalLatency += result.latency
            if result.ok:
                self.succeeded += 1
                self.sum_of_results += result.value
                if self.minResult is None or self.minResult > result.value:
                    self.minResult = result.value
                if self.maxResult is None or self.maxResult < result.value:
                    self.maxResult = result.value
                if result.operator in self.by_operator:
                    self.by_operator[result.operator] += 1

            else:
                self.failed += 1
                self.errors_by_stage[result.stage] += 1

    def report(self) -> str:
        with self.lock:
            avgLatency_ms = (self.totalLatency / self.total * 1000) if self.total else 0.0
            lines = [
                "=" * 50,
                "PIPELINE REPORT",
                "=" * 50,
                f"total jobs seen    : {self.total}",
                f"succeeded          : {self.succeeded}",
                f"failed             : {self.failed}",
                f"  - validator errs : {self.errors_by_stage['validator']}",
                f"  - solver errs    : {self.errors_by_stage['solver']}",
                f"sum of results     : {self.sum_of_results:.4f}",
                f"max result         : {self.maxResult}",
                f"min result         : {self.minResult}",
                f"Average Latency(ms): {avgLatency_ms}",
                "by operator (successful only):",
            ]
            for op, count in self.by_operator.items():
                lines.append(f"  {op}: {count}")
            lines.append("=" * 50)
            return "\n".join(lines)

class WorkerShutdownCounter:
    def __init__(self, n: int) -> None:
        self.remaining = n
        self.lock = threading.Lock()

    def worker_done(self) -> bool:
        with self.lock:
            self.remaining -= 1
            return self.remaining == 0

def generator(raw_q: "queue.Queue[Union[Job, object]]", num_jobs: int, malformed_rate: float, rng: random.Random) -> None:
    for job_id in range(num_jobs):
        if rng.random() < malformed_rate:
            bad_choice = rng.choice(["bad_operator", "bad_operand"])
            if bad_choice == "bad_operator":
                job = Job(job_id, operator="^", a=rng.uniform(-100, 100), b=rng.uniform(-100, 100))
            else:
                job = Job(job_id, operator = rng.choice(validOps), a=float("nan"), b=rng.uniform(-100, 100))

        else:
            operator = rng.choice(validOps)
            a = rng.uniform(-100, 100)
            b = 0.0 if rng.uniform(-100, 100) < 0.03  else rng.uniform(-100, 100)
            job = Job(job_id, operator, a, b)

        raw_q.put(job)
        log_debug(f"generated {job}")
    raw_q.put(SENTINAL)
    log(f"Generated {num_jobs} jobs")

def is_number(x) -> bool:
    return isinstance(x, (int, float)) and x == x

def validator(raw_q: "queue.Queue[Union[Job, object]]", valid_q: "queue.Queue[Union[Job, object]]", result_q: "queue.Queue[Union[Job, object]]", num_workers: int) -> None:
    checked = 0
    reject = 0
    while True:
        item = raw_q.get()
        if item is SENTINAL:
            break

        job: Job = item
        checked += 1
        if job.operator not in validOps:
            latency = time.perf_counter() - job.created
            result_q.put(Result(job.job_id, job.operator, job.a, job.b, None, False, stage="validator", error=f"Unknown Operator {job.operator!r}", latency=latency))
            reject += 1
            continue
        if not (is_number(job.a) and is_number(job.b)):
            result_q.put(Result(job.job_id, job.operator, job.a, job.b, None, False, stage="validator", error=f"Unknown Operand {job.a!r} & {job.b!r}"))
            reject += 1
            continue
        valid_q.put(job)

    for n in range(num_workers):
        valid_q.put(SENTINAL)
    log(f"validator done: checked {checked}, rejected {reject}")

def solver(valid_q: "queue.Queue[Union[Job, object]]", result_q: "queue.Queue[Union[Job, object]]", shutdownCount: WorkerShutdownCounter) -> None:
    solved = 0
    while True:
        item = valid_q.get()
        if item is SENTINAL:
            break
        job: Job = item
        latency = time.perf_counter() - job.created
        try:
            value = compute(job.a, job.b, job.operator)
            result_q.put(Result(job.job_id, job.operator, job.a, job.b, value, True, stage="solver", latency=latency))
        except ZeroDivisionError:
            result_q.put(Result(job.job_id, job.operator, job.a, job.b, None, False, stage="solver", error = "Division by Zero", latency=latency))
        except Exception as exc:
            result_q.put(Result(job.job_id, job.operator, job.a, job.b, None, False, stage="solver", error = f"unexpected error {exc}", latency=latency))
        solved += 1
    log(f"Solver work done, Solved {solved} jobs")
    if shutdownCount.worker_done():
        result_q.put(SENTINAL)

def compute(a: float, b: float, operator: str) -> float:
    if operator == "+":
        return a + b
    elif operator == "*":
        return a * b
    elif operator == "/":
        return a / b
    elif operator == "-":
        return a - b
    elif operator == "%":
        return a % b
    else:
        raise ValueError(f"Unknown Operator {operator}")

def aggregator(result_q: "queue.Queue[Union[Job, object]]", stats: PipelineStats) -> None:
    while True:
        item = result_q.get()
        if item is SENTINAL:
            break
        stats.record(item)
    log("aggregator done")

def runPipeline(numJobs: int = 2000, numWorkers: int = 4, queueMaxSize: int = 256, malformedRate: float = 0.05, seed: Optional[int] = None,) -> PipelineStats:
    rng = random.Random(seed)
    raw_q: "queue.Queue" = queue.Queue(maxsize=queueMaxSize)
    valid_q:  "queue.Queue" = queue.Queue(maxsize=queueMaxSize)
    result_q:  "queue.Queue" = queue.Queue(maxsize=queueMaxSize)

    stats = PipelineStats()
    shutdownCount = WorkerShutdownCounter(numWorkers)

    threads: list[threading.Thread] = []

    threads.append(threading.Thread(target=generator, name="Generator", args=(raw_q, numJobs, malformedRate, rng)))
    threads.append(threading.Thread(target=validator, name="Validator", args=(raw_q, valid_q, result_q, numWorkers)))

    for i in range(numWorkers):
        threads.append(threading.Thread(target=solver, name=f"Solver {i}", args=(valid_q, result_q, shutdownCount)))

    aggreg = threading.Thread(target=aggregator, name="Aggregator", args=(result_q, stats))
    threads.append(aggreg)

    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.perf_counter() - start

    rate = numJobs / elapsed if elapsed else 0
    log(f"TOTAL RUNTIME: {elapsed:.3f}s with {rate:.0f} job/sec")
    return stats

def main():
    print("Running...")
    parser = argparse.ArgumentParser(description="Threaded arithmetic job pipeline")
    parser.add_argument("--num-jobs", type=int, default=2000)
    parser.add_argument("--num-workers", type=int, default=4, help="number of Solver workers threads (K)")
    parser.add_argument("--queue-maxsize", type=int, default=256, help="bounded queue size for backpressure")
    parser.add_argument("--malformed-rate", type=float, default=0.05, help="fraction of jobs that are intentionally invalid")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("-v", "--verbose", action="store_true", help="debug logging (logs every job)")
    args = parser.parse_args()

    if args.verbose:
        global VERBOSE
        VERBOSE = True

    stats = runPipeline(
        numJobs=args.num_jobs,
        numWorkers=args.num_workers,
        queueMaxSize=args.queue_maxsize,
        malformedRate=args.malformed_rate,
        seed=args.seed
        )
    print(stats.report())

if __name__ == "__main__":
    main()
    