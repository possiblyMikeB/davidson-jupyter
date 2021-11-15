#!/bin/bash
set -e
###########################################################
#
# Name: `setup-env.sh`
# Synop: 
#    initialize minimal conda environment used as
#   a base for profile's runtime environment
# 
####

## environment & conda details
CONDA_ENV="py-37-test"
CONDA_PATH="/opt/conda"

## enable conda 
module load conda

## remove any existing env
conda env remove -y -n "${CONDA_ENV}"

## create blank env 
#   and setup required conda packages 
conda create -y -n "${CONDA_ENV}"

# install additional binary packages
conda install -y -n "${CONDA_ENV}" -c conda-forge \
      python=3.7 \
      pip \
      nodejs=12 \
      cudatoolkit=11 \
      cudnn=8
    
# install gurobi packages
conda install -y -n "${CONDA_ENV}" -c gurobi \
    gurobi=9.1

# activate environment and
#  modify the python environment using `pip`
source ${CONDA_PATH}/bin/activate "${CONDA_ENV}"

# install packages
python3 -m pip install --no-cache-dir --compile \
    numpy \
    scipy \
    sympy \
    pandas \
    matplotlib \
    ipywidgets \
    ipyparallel \
    dask \
    dask-jobqueue \
    scikit-learn \
    tensorflow-gpu==2.4

