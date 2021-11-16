
## idle culling services

service_env = dict()
if c.JupyterHub.internal_ssl:
    # if we are using end-to-end mTLS, then pass 
    #   certs to service and set scheme to `https`

    # TODO: Generate certs automatically
    pass

# NOTE: you must generate certs for services
c.JupyterHub.services += [
    { # Idle Server culling service
        'name': 'cull-idle',
        'admin': True,
        'command': [
            ## the `jupyterhub-idle-culler` package installs the 
            # similarly named executable in the environment  
            sys.executable, '-m',
            'jupyterhub_idle_culler',
            '--cull-every=120',
            '--timeout=5400',
            '--concurrency=4',
            f'--internal-certs-location={c.JupyterHub.internal_certs_location}',
            f'--ssl-enabled={c.JupyterHub.internal_ssl}'
        ],
        'environment': service_env
    }
]

# this service doesn't bind to a port
#  so no change to service_port
service_port += 0
