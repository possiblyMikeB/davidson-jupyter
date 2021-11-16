
from socket import gethostbyname

# add nodes from Watson-132 to 'trusted_alt_names'
nodes += [ f'w210{n}' for n in range(30,48) ]

c.JupyterHub.trusted_alt_names +=  \
    [ f'DNS:{name}' for name in nodes ]+\
    [ f'IP:{gethostbyname(name)}' for name in nodes ]+\
    [ f'DNS:{name}.davidson.edu' for name in nodes ] 
