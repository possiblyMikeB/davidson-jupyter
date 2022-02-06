# attach Duo 2FA to an already
#    selected authenticator class

# pull in encoding shim for our Duo modification
from davidson.hub.authenticator import EncodeAuthenticatorShim
from duoauthenticator import DuoAuthenticator

# setup Duo two-factor secondary auth        
c.DuoAuthenticator.ikey = os.environ.get('DUO_IKEY') 
c.DuoAuthenticator.skey = os.environ.get('DUO_SKEY')
c.DuoAuthenticator.akey = os.environ.get('DUO_AKEY')
c.DuoAuthenticator.apihost = os.environ.get('DUO_API_HOST')
c.DuoAuthenticator.primary_auth_class = type('EncodeAuthenticator', (object, c.JupyterHub.authenticator_class, EncodeAuthenticatorShim), {})

# set authenticator class
c.JupyterHub.authenticator_class = DuoAuthenticator
