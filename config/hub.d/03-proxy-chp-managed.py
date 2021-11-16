
from jupyterhub.proxy import ConfigurableHTTPProxy

## HTTP Route Proxy ############################################################

# for mini-hub's the controller can manage the route proxy  
c.ConfigurableHTTPProxy.should_start = True
c.ConfigurableHTTPProxy.pid_file = 'proxy.pid'
c.ConfigurableHTTPProxy.api_url = f'http://localhost:{service_port}'
c.ConfigurableHTTPProxy.command = ['configurable-http-proxy']
c.ConfigurableHTTPProxy.auth_token = \
    os.environ.get('CONFIGPROXY_AUTH_TOKEN')

# set proxy class
c.JupyterHub.proxy_class = ConfigurableHTTPProxy

# increment service_port
service_port += 1
