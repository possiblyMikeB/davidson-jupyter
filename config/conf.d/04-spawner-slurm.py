
import os, sys, pwd, socket, shutil, asyncio
from traitlets import (
    Integer, Unicode, Float, Dict, default 
)

# pull in Site spawner class
from davidson.hub.spawner import SiteSlurmSpawner

# ######################################
# IMPORTANT!!
#  The environment variable SLURM_PATH, must be set in order
#  for spawning and monitoring of server-instances to function

slurm_prefix = os.environ['SLURM_PATH'] # (this will fail if not set)

# ##########################

c.SiteSlurmSpawner.batchspawner_singleuser_cmd = '' # (using custom shim)
c.SiteSlurmSpawner.exec_prefix='' # (was 'sudo -E -u {username} ')

# avoid additional call to `sudo`
c.SiteSlurmSpawner.\
    batch_query_cmd = f"{slurm_prefix}/bin/squeue" + " -u {username} -h -j {job_id} -o '%T %B'"

# TOOD: investigate the need for `sudo` on the 
#  sbatch & scancel calls
c.SiteSlurmSpawner.\
    batch_cancel_cmd = "sudo -E -u {username} " + f"{slurm_prefix}/bin/scancel" + " {job_id}"

c.SiteSlurmSpawner.\
    batch_submit_cmd = "sudo -E -u {username} " + f"{slurm_prefix}/bin/sbatch" + " --parsable"

## import & store job-script template 
job_template = os.environ.get('SPAWNER_SLURM_SCRIPT')
if os.path.exists(job_template):
    c.SiteSlurmSpawner.batch_script = open(job_template, 'r').read()
else:
    c.SiteSlurmSpawner = job_template

## used to communicate the hub-id to the running job.
c.SiteSlurmSpawner.req_profile = hub_id

## check for job parameters
arg_names = [
    'partition', 'account', 'cluster', 'qos', 'reservation',
    'nprocs', 'ntasks', 'memory', 'gres', 
    'runtime', 'workspace'
]

for name in arg_names:
    try: 
        # check to see if we've been passed something in
        #  the environment.
        val = os.environ[f'SPAWNER_SLURM_JOB_{name.upper()}']
        if val and hasattr(SiteSlurmSpawner, f'req_{name}'):
            # if so and we have a place to hold it, 
            #   then, store the value.
            setattr(c.SiteSlurmSpawner, f'req_{name}', val)
            pass
    except KeyError:
        continue


## job-step specific parameters
c.SiteSlurmSpawner.req_srun = 'srun -n1'

for name in ['epilog', 'prolog' ]:
    path = os.environ.get(f'SPAWNER_SLURM_TASK_{name.upper()}')
    if path:
        c.SiteSlurmSpawner.req_srun += f' --task-{name} {path}'
        pass

c.SiteSlurmSpawner.req_options = '--ntasks=1 ' + os.environ.get('SPAWNER_SLURM_JOB_EXTRA', '')

## conda environment parameters
c.SiteSlurmSpawner.req_conda_env = os.environ.get('SPAWNER_SLURM_CONDA_ENV')
c.SiteSlurmSpawner.req_conda_path = os.environ.get('SPAWNER_SLURM_CONDA_PATH')

# set spawner class
c.JupyterHub.spawner_class = SiteSlurmSpawner
