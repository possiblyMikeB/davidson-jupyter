
## environment & conda details
CONDA_PATH="/opt/conda"

# define application environment and 
#   kernel install target environment
R_ENV="r-40"
R_PREFIX="${CONDA_PATH}/envs/${R_ENV}"

TARGET_ENV="common"
TARGET_PREFIX="${CONDA_PATH}/envs/${TARGET_ENV}"

## remove existing environment 
mamba env remove -y -n "${R_ENV}"

## create bare environment for octave.
mamba create -y -n "${R_ENV}"

# install octave package and kernel from `hcc` repo
mamba install -y -n "${R_ENV}" -c conda-forge \
    r=4.0 \
    r-essentials \
    r-irkernel \
    r-rmarkdown \
    r-googlesheets4 

## copy kernel definition to target environment
cp -vr \
    "${R_PREFIX}/share/jupyter/kernels/ir" \
    "${TARGET_PREFIX}/share/jupyter/kernels"
    
# update kernel json definition 
tee "${TARGET_PREFIX}/share/jupyter/kernels/ir/kernel.json" <<EOF
{
    "argv": ["/bin/bash", "-c",
                "source ${CONDA_PATH}/bin/activate ${R_ENV} && R --slave -e 'IRkernel::main()' --args '{connection_file}'"],
    "display_name": "R",
    "language": "R",
    "name": "R"
}
EOF
