import numpy as np
cimport numpy as np
cimport cfft
from cfft cimport fftw_plan, fftw_execute, fftw_malloc, \
fftw_destroy_plan, fftw_free, fftw_plan_dft_1d

# External declarations and definitions of fftw functions
cdef extern from "fft_defs.h":
	cdef unsigned _FFTW_ESTIMATE

FFTW_ESTIMATE = _FFTW_ESTIMATE

cdef fftw_plan _fftw_plan_dft_1d(int N, double_c *in_arr,
						double_c *out, int sign,
						unsigned flags):
	return <void *>fftw_plan_dft_1d(N, in_arr,
							out, sign,
							flags)

cdef class FFT:
	"""
	Class implementing forwards and backwards Fourier transform from fftw. First,
	an instance of the class must be initialized. Then the FFT or IFFT can be
	computed using compute. After the result is obtained, cleanup must be
	called to free memory.
	"""

	cdef fftw_plan _p
	cdef fftw_complex *_input
	cdef fftw_complex *_out
	cdef int64_t _N

	def __cinit__(self, int N, int sign):
		"""
		N is the length of the input array. The output will have length
		(N / 2) + 1. Sign is the sign of the exponent in the transform.
		A sign of -1 is the forward transform, and 1 is the backward.
		"""

		self._N = N
		self._input = <fftw_complex*>fftw_malloc(sizeof(fftw_complex) * N)
		self._out = <fftw_complex*>fftw_malloc(sizeof(fftw_complex) * N)
		self._p = _fftw_plan_dft_1d(N, in, out, sign, 
			FFTW_ESTIMATE)

	def compute(self, input):
		"""
		Compute the FFT or IFFT of the given input.
		"""
		# Should raise exception if len(input) != N
		for i in range(self.N):
			self._input[i] = input[i]
		fftw_execute(self._p)
		return self._out

	def cleanup(self):
		"""
		Clean up memory used by fftw. Must be called at some point!
		"""

		fftw_destroy_plan(self._p)
		fftw_free(self._input)
		fftw_free(self._output)
