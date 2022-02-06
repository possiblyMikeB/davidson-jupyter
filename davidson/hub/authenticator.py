# prepare for Duo
from base64 import standard_b64encode as base64encode
from jupyterhub import orm
from jupyterhub.user import User
from jupyterhub.metrics import TOTAL_USERS

# simple encoding shim to allow `auth_state` use with Duo
class EncodeAuthenticatorShim:
    """
     `EncodeAuthenticator` is a shim allowing for complex data to be
         passed through the Duo process
    """
    async def authenticate(self, handler, data):

        # attempt to authenticate the user
        auth = await super().authenticate(handler, data)
        if auth is None:
            return auth
        ## IF user authentication was successful, ensure account
        #    exists and auth_state is appropriately populated

        # convert simple `auth` return to appropriate dict() 
        if isinstance(auth, str):
            auth = {'name': auth}

        # decompose `auth` dict(), create account, if missing, and store auth_state, if found
        username = auth['name']
        groupname = f'access-{username}'
        admin = auth.get('admin')
        
        # serach for associated account, create if missing
        user = orm.User.find(self.db, name=username)
        if user is None:
            user = orm.User(name=username)
            self.db.add(user)
            TOTAL_USERS.inc()
            self.db.commit()
            pass

        # serach for primary access group, create if missing
        group = orm.Group.find(self.db, name=groupname)
        if group is None:
            group = orm.Group(name=groupname)
            group.users.append(user)
            self.db.add(group)
            self.db.commit()
            pass
        
        # handle administrative rights 
        if admin is not None and user.admin != admin:
            user.admin = admin
            self.db.commit()
            pass

        auth_state = None
        if self.enable_auth_state:
            # base64 encode, `pop`, or make "", any problematic values
            auth_state = dict()
            for k,v in auth.get('auth_state', {}).items():
                if isinstance(v, list) and len(v) > 0: 
                    v = v[0]
                else:
                    v = v or ''

                if isinstance(v, bytes):
                    auth_state[k] = base64encode(v).decode('utf-8')
                else:
                    auth_state[k] = v
                pass
            auth['auth_state'].update(auth_state)
            pass
        return auth
    pass
