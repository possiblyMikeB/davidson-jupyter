import os

## turn on/off collaborative editing
c.LabApp.collaborative = False


import os

## setup resource monitor
#  (if SLURM environment variables defined)

# memory
if 'SLURM_MEM_PER_NODE' in os.environ:
    c.ResourceUseDisplay.mem_limit = int(os.environ['SLURM_MEM_PER_NODE'])
    c.ResourceUseDisplay.mem_limit *= 1024*1024 # rescale to bytes
    pass

# cpu
if 'SLURM_CPUS_PER_TASK' in os.environ:
    c.ResourceUseDisplay.track_cpu_percent = True
    # c.ResourceUseDisplay.cpu_limit = float(os.environ['SLURM_CPUS_PER_TASK'])
    pass

