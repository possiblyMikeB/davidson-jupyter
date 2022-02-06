
from jupyterhub.proxy import Proxy
from jupyterhub_traefik_proxy import TraefikEtcdProxy
from jupyterhub.utils import maybe_future
from traitlets import Any, default, Unicode

# pull in site proxy implementation
from davidson.hub.proxy import SiteTraefikProxy

c.SiteTraefikProxy.hub_id = hub_id
c.SiteTraefikProxy.hub_hostname = hub_hostname
c.SiteTraefikProxy.should_start = True

# configure traefik using etcd backend
c.SiteTraefikProxy.traefik_default_host = f'{hub_hostname}'
c.SiteTraefikProxy.traefik_default_desig = f'{hub_id}'
c.SiteTraefikProxy.traefik_api_url = os.environ['PROXY_API_URL']  
c.SiteTraefikProxy.traefik_api_username = os.environ.get('PROXY_USERNAME')
c.SiteTraefikProxy.traefik_api_password = os.environ.get('PROXY_PASSWORD')
c.SiteTraefikProxy.traefik_api_validate_cert = False

## key/value store config
# defined in /etc/traefik/traefik.yml
c.SiteTraefikProxy.kv_traefik_prefix = os.environ.get('PROXY_PREFIX')

# SEE: `NOTES.config.md` for reasoning behind this next prefix
c.SiteTraefikProxy.kv_jupyterhub_prefix = f'/jupyterhub/{hub_id}/proxy/routes'

# client connection url
c.SiteTraefikProxy.kv_url = os.environ['ETCD_CLIENT_URL']

# mTLS credentials for etcd k/v store
c.SiteTraefikProxy.etcd_client_ca_cert = os.environ['ETCD_CLIENT_CA']
c.SiteTraefikProxy.etcd_client_cert_crt = os.environ['ETCD_CLIENT_CERT']
c.SiteTraefikProxy.etcd_client_cert_key = os.environ['ETCD_CLIENT_KEY']

# set proxy class
c.JupyterHub.proxy_class = SiteTraefikProxy # TraefikEtcdProxy


