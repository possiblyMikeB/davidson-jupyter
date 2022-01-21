"""
0;10;1cReturn config on servers to start for theia

See https://jupyter-server-proxy.readthedocs.io/en/latest/server-process.html
for more information.
"""
import os
import shutil

def setup_theia():
    # Make sure theia is in $PATH
    def _theia_command(port):
        pwd = os.getcwd()
        full_path = shutil.which('theia')
        if not full_path:
            raise FileNotFoundError('Can not find theia executable in $PATH')
        return [ 'bash', '-c',
            f'source /etc/profile && module load theia && cd /opt/pub/apps/theia-cpp && theia start {pwd} --hostname=127.0.0.1 --port={port}' ]

    return {
        'command': _theia_command,
        'environment': {
            'USE_LOCAL_GIT': 'true'
        },
        'timeout': 15,
        'launcher_entry': False
    }
