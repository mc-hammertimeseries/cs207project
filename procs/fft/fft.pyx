import numpy as np
cimport numpy as np
np.import_array()
cimport cfft
from cfft cimport fftw_plan, fftw_execute, fftw_cleanup, \
fftw_destroy_plan, fftw_plan_dft_1d, fftw_complex

# External declarations and definitions of fftw functions.
cdef extern from "fft_defs.h":
	# Flag that initializes FFT faster at the expense of runtime.
	cdef unsigned FFTW_ESTIMATE

	# These determine whether the FFT is forward or backward/inverse.
	cdef int FFTW_FORWARD
	cdef int FFTW_BACKWARD

cdef fft(int N, complex *in_arr, complex *out_arr, int sign):
	"""
	Executes the FFT on the given input and output arrays.
	Sign is the sign of the exponent in the FFT.
	-1 -> forward, +1 -> backward/inverse.
	"""
	p = fftw_plan_dft_1d(N, in_arr, out_arr, sign, FFTW_ESTIMATE)
	fftw_execute(p)
	fftw_destroy_plan(p)

def fft_ccor(np.ndarray[complex, ndim=1, mode='c'] ts_1,
	np.ndarray[complex, ndim=1, mode='c'] ts_2,
	np.ndarray[complex, ndim=1, mode='c'] out_arr):
	"""
	Computes the cross-correlation of the given timeseries.
	At the end of execution, out_arr contains the cross-correlation.
	Does not modify ts_1 or ts_2.

	Note: compared to numpy.fft, the cross-correlation is given
	in the order [0, N-1, N-2, ..., 1]. The calling function
	should deal with this appropriately.

	Parameters
	----------
	ts_1, ts_2 : numpy arrays
		1-D numpy arrays of complex type.
	out_arr : numpy array
		1-D numpy array of complex type. Overwritten with the final result.
	"""

	# Length of time series.
	N = ts_1.shape[0]

	# Take FFT of first times eries.
	fft(N, &ts_1[0], &out_arr[0], FFTW_BACKWARD)
	cdef np.ndarray[complex, ndim=1, mode='c'] ts_1_fft = out_arr.copy()

	# Take FFT of second time series.
	fft(N, &ts_2[0], &out_arr[0], FFTW_BACKWARD)
	cdef np.ndarray[complex, ndim=1, mode='c'] ts_2_fft = out_arr.copy()
	
	# Take IFFT. Note that ordering is different, so we do
	# conj(fft(ts_1)) * fft(ts_2) instead of the other way around.
	ts_2_fft *= np.conj(ts_1_fft)
	fft(N, &ts_2_fft[0], &out_arr[0], FFTW_FORWARD)

	# Normalize the FFT.
	out_arr /= N

	# Clean up any memory used by fftw	
	fftw_cleanup()
