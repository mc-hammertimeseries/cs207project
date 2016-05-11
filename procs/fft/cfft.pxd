# Function declarations from fftw.

# from libc.stddef cimport size_t

cdef extern from "fftw3.h":
	ctypedef struct fftw_plan_struct:
		pass

	ctypedef fftw_plan_struct *fftw_plan

	ctypedef double *fftw_complex

	fftw_plan fftw_plan_dft_1d(int N, complex *in_arr,
								complex *out_arr, int sign,
								unsigned flags) nogil

	void fftw_execute(fftw_plan)

	void fftw_destroy_plan(fftw_plan)

	void fftw_cleanup()
