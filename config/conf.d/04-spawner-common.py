import json, os

## base spawner config
try:
    c.Spawner.cmd = \
        json.loads(os.environ['SPAWNER_CMD'])
except KeyError:
    c.Spawner.cmd = [ 
        'jupyterhub-singleuser', # OAuth wrapped jupyter instance server
        '--KernelManager.transport=ipc', # -- all kernel comms over UNIX sockets
        '--MappingKernelManager.cull_idle_timeout=0'  # -- no kernel culling
    ]


c.Spawner.http_timeout = int(os.environ.get('SPAWNER_HTTP_TIMEOUT', '20')) # grace period for spawner connect back
c.Spawner.default_url = os.environ.get('SPAWNER_DEFAULT_URL', '/lab')  # default route to visit once spawned

# set jupyter instacne base directory (relative to $HOME)
if hub_id.lower() in {'jupyter', 'public', 'pub'}:
    c.Spawner.notebook_dir = ''
else:
    # restrict to context specific notebook path
    c.Spawner.notebook_dir = f'Workspace/{hub_id}'
    pass

