
import json
from ldapauthenticator import LDAPAuthenticator

## ldap primary auth configuration

c.LDAPAuthenticator.use_ssl = False
c.LDAPAuthenticator.server_address = \
     os.environ['LDAP_SERVER_ADDRESS']

c.LDAPAuthenticator.valid_username_regex = \
    r"^[a-z][.a-z0-9_-]*@[dD][aA][vV][iI][dD][sS][oO][nN].[eE][dD][uU]$"

c.LDAPAuthenticator.lookup_dn = True
c.LDAPAuthenticator.lookup_dn_search_filter = '({login_attr}={login})'
c.LDAPAuthenticator.lookup_dn_user_dn_attribute = 'cn'
c.LDAPAuthenticator.lookup_dn_search_user = \
     os.environ['LDAP_SERVER_USERDN']
c.LDAPAuthenticator.lookup_dn_search_password = \
     os.environ['LDAP_SERVER_PASSWORD']

c.LDAPAuthenticator.use_lookup_dn_username = True
c.LDAPAuthenticator.user_attribute = \
    os.environ['LDAP_USER_ATTRIBUTE']
c.LDAPAuthenticator.user_search_base = \
    os.environ['LDAP_USER_BASE']

c.LDAPAuthenticator.attributes = \
    json.loads(
        os.environ['LDAP_ATTRIBUTES'])

## determine groups allowed access

c.LDAPAuthenticator.allowed_groups = \
    json.loads(
        os.environ['LDAP_GROUPS_ALLOW'])

# enable encrypted & persistent `auth_state`
c.LDAPAuthenticator.enable_auth_state = True

# select user attibutes provided by ldap to encrypt and store
c.LDAPAuthenticator.auth_state_attributes = \
    c.LDAPAuthenticator.attributes

# set authenticator class
c.JupyterHub.authenticator_class = LDAPAuthenticator
