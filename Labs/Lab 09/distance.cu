%%writefile distance.cu

#include <stdio.h>

#include <math.h>

#include <cuda_runtime.h>

#define N 10000000

// CPU version

void distance_cpu(float *x, float *y, float *d) {

 for(int i=0;i<N;i++) {

 d[i] = sqrtf(x[i]*x[i] + y[i]*y[i]);

 }

}

// CUDA kernel

__global__ void distance_gpu(float *x, float *y, float *d) {

 int i = blockIdx.x * blockDim.x + threadIdx.x;

 if(i < N) {

 d[i] = sqrtf(x[i]*x[i] + y[i]*y[i]);

 }

}

int main() {

 float *x, *y, *d_cpu, *d_gpu;

 float *dx, *dy, *dd;

 size_t size = N * sizeof(float);

 x = (float*)malloc(size);

 y = (float*)malloc(size);

 d_cpu = (float*)malloc(size);

 d_gpu = (float*)malloc(size);

 // initialize data

 for(int i=0;i<N;i++){

 x[i] = i * 0.001f;

 y[i] = i * 0.002f;

 }

 // CPU timing

 clock_t start = clock();

 distance_cpu(x,y,d_cpu);

 clock_t end = clock();

 printf("CPU time: %f seconds\n",

 (double)(end-start)/CLOCKS_PER_SEC);

 // allocate GPU memory

 cudaMalloc(&dx,size);

 cudaMalloc(&dy,size);

 cudaMalloc(&dd,size);

 cudaMemcpy(dx,x,size,cudaMemcpyHostToDevice);

 cudaMemcpy(dy,y,size,cudaMemcpyHostToDevice);

 // GPU timing

 start = clock();

 int threads = 256;

 int blocks = (N + threads - 1)/threads;

 distance_gpu<<<blocks,threads>>>(dx,dy,dd);

 cudaDeviceSynchronize();

 end = clock();

 printf("GPU time: %f seconds\n",

 (double)(end-start)/CLOCKS_PER_SEC);

 cudaMemcpy(d_gpu,dd,size,cudaMemcpyDeviceToHost);

 printf("Example result: %f\n", d_gpu[100]);

 cudaFree(dx);

 cudaFree(dy);

 cudaFree(dd);

 free(x);

 free(y);

 free(d_cpu);

 free(d_gpu);

 return 0;

}