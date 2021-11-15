#!/bin/bash 

## environment & conda details
CONDA_PATH="/opt/conda"

# define application environment and 
#   kernel install target environment
OCTAVE_ENV="octave"
OCTAVE_PREFIX="${CONDA_PATH}/envs/${OCTAVE_ENV}"

TARGET_ENV="common"
TARGET_PREFIX="${CONDA_PATH}/envs/${TARGET_ENV}"

## remove existing environment 
mamba env remove -y -n "${OCTAVE_ENV}"

## create bare environment for octave.
mamba create -y -n "${OCTAVE_ENV}"

# install octave package and kernel from `hcc` repo
mamba install -y -n "${OCTAVE_ENV}" -c hcc \
    octave=5.2 \
    octave_kernel

## copy kernel definition to target environment
cp -vr \
    "${OCTAVE_PREFIX}/share/jupyter/kernels/octave" \
    "${TARGET_PREFIX}/share/jupyter/kernels"
    
# update kernel json definition 
tee "${TARGET_PREFIX}/share/jupyter/kernels/octave/kernel.json" <<EOF
{
    "argv": ["/bin/bash", "-c",
                "source ${CONDA_PATH}/bin/activate ${OCTAVE_ENV} && python -m octave_kernel -f {connection_file}"],
    "display_name": "Octave",
    "mimetype": "text/x-octave",
    "language": "octave",
    "name": "octave"
}
EOF