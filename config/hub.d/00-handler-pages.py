import jupyterhub.handlers as h

# pull in site specific request handlers
from davidson.hub.handlers import SiteAdminHandler, SiteHomeHandler

# configure use of site handlers
h.default_handlers =[(r'/home', SiteHomeHandler),
                    (r'/admin', SiteAdminHandler)]+h.default_handlers
