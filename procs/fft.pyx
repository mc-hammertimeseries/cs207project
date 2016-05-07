import numpy as np
cimport numpy as np
cimport cfft
# from cfft cimport fftw_plan, fftw_execute, fftw_malloc, \
# fftw_destroy_plan, fftw_free, fftw_plan_dft_1d

# cdef extern from "fft_defs.h":
# 	cdef unsigned _FFTW_ESTIMATE

# FFTW_ESTIMATE = _FFTW_ESTIMATE

# cdef fftw_plan _fftw_plan_dft_1d(int N, double_c *in_arr,
# 						double_c *out, int sign,
# 						unsigned flags):
# 	return <void *>fftw_plan_dft_1d(N, in_arr,
# 							out, sign,
# 							flags)

# cdef class FFT:
# 	cdef fftw_plan _p
# 	cdef fftw_complex *_input
# 	cdef fftw_complex *_out
# 	cdef int64_t _N

# 	def __cinit__(self, int N, int sign):
# 		self._N = N
# 		_input = <fftw_complex*>fftw_malloc(sizeof(fftw_complex) * N)
# 		self.input = _input
# 		_out = <fftw_complex*>fftw_malloc(sizeof(fftw_complex) * N)
# 		self.out = _out
# 		_p = _fftw_plan_dft_1d(N, in, out, sign, 
# 			FFTW_ESTIMATE)
# 		self.p = _p

# 	def compute(self, input):
# 		for i in range(self.N):
# 			self._input[i] = input[i]
# 		fftw_execute(self._p)
# 		return self._out

# 	def cleanup(self):
# 		fftw_destroy_plan(self._p)
# 		fftw_free(self._input)
# 		fftw_free(self._output)

# # cdef void fft_complex_1d(int N, double *in, double *out, int sign,
# # 	unsigned flags):
# # 	cdef double[N][2] in_2
# # 	for i in range(N):
# # 		in_2[i][0] = in[i][0]

# # 	cdef fftw_plan p
# # 	in = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * N)
# # 	out = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * N)
# # 	p = fftw_plan_dft_1d(N,
# # 						fftw_complex *in, fftw_complex *out,
# # 						FFTW_ESTIMATE)
# # 	fftw_execute(p)

# # 	try:
# # 		print([i for i in out])
# # 	finally:
# # 		fftw_destroy_plan(p);
# # 		fftw_free(in); fftw_free(out);
	
# # cdef correlation:
# # 	fft(fft(a, -1), 1) * conj(fft(-1))
