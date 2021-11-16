import unittest
import os
from pathlib import Path
import shutil
from hubctl.config import HubConfig
from hubctl.config import ETCDClient


class ConfigTests(unittest.TestCase):
    client = ETCDClient()
    config = HubConfig()

    def test_ETCD_atomic(self):
        self.client.put('/jupyterhub/DEV/enabled', 'true')
        self.assertEqual(
            self.client.get('/jupyterhub/DEV/enabled'),
            'true'
        )
        pass

    def test_ETCD_many(self):
        self.client.put({
            '/jupyterhub/DEV/enabled': 'false',
            '/jupyterhub/DEV/port': '8089',
            '/jupyterhub/DEV/proxy/api-url': 'http://traefik.dev.jupyter.davidson.edu:9000'
        })
        self.assertEqual(
            set(self.client.get([
                '/jupyterhub/DEV/enabled',
                '/jupyterhub/DEV/port',
                '/jupyterhub/DEV/proxy/api-url'
            ])),
            {
                'false',
                '8089',
                'http://traefik.dev.jupyter.davidson.edu:9000'
            }
        )
        pass

    def test_ETCD_get_keys(self):
        from random import choice
        keys = {
            '/jupyterhub/DEV/db/host',
            '/jupyterhub/DEV/db/name',
            '/jupyterhub/DEV/db/password',
            '/jupyterhub/DEV/db/scheme',
            '/jupyterhub/DEV/db/username',
            '/jupyterhub/DEV/db/snapshot'
        }

        for key in keys:
            self.client.put(key, 'that thing ' * choice(list(range(10))))
            
        self.assertEqual(
            set(self.client.get_keys('/jupyterhub/DEV/db')),
            keys
        )
        pass

    def test_ETCD_delete(self):
        self.client.put({
            '/test/delete': '1',
            '/test/delete/prefix1': '2',
            '/test/delete/prefix2': '3'
        })
        self.assertTrue(
            self.client.delete('/test/delete'),
            "Should return true when key deleted"
        )
        self.assertFalse(
            self.client.delete('/test/delete'),
            "Should return false when key doesn't exist"
        )
        self.assertEqual(
            self.client.delete('/test/delete', prefix=True).deleted,
            2,
            "Should delete 2 remaining keys"
        )

    def test_ETCD_json(self):
        obj = {
            'first': True,
            'second': {
                'nest_depth': 1,
                'counts': ['this', 'is', 'a', 'list']
            },
            'a_string': 'as promised'
        }
        self.client.put_json('/test/obj', obj)
        self.assertEqual(
            self.client.get_json('/test/obj'),
            obj
        )
        pass

    def test_HubConfig_export_env(self):
        os.environ['JUPYTERHUB_PORT'] = '69420'
        self.config.export_env()
        self.assertEqual(
            self.client.get('/jupyterhub/DEV/port'),
            '69420'
        )
        pass

    def test_HubConfig_files(self):
        # there is a rule in params.internal_tls which
        #  will cause the following key to generate a new file
        self.config.put('tls/cert/user-testing/cert', 'a thing')
        
        try:
            # remove target parent directory (if it exists)
            shutil.rmtree('tls')
        except FileNotFoundError:
            pass

        # pull/create/restore config-backed files
        self.config.create_files()

        # make sure it's worked
        self.assertEqual(
            Path('tls/user-testing/user-testing.crt').read_text(),
            'a thing'
        )

        # overwrite contents of key-associated file
        Path('tls/user-testing/user-testing.crt').\
            write_text('not that thing')
        
        # update file associated key values
        self.config.put_files()

        # verify contents of kv-store
        self.assertEqual(
            self.config.get('tls/cert/user-testing/cert'),
            'not that thing'
        )

        pass

if __name__ == "__main__":
    unittest.main()

