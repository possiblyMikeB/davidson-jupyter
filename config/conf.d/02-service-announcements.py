## IMPORTANT: Must be loaded after `02-service-common.py

## announcement service

service_env = dict()
service_url = f'{hub_hostname}:{service_port}'

if c.JupyterHub.internal_ssl:
    # if we are using end-to-end mTLS, then pass 
    #   certs to service and set scheme to `https`

    # TODO: Generate certs automatically
    PKI_STORE=c.JupyterHub.internal_certs_location
    service_env = {
        'JUPYTERHUB_SSL_CERTFILE':
            f'{PKI_STORE}/hub-internal/hub-internal.crt',
        'JUPYTERHUB_SSL_KEYFILE':
            f'{PKI_STORE}/hub-internal/hub-internal.key',
        'JUPYTERHUB_SSL_CLIENT_CA':
            f'{PKI_STORE}/hub-ca_trust.crt',
    }
    service_url = f'https://{service_url}'

else:
    # if not, set schema to `http`
    service_url = f'http://{service_url}'
    pass

# NOTE: you must generate certs for services
c.JupyterHub.services += [
    { # Hub-wide announcments service
        'name': 'announcement',
        'url': service_url,
        'command': [
            sys.executable, '-m', 'jupyterhub_announcement',
            f'--AnnouncementService.fixed_message="Welcome to the {hub_id} JupyterHub server!"',
            f'--AnnouncementService.port={service_port}',
            f'--AnnouncementQueue.persist_path=announcements.json',
            f'--AnnouncementService.template_paths=["{hub_path}/share/jupyterhub/templates","{hub_path}/templates"]'
        ],
        'environment': service_env
    }
]

# increment service port
service_port += 1
