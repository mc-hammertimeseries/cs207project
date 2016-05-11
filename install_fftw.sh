#!/bin/sh
set -ex
wget http://www.fftw.org/fftw-3.3.4.tar.gz
tar -xzvf fftw-3.3.4.tar.gz
cd fftw-3.3.4 && ./configure --enable-shared --prefix=$HOME/fftw && make && make install