from collections import deque
from position import Position

class Pathfinder:
    @staticmethod
    def next_step(start, target, cols, rows, obstacles):
        if start == target:
            return start
        
        blocked = set(obstacles)
        blocked.discard(start.as_tuple())
        blocked.discard(target.as_tuple())

        visited = {start.as_tuple(): None}
        queue = deque([start])

        while queue:
            current = queue.popleft()
            if current == target:
                break
            for neighbor in current.neighbors(cols, rows):
                key = neighbor.as_tuple()
                if key in visited or key in blocked:
                    continue
                visited[key] = current
                queue.append(neighbor)

        if target.as_tuple() not in visited:
            return start
        
        path = []
        node = target
        while node != start:
            path.append(node)
            node = visited[node.as_tuple()]
        path.reverse()
        return path[0]