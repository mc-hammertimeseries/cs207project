from distutils.core import setup, Extension
# from Cython.Build import cythonize
import numpy

sourcefiles = ["fft.pyx"]

setup(
    ext_modules=[
        Extension("fft", sourcefiles,
                  include_dirs=[numpy.get_include()]),
    ],
)

# Or, if you use cythonize() to make the ext_modules list,
# include_dirs can be passed to setup()

# setup(
# 	name="fftw wrapper",
#     ext_modules=cythonize("fft.pyx"),
#     include_dirs=[numpy.get_include()]
# )
