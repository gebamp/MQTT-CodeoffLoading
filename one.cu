 #include <stdio.h>
 #define N 10000000
 #define numThread 2 
 #define numBlock 200  

 __global__ void add( int *a, int *b, int *c ) {
 
     int tid = blockDim.x * blockIdx.x + threadIdx.x;
     while (tid < N) {
         c[tid] = a[tid] + b[tid];      
         tid += blockDim.x;       
                                  
     }
 }
 
 
 int main( void ) {
     int *a, *b, *c;               // The arrays on the host CPU machine
     int *dev_a, *dev_b, *dev_c;   // The arrays for the GPU device
 
     a = (int*)malloc( N * sizeof(int) );
     b = (int*)malloc( N * sizeof(int) );
     c = (int*)malloc( N * sizeof(int) );
 
     for (int i=0; i<N; i++) {
         a[i] = i;
         b[i] = i;
     }
 
      cudaMalloc( (void**)&dev_a, N * sizeof(int) );
      cudaMalloc( (void**)&dev_b, N * sizeof(int) );
      cudaMalloc( (void**)&dev_c, N * sizeof(int) );
      cudaMemcpy( dev_a, a, N * sizeof(int),
                               cudaMemcpyHostToDevice );
      cudaMemcpy( dev_b, b, N * sizeof(int),
                               cudaMemcpyHostToDevice );
     add<<<numBlock,numThread>>>( dev_a, dev_b, dev_c );
     cudaMemcpy( c, dev_c, N * sizeof(int),
                               cudaMemcpyDeviceToHost );
     bool success = true;
     int total=0;
     printf("Checking %d values in the array.\n", N);
     for (int i=0; i<N; i++) {
         if ((a[i] + b[i]) != c[i]) {
             printf( "Error:  %d + %d != %d\n", a[i], b[i], c[i] );
             success = false;
         }
         total += 1;
     }
     if (success)  printf( "We did it, %d values correct!\n", total );
     free( a );
     free( b );
     free( c );
      cudaFree( dev_a );
      cudaFree( dev_b );
      cudaFree( dev_c );
     return 0;
 }
