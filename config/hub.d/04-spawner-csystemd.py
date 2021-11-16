from csystemdspawner import CSystemdSpawner
from random import choice
from socket import gethostbyname

#c.CSystemdSpawner.controller = 'jupyterctl0'

# used to distribute the notebooks
#   onto the nodes
def select_node(s):
    nodes = [
        'w21045.davidson.edu'
    ]
    
    s.host = choice(nodes)
    s.ip = gethostbyname(s.host)
    return

# selects host before spawn
c.CSystemdSpawner.pre_spawn_hook = select_node
    
# XXX: value is set in `pre_spawn_hook`
# c.CSystemdSpawner.host = 

# main resource container/slice
#c.CSystemdSpawner.slice = ''

# unit-name for transient service
c.CSystemdSpawner.unit_name_template = 'notebook-{USERNAME_HASH}{NAME_HASH}'
c.CSystemdSpawner.cmd = [ # command used to spawn server
    '/opt/shared/bin/python3',
          '-m', 'jupyterhub.singleuser' ]

# env config
c.CSystemdSpawner.default_shell = '/bin/bash'
c.CSystemdSpawner.environment = {
    'PATH': '/opt/shared/bin:/bin:/bin:/usr/bin:/sbin:/usr/sbin',
    'PYTHONUNBUFFERED': '1'
}

# user-service config
c.CSystemdSpawner.user_workingdir   = '/home/DAVIDSON/{USERNAME}/'
c.CSystemdSpawner.username_template = '{USERNAME}@davidson.edu'
# (NOTE: using a specific systemd-slice allows us to limit ram+swap usage
#   see github.com/jupyterhub/systemdspawner/issues/15#issuecomment-327947945
#   however, this only works for >= RHEL/Cent 8.0)

c.CSystemdSpawner.mem_limit = '1G'
c.CSystemdSpawner.cpu_limit = 0.5

c.CSystemdSpawner.isolate_devices   = False
c.CSystemdSpawner.isolate_tmp       = False
c.CSystemdSpawner.disable_user_sudo = False
c.CSystemdSpawner.unit_extra_properties = {
    'MemoryAccounting'  : 'true',
    'CPUAccounting'     : 'true',
    'MemoryMax'         : '1G',
    'MemorySwapMax'     : '1G',
    'CPUQuota'          : '50%'
#   'CPUQuotaPeriodSec' : '500'
}
