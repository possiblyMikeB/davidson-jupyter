
from jupyterhub.auth import PAMAuthenticator

# basic PAM authentication setup
c.PAMAuthenticator.service = 'jupyter-hub'

# access controls
c.PAMAuthenticator.whitelist = set()
c.PAMAuthenticator.group_whitelist = {
    'rhel admins@davidson.edu',
    'jupyter_access@davidson.edu'
}
 
# admin rights
c.PAMAuthenticator.admin_groups = {
    'rhel admins@davidson.edu',
    'hub-admin'
}

# the following will be written to /etc/pam.d/jupyter-hub
PAM_SERVICE="""
# Note: This file is based on the file "/etc/pam.d/login"
#   shipped with CentOS 8.

auth       substack     password-auth
auth       include      postlogin

account    required     pam_nologin.so
account    include      password-auth
password   include      password-auth

# pam_selinux.so close should be the first session rule
session    required     pam_selinux.so close

# pam_selinux.so open should only be followed by sessions to be executed in the user context
session    required     pam_selinux.so open
session    required     pam_namespace.so
session    optional     pam_keyinit.so force revoke
session    include      password-auth
session    include      postlogin

-session   optional     pam_ck_connector.so
"""

# create pam service using `PAM_SERVICE`
with open(f'/etc/pam.d/{c.PAMAuthenticator.service}', 'w') as servfil:
    print(PAM_SERVICE, file=servfil, flush=True)
    pass

# set authneticator class
c.JupyterHub.authenticator_class = PAMAuthenticator
