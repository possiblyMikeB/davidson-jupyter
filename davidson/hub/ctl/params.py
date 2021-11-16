
import os
import re
from pathlib import Path
from . import utils

# etcd keys used for configuration

prefix_reg = re.compile(r'/jupyterhub/(?P<id>[A-Za-z0-9]+)')
prefix = '/jupyterhub/{id}'

# ######################################################################

class ParameterGroup(utils.KeepRefs):
    def __init__(
        self, keys=[], files=dict(),
        prefix='', prefix_env=''
     ):
        super().__init__()
        self.group_prefix = prefix
        self.group_prefix_env = prefix_env
        self.keys = keys
        self.files = files
        pass

    def env_vars(self):
        if not self.group_prefix_env:
            return []

        var_prefix = self.group_prefix_env
        return [
            f'{var_prefix}{suffix}'
            for suffix in [
                utils.regex_to_var(key)
                for key in self.keys
            ]
        ]

        pass

    def get_keys(self, drop_prefix=False):
        pref = self.group_prefix
        if drop_prefix:
            pref = pref.replace(prefix+'/', '', 1)
        return [
            f'{pref}{key}'
            for key in self.keys
        ]
        pass

    def valid_keys(self, keys, drop_prefix=False):
        """Return the list of entries from `keys` which match
            a key/regex in the ParameterGroup"""
        valid = []
        for key_reg in self.get_keys(drop_prefix=drop_prefix):
            reg = re.compile(f'^{key_reg}$')
            for key in keys:
                m = reg.match(key)
                if m:
                    valid.append(key)
        return valid

    def map_envs(self, drop_prefix=False):
        return dict(
            zip(
                self.get_keys(drop_prefix=drop_prefix),
                self.env_vars()
            )
        )

    def map_files(self, keys, drop_prefix=False):
        fmap = dict()
        for rel_reg, path_fmt in self.files.items():
            key_reg = self.group_prefix+rel_reg
            if drop_prefix:
                key_reg = key_reg.replace(prefix+'/', '', 1)
            reg = re.compile(f'^{key_reg}$')
            for key in keys:
                m = reg.match(key)
                if m:
                    fmap[key] = Path(
                        path_fmt.format(**m.groupdict())
                    )
        return fmap
    pass


# #####################################################################

hub = {
    'prefix_env': 'JUPYTERHUB_',
    'prefix': f'{prefix}/',
    'keys':
    [
        'enabled',
        'port',
        'status',
        'cookie-secret',
        'crypt-key',
        'internal-tls',

        'path/data',
        'path/templates',
        'path/run',
        'path/certs',

        'db/scheme',
        'db/username',
        'db/password',
        'db/host',
        'db/name',
        'db/snapshot'
    ]
}

proxy = {
    'prefix_env': 'PROXY_',
    'prefix': f'{prefix}/proxy/',
    'keys':
    [
        'api-url',
        'username',
        'password',
        'prefix',
        'auth/ca',
        'auth/cert',
        'auth/key',
        'token',
        'trusted-port'

        # NOTE: The keys
        #     '/jupyterhub/{id}/proxy/routes{path:^/[a-zA-Z0-9-_/]*}',
        #   maintained by jupyterhub
    ]
}

service = {
    'prefix_env': 'SERVICE_',
    'prefix': f'{prefix}/service/',
    'keys':
    [
        'cull-idle/timeout',
        'cull-idle/every',
        'cull-idle/users',
        'cull-idle/concurrency',
        'cull-idle/max-age',

        'announcements/message',
        'announcements/data'
    ],
    'files': {
        'announcements/data': 'announcements.json'
    }

}

auth = {
    'prefix_env': '',
    'prefix':  f'{prefix}/auth/',
    'keys':
    [
        r'ldap/cache',
        r'ldap/server/address',
        r'ldap/server/userdn',
        r'ldap/server/password',
        r'ldap/attributes', 
        r'ldap/user-base',
        r'ldap/user-attribute',
        r'ldap/groups/allow',
        r'ldap/groups/require',

        r'duo/ikey',
        r'duo/skey',
        r'duo/akey',
        r'duo/api-host',

        r'lti/(?P<app>[a-zA-Z0-9-_]+)/key',
        r'lti/(?P<app>[a-zA-Z0-9-_]+)/secret',
        r'lti/(?P<app>[a-zA-Z0-9-_]+)/user_attr'
    ],
    'files': {}
}

spawner = {
    'prefix_env': 'SPAWNER_',
    'prefix': f'{prefix}/spawner/',
    'keys':
    [
        'default-url',
        'timeout',
        'cmd',

        'slurm/script-template',
        'slurm/job/name',
        'slurm/job/cluster',
        'slurm/job/partition',
        'slurm/job/account',
        'slurm/job/qos',
        'slurm/job/ntasks',
        'slurm/job/nprocs',
        'slurm/job/memory',
        'slurm/job/reservation',
        'slurm/job/gres',
        'slurm/job/runtime',
        'slurm/job/prolog',
        'slurm/job/epilogue',
        'slurm/job/extra',
        'slurm/task/prolog',
        'slurm/task/epilogue',
        'slurm/task/extra',
        'slurm/conda/path',
        'slurm/conda/env',
        'slurm/conda/install',
        'slurm/conda/update',
        'slurm/submit/host',
        'slurm/submit/token',

        'systemd/host',
        'systemd/limit-cpu',
        'systemd/limit-mem',
        'systemd/isolate-devices',
        'systemd/isolate-temp',
        'systemd/disable-sudo',
        'systemd/properties',

        'docker/image'
    ],
    'files': {}
}

internal_tls = {
    'prefix': f'{prefix}/tls/',
    'keys':
    [
        'certipy',
        'ca/proxy-client/cert',
        'ca/proxy-client/key',
        'ca/proxy-client/trusts',
        'ca/proxy-api/cert',
        'ca/proxy-api/key',
        'ca/proxy-api/trusts',
        'ca/notebooks/cert',
        'ca/notebooks/key',
        'ca/notebooks/trusts',
        'ca/services/cert',
        'ca/services/key',
        'ca/services/trusts',
        'ca/hub/cert',
        'ca/hub/key',
        'ca/hub/trusts',

        'cert/hub-internal/cert',
        'cert/hub-internal/key',
        'cert/hub-internal/ca',
        'cert/proxy-client/cert',
        'cert/proxy-client/key',
        'cert/proxy-client/ca',
        'cert/proxy-api/cert',
        'cert/proxy-api/key',
        'cert/proxy-api/ca',

        r'cert/user-(?P<name>[a-z0-9]+)/cert',
        r'cert/user-(?P<name>[a-z0-9]+)/key',
        r'cert/user-(?P<name>[a-z0-9]+)/ca'
    ],
    'files':
    {
        r'certipy': 'certipy.json',
        r'ca/(?P<name>[a-zA-Z0-9_-]+)/cert': 'tls/{name}-ca/{name}-ca.crt',
        r'ca/(?P<name>[a-zA-Z0-9_-]+)/key': 'tls/{name}-ca/{name}-ca.key',
        r'ca/(?P<name>[a-zA-Z0-9_-]+)/trust': 'tls/{name}-ca_trust.crt',
        r'cert/(?P<name>[a-zA-Z0-9_-]+)/cert': 'tls/{name}/{name}.crt',
        r'cert/(?P<name>[a-zA-Z0-9_-]+)/key': 'tls/{name}/{name}.key',
        r'cert/(?P<name>[a-zA-Z0-9_-]+)/ca': 'tls/{name}/ca_trust.crt'
    }
}


# eval $(sed -ne 's/"/\\"/g; s/\(^[A-Z0-9a-z_-][^=]\+\)=\(.*\)$/export \1="\2"/p' "etc/jupyterhub/private.sh")


hub = ParameterGroup(**hub)
proxy = ParameterGroup(**proxy)
service = ParameterGroup(**service)
spawner = ParameterGroup(**spawner)
auth = ParameterGroup(**auth)
internal_tls = ParameterGroup(**internal_tls)


def all_keys(drop_prefix=False):
    ret = []
    for obj in ParameterGroup.get_instances():
        ret.extend(obj.get_keys(drop_prefix=drop_prefix))
    return ret


def all_envs():
    ret = []
    for obj in ParameterGroup.get_instances():
        ret.extend(obj.env_vars())
    return ret


def all_valid_keys(keys, drop_prefix=False):
    ret = []
    for obj in ParameterGroup.get_instances():
        ret.extend(obj.valid_keys(keys, drop_prefix=drop_prefix))
    return ret


def map_all_envs(drop_prefix=False):
    ret = dict()
    for obj in ParameterGroup.get_instances():
        ret.update(obj.map_envs(drop_prefix=drop_prefix))
    return ret


def map_values(drop_prefix=False):
    var_map = map_all_envs(drop_prefix=drop_prefix)
    ret = dict()
    for key, var in var_map.items():
        reg = re.compile(f'^{var}$')
        fkey = utils.regex_to_fmt(key)
        for name in os.environ.keys():
            m = reg.match(name)
            if m:
                fkey = fkey.format(id='{id}', **m.groupdict())
                ret[fkey] = os.environ.get(name)
                break
    return ret


def map_all_files(keys, drop_prefix=False):
    ret = dict()
    for obj in ParameterGroup.get_instances():
        ret.update(
            obj.map_files(keys, drop_prefix=drop_prefix)
        )
    return ret
