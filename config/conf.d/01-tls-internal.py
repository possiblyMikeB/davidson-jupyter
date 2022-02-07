

## end-to-end encryption
c.JupyterHub.generate_certs = False
c.JupyterHub.internal_ssl = True
c.JupyterHub.internal_certs_location = \
    os.environ.get('JUPYTERHUB_PATH_CERTS')

c.JupyterHub.trusted_alt_names = []

