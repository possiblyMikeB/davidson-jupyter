
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor

from traitlets import Any, default, Unicode
from traitlets.config import LoggingConfigurable, Application

from jupyterhub.utils import maybe_future

from urllib.parse import urlparse
import os, sys, json, re
import etcd3
import pathlib

# debuging
from pprint import pprint as print

# local imports
from . import params
from . import utils

# https://github.com/ipython/traitlets/blob/2bb2597224ca5ae485761781b11c06141770f110/traitlets/config/application.py#L274


class ETCDClient(LoggingConfigurable):
    """
        Principal interface to kv store
    """

    # concurrent executor
    executor = Any()

    @default("executor")
    def _default_executor(self):
        return ThreadPoolExecutor(1)

    # client configuration options
    client = Any()
    auth_ca = Unicode(
        config=True,
        allow_none=True,
        default_value=os.environ.get(
            'ETCD_CLIENT_CA',
            os.environ.get(
                'ETCDCTL_CACERT',
                None
            )
        ),
        help="""Etcd client root certificates""",
    )
    auth_cert = Unicode(
        config=True,
        allow_none=True,
        default_value=os.environ.get(
            'ETCD_CLIENT_CERT',
            os.environ.get(
                'ETCDCTL_CERT',
                None
            )
        ),
        help="""Etcd client certificate chain
            (auth_key must also be specified)""",
    )
    auth_key = Unicode(
        config=True,
        allow_none=True,
        default_value=os.environ.get(
            'ETCD_CLIENT_KEY',
            os.environ.get(
                'ETCDCTL_KEY',
                None
            )
        ),
        help="""Etcd client private key
            (auth_cert must also be specified)""",
    )
    endpoint_url = Unicode(
        config=True,
        allow_none=False,
        default_value=os.environ.get('ETCD_CLIENT_URL') or os.environ.get('ETCDCTL_ENDPOINTS').split(',')[-1],
        help="URL of an ETCD client endpoint or gateway."
    )

    @default("client")
    def _default_client(self):
        etcd_service = urlparse(self.endpoint_url)
        return etcd3.client(
            host=str(etcd_service.hostname),
            port=etcd_service.port,
            ca_cert=self.auth_ca,
            cert_cert=self.auth_cert,
            cert_key=self.auth_key,
        )

    def __init__(self, *args, **kwargs):
        self.prefix = ''
        super().__init__(*args, **kwargs)
        pass

    # interface methods
    def set_prefix(self, prefix):
        """Set working/default prefix for all transactions"""
        self.prefix = prefix
        pass

    # @run_on_executor
    def get_keys(self, prefix, **kwargs):
        """return all keys/routes with prefix `path` possibly 
              relativized to `self.prefix`"""
        response = self.client.get_prefix(self.prefix+prefix, keys_only=True)
        keys = [
            m.key.decode().replace(self.prefix, '', 1)
            for v, m in response
        ]
        return keys

    # @run_on_executor
    def get(self, key, apply_func=lambda x : x, **kwargs):
        # if we are given a list of keys
        if isinstance(key, list):
            # then request all of their values in one
            #   transaction
            success = [
                self.client.transactions.get(self.prefix + k)
                for k in key
            ]
            status, response = self.client.transaction(
                compare=[], success=success, failure=[]
            )
            return [
                apply_func(v[0][0].decode())
                for v in response if v[0][0] is not None
            ]

        # otherwise, treat as a single transaction
        value, meta = self.client.get(self.prefix+key, **kwargs)
        if value is None:
            return None
        return apply_func(value.decode())

    def get_json(self, key, **kwargs):
        return self.get(key, apply_func=json.loads, **kwargs)

    # @run_on_executor
    def put(self, obj, value=None, **kwargs):
        """associate `value` with `obj`; unless `obj` is `dict()`, 
            in which case, we perform a transaction associating each 
            dict key with it's value.
        """
        if isinstance(obj, dict):
            success = [
                self.client.transactions.put(self.prefix+key, value)
                for key, value in obj.items()
            ]
            status, response = self.client.transaction(
                compare=[], success=success, failure=[]
            )
            return response
        return self.client.put(self.prefix+obj, value, **kwargs)

    def put_json(self, key, obj, **kwargs):
        """Attempt to serialize `obj` as json, then associate
            encoded value with `key`"""
        return self.put(key, json.dumps(obj), **kwargs)

    # @run_on_executor
    def delete(self, key, prefix=False, **kwargs):
        """Delete `key` and any associated value from the store"""
        if prefix:
            return self.client.delete_prefix(self.prefix+key, **kwargs)
        return self.client.delete(self.prefix+key, **kwargs)


class HubConfig(ETCDClient):

    id = Unicode(
        config=True,
        allow_none=False,
        default_value=os.environ['JUPYTERHUB_ID'],
        help="Unique ID of the jupyterhub instance."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_prefix(
            params.prefix.format(id=self.id)+'/'
        )
        pass

    def export_env(self):
        """
        Save values of environment variables to their
            respective key/value store locations
        """
        fmt_map = params.map_values(drop_prefix=True)
        env_map = {
            key.format(id=self.id): val
            for key, val in fmt_map.items()
        }
        #print(env_map)
        return self.put(env_map)

    def import_env(self):
        raise NotImplementedError()

    def create_files(self):
        keys = params.all_valid_keys(
            self.get_keys(''), drop_prefix=True
        )
        file_map = params.map_all_files(
            keys, drop_prefix=True
        )
        for key, pobj in file_map.items():
            pobj.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            pobj.write_text(self.get(key))
            pobj.chmod(0o600)
            pass
    
    def put_files(self):
        keys = params.all_valid_keys(
            self.get_keys(''), drop_prefix=True
        )
        file_map = params.map_all_files(
            keys, drop_prefix=True
        )
        contents = dict()
        for key, pobj in file_map.items():
            pobj.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            if not pobj.exists():
                # skip missing files..  
                continue
            contents[key] = pobj.read_text()
            pass

        self.put(contents)
        pass

class HubInstance(LoggingConfigurable):
    """
        Class defining and interacting with a discovered or configured 
            instance of JupyterHub
    """
    id = Unicode(
        config=True,
        allow_none=False,
        default_value=None,
        help="Unique ID of the jupyterhub instance."
    )
    token = Unicode(
        config=True,
        allow_none=False,
        default_value=os.environ.get('JUPYTERHUB_API_TOKEN'),
        help="API Token granting administrative access to the intsnace."
    )
    url = Unicode(
        config=True,
        allow_none=False,
        default_value="http://localhost:8080",
        help="URL of JupyterHub instance's controller API url",
    )
    tls_ca = Unicode(
        config=True,
        default_value=os.environ.get(''),
        help="Certificates of trusted CAs for mTLS"
    )
    tls_cert = Unicode(
        config=True,
        default_value=os.environ.get(''),
        help="Client certificate to use when contacting the instance."
    )
    tls_key = Unicode(
        config=True,
        default_value=os.environ.get(''),
        help="Client private key to use when connecting to the instance."
    )

    def populate_config(self):
        """Populates the keys listed in `config_keys`  with
             empty or example values
         """ 
        comp = re.compile(r':[^:}]*}')
        pass

    def generate_env(self):
        pass

    def get_credentials(self):
        pass

    def start_server(self, username, name=None):
        pass

    def stop_server(self, username, name=None):
        pass

    def add_users(self, usernames):
        pass

    def delete_users(self, usernames):
        pass

    def get_all_users(self):
        pass

    def get_user(self, username):
        pass

    def add_groups(self, groups):
        pass

    def delete_groups(self, groups):
        pass

    def get_all_groups(self):
        pass

    def get_group(self, group):
        pass

    def proxy_routes(self):
        pass


def main():
    #hub = HubInstance()
    return 0


if "__name__" == "__main__":
    sys.exit(main())
    pass
