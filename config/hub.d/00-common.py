import sys, pwd, json
from jupyterhub.utils import random_port

# test if `hub_port` has been defined, if not use
#  default value
try:
    x = hub_port
except NameError:
    hub_port = random_port()
    pass

# test if `hub_id` has been defined, if not use
#  default value
try:
    x = hub_id 
except NameError:
    hub_id = os.environ['JUPYYERHUB_ID']
    pass

# test if `hub_domain` has been defined,
#  if not use default value
try:
    x = hub_domain
except NameError:
    hub_domain = os.environ.get('JUPYTERHUB_DOMAIN', 'localhost')
    pass

# test if `hub_hostname` has been defined,
#  if not use default value
try: 
    x = hub_hostname
except NameError:
    # set default derived hostname 
    hub_hostname = os.environ.get('JUPYTERHUB_HOSTNAME', f'{hub_id}.{hub_domain}')
    pass

# ##############################################################################
# Jupyterhub Config File

c.JupyterHub.log_level = os.environ.get('JUPYTERHUB_LOGLEVEL', 'WARN')
c.JupyterHub.log_datefmt = f'{hub_id} '

## base application config
c.JupyterHub.ip = hub_hostname
c.JupyterHub.port = hub_port
service_port = hub_port+1

# the following are required for spawner connect-back
c.JupyterHub.hub_ip = hub_hostname
c.JupyterHub.hub_port = service_port

# increament service_port
service_port += 1

# don't send users to 'Control Panel' by default
c.JupyterHub.redirect_to_server = True 

# do not shutdown single-user servers on exit
c.JupyterHub.cleanup_servers = False 

## spawner related limits 
c.JupyterHub.active_server_limit = 96 # best guess
c.JupyterHub.concurrent_spawn_limit = 50
c.JupyterHub.init_spawners_timeout = 30

## named servers
c.JupyterHub.allow_named_servers = False
c.JupyterHub.named_server_limit_per_user = 1
c.JupyterHub.default_server_name = ''

# allow admins to access all private `user` routes and services
c.JupyterHub.admin_access = True

# until otherwise requested, turn off internal ssl
c.JupyterHub.internal_ssl = False

## templates, database, and torage paths
c.JupyterHub.data_files_path = \
    os.environ['JUPYTERHUB_PATH_DATA']
c.JupyterHub.template_paths = \
    ["templates", os.environ['JUPYTERHUB_PATH_TEMPLATES']]
c.JupyterHub.cookie_secret = bytes.fromhex( 
    os.environ['JUPYTERHUB_COOKIE_SECRET']
)

# NOTE: when the the number of concurrent users is guarentted to be below 30,
#  using sqlite is perfectly acceptable

def make_db_url():
    seg = ''
    scheme = os.environ['JUPYTERHUB_DB_SCHEME']
    username = os.environ.get('JUPYTERHUB_DB_USERNAME')
    password = os.environ.get('JUPYTERHUB_DB_PASSWORD')
    hostname = os.environ.get('JUPYTERHUB_DB_HOST')
    name = os.environ['JUPYTERHUB_DB_NAME']
    if hostname:
        if username and password:
            seg = f'{username}:{password}@{hostname}'
        elif username:
            seg = f'{username}@{hostname}'
        else:
            seg = f'{hostname}'
        pass
    return f'{scheme}://{seg}/{name}' 

c.JupyterHub.db_url = make_db_url()

c.JupyterHub.services = []
c.JupyterHub.extra_handlers = []
c.JupyterHub.trusted_alt_names = []
