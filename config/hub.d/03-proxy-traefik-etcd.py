
from jupyterhub.proxy import Proxy
from jupyterhub_traefik_proxy import TraefikEtcdProxy
from jupyterhub.utils import maybe_future
from traitlets import Any, default, Unicode

class SiteTraefikProxy(TraefikEtcdProxy):
    @default("kv_traefik_prefix")
    def _default_kv_traefik_prefix(self):
        return "/traefik"

    @default("kv_jupyterhub_prefix")
    def _default_kv_jupyterhub_prefix(self):
        return f"/jupyterhub/{hub_id}/proxy/routes"

    
    async def start(self):
        """Initialize Hub specific dynamic configuration.
            NOTE: We are assuming that Traefik is already running as an external service
            and this routine is being used to arrange client certificates which will be 
            used to connect to backend server instances.
        """
        # list holding all the kv transactions we are going to build
        actions = []
        
        # useful definitions
        desig = self.traefik_default_desig
        pref = f'{self.kv_traefik_prefix}'+'http' 
        route_prefix = f'{pref}/routers/{desig}'
        serve_prefix = f'{pref}/services/{desig}'
        trans_prefix = f'{pref}/serverstransports/{desig}'

        # entries defining connect-back route&service
        entries = {
            f'{serve_prefix}/loadbalancer/servers/0/url': self.app.hub_bind_url,
            f'{route_prefix}/entrypoints/0': 'trusted',
            f'{route_prefix}/service': desig,
            f'{route_prefix}/rule': f'Host(`{hub_hostname}`) && PathPrefix(`/hub/api`)',
            f'{route_prefix}/tls': ''
        }
        
        # push assigning them to our list of operations to perform
        actions += [
            self.kv_client.transactions.put(k, v)
            for k,v in entries.items()
        ]

        # check to see if we have internal ssl/tls on
        if self.app.internal_ssl:
            # if so, define appropriate serversTransport specification
            client_cert_id = 'proxy-client'
            #api_cert_id = 'proxy-api'

            # read in the cert, key, and ca-bundle.
            keyfile = self.app.internal_proxy_certs[client_cert_id]['keyfile']
            certfile = self.app.internal_proxy_certs[client_cert_id]['certfile']
            cafile = self.app.internal_trust_bundles[f'{client_cert_id}-ca']

            key = open(keyfile, 'r').read()
            cert = open(certfile, 'r').read()
            ca = open(cafile, 'r').read()

            # attach them to a serversTransports specification 
            #  used by any routes we add (also point)
            
            entries = {
                # add serversTransports entry 
                f'{trans_prefix}/servername': hub_hostname,
                f'{trans_prefix}/rootcas/0': ca,
                f'{trans_prefix}/certificates/0/certfile': cert,
                f'{trans_prefix}/certificates/0/keyfile': key,

                # update service def to use serverstransport
                f'{serve_prefix}/loadbalancer/serverstransport': desig
            }

            # push assigning actions to list of transaction to perform
            actions = [
                self.kv_client.transactions.put(k, v) 
                for k,v in entries.items() 
            ]+actions
            pass

        # execute actions in one operation
        stat, res = await maybe_future(self._etcd_transaction(actions))
        pass

    async def stop(self):
        """Tear down Hub specific dynamci configuration."""
        if self.app.internal_ssl:
            # Remove the serversTransports entry 
            pass

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


