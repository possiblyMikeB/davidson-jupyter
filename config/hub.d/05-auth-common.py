
## common auth parameters

# enable encrypted persistent user authentication information
c.Authenticator.enable_auth_state = True

# blacklist local admins 
c.Authenticator.blacklist = {'admin', 'root'}

# don't delete extranious users
c.Authenticator.delete_invalid_users = False

