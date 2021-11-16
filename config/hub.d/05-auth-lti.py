## Authentication ##############################################################

from ltiauthenticator import LTIAuthenticator

## setup LTI Authentication

# determine all LTI (key, secret) authentication pairs
#  and add thn as `consumers`
ii=0
c.LTIAuthenticator.consumers = dict()
while True:
    try:
        key = os.environ[f'LTI_CLIENT_KEY{ii}']
        secret = os.environ[f'LTI_CLIENT_SECRET{ii}']

        if key in c.LTIAuthenticator.consumers:
            msg=f'LTI key collision at {ii}: Keys must be distinct'
            raise Exception(msg)

        c.LTIAuthenticator.consumers[key]=secret
        ii+=1
    except KeyError: 
        # leave the loop after first missing varible 
        #  all other exceptions get elevated
        break

# set authenticator class
c.JupyterHub.authenticator_class = LTIAuthenticator
