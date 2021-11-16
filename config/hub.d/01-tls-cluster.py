
# add nodes from the cluster to trusted alt-names
from socket import gethostbyname 

# generate a list of trusted alt-names for possible 
#   places the spawner will launch the instance
nodes=\
        [f'{hub_hostname}']+\
        [f'{hub_hostname.replace(".davidson.edu","")}']+\
        [f'compute{n}' for n in range(0, 8)]+\
        [f'gpu{n}' for n in range(0,2)]+\
        ['jupyterctl0']+\
        ['jupyterdev0']+['computedev0']

c.JupyterHub.trusted_alt_names += \
    [ f'DNS:{host}' for host in nodes ]+\
    [ f'IP:{gethostbyname(host)}' for host in nodes ]+\
    [ f'DNS:*.{hub_hostname}', 
      f'DNS:*.{hub_hostname.replace("davidson.edu","")}']

c.JupyterHub.trusted_alt_names += \
    [f'DNS:api.{hub_id.lower()}.localhost', f'DNS:traefik.{hub_domain}']
