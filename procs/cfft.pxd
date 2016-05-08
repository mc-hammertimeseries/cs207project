# Function declarations from fftw.

cdef extern from "fftw3.h":
	ctypedef struct fftw_plan_struct:
		pass

	ctypedef fftw_plan_struct *fftw_plan

	fftw_plan fftw_plan_dft_1d(int N, double_c *input,
								double_c *out, int sign,
								unsigned flags)

	void fftw_execute(fftw_plan p)

	void *fftw_malloc(size_t sizeof)

	void fftw_destroy_plan(fftw_plan p)

	void fftw_free(void *p)
