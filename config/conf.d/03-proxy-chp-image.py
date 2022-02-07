
from jupyterhub.proxy import ConfigurableHTTPProxy

## HTTP Route Proxy (container) #########################################

# get the port of the entryPoint for Traefik we've setup 
#   to route internal communications
trusted_port = \
    os.environ.get('PROXY_TRUSTED_PORT') 

# expect the proxy will be running when we start
#  and that we have the right auth-token
c.ConfigurableHTTPProxy.should_start = False
c.ConfigurableHTTPProxy.auth_token = \
    os.environ.get('CONFIGPROXY_AUTH_TOKEN')

# we have setup Traefik to use hosted based routing, 
#  over a `trusted` port
c.ConfigurableHTTPProxy.api_url = \
    f'http://api.{hub_id.lower()}.localhost:{trusted_port}'

# set proxy class
c.JupyterHub.proxy_class = ConfigurableHTTPProxy

# no new managed service, so don't increment `service_port`
service_port += 0
