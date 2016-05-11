from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy as np

sourcefiles = ["fft.pyx"]

setup(
	name="fftw wrapper",
    ext_modules=cythonize([Extension("fft", ["fft.pyx"], libraries=["fftw3"],
    	include_dirs=[np.get_include(), '.', "/home/travis/fftw", "/home/travis/fftw/include"],
    	library_dirs=["/home/travis/fftw", "/home/travis/fftw/lib", "/home/travis/fftw/include", "/home/travis/include"])])
    # include_dirs=[np.get_include(), '.']
)
