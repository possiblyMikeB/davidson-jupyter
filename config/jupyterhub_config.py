import os, time, sys, shutil
from etcd3 import client as etcd
from jupyterhub.utils import random_port
from urllib.parse import urlparse

# extract ETCD connection info from env-var
etcd_host, etcd_port = \
    urlparse(os.environ['ETCD_CLIENT_URL']).netloc.split(':')

# connect to configuration key/value store
conf = etcd(
    host=etcd_host, 
    port=int(etcd_port),
    ca_cert=os.environ['ETCD_CLIENT_CA'], 
    cert_cert=os.environ['ETCD_CLIENT_CERT'], 
    cert_key=os.environ['ETCD_CLIENT_KEY']
)

## Base configuration parameter
# hub_id   -- REQUIRED 
# hub_path -- REQUIRED (install prefix)
# hub_port  -- defaults to `random_port()`
# hub_domain -- defaults to `localhost`
# hub_hostname -- defaults to `{hub_id}.localhost`
# hub_path -- install prefix of hub related files

hub_id = os.environ['JUPYTERHUB_ID']
hub_path = os.environ['JUPYTERHUB_PREFIX']

# path.abspath(  # basepath of hub
#     os.path.join(
#         os.path.dirname(
#             shutil.which("jupyterhub")
#         ),
#         '..'
#     )
# )

val, meta = conf.get(f'/jupyterhub/{hub_id}/port')
if not val:
    hub_port = random_port()
    conf.put(f'/jupyterhub/{hub_id}/port', str(hub_port))
else:
    hub_port = int(val)


sections = [
    '00-common.py',
    '00-handler-pages.py',
    '01-tls-internal.py',
    '01-tls-cluster.py',
    '02-service-common.py',
    '02-service-announcements.py',
    '02-service-cull-idle.py',
    '03-proxy-common.py',
    '03-proxy-traefik-etcd.py',
    '04-spawner-common.py',
    '04-spawner-slurm.py',
    '05-auth-common.py',
    '05-auth-ldap.py',
    '05-auth-duo.py'
]

# load sections
for item in sections:
    print(f"Loading {item}", file=sys.stderr)
    with open(f'{hub_path}/etc/jupyterhub/conf.d/{item}', 'r') as confile:
        exec(confile.read())
        pass

# add default admins
c.Authenticator.admin_users = {'miblackmon'}

# health monitoring service  
c.JupyterHub.services += [
    {'name': 'davidson-ric',
     'api_token': os.environ['SERVICE_DAVIDSON_RIC_TOKEN'],
     'admin': True},
]

# internal...
c.JupyterHub.hub_bind_url = f'https://{hub_hostname}:{hub_port+1}'
#c.JupyterHub.hub_connect_url = f'https://{hub_hostname}:9001'

# sleep for a bit to let things settle
time.sleep(1)

