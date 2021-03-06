#!/usr/bin/env python3
import os, sys
from runpy import run_path
from shutil import which
from jupyterhub.utils import random_port, url_path_join
from jupyterhub.services.auth import HubAuth

def main(argv=None):
    port = random_port()
    hub_auth = HubAuth()
    hub_auth.client_ca = os.environ.get('JUPYTERHUB_SSL_CLIENT_CA', '')
    hub_auth.certfile = os.environ.get('JUPYTERHUB_SSL_CERTFILE', '')
    hub_auth.keyfile = os.environ.get('JUPYTERHUB_SSL_KEYFILE', '')

    obj=dict([('port', port)])
    url=url_path_join(hub_auth.api_url, 'batchspawner')

    # record useful information
    print((f"Connecting to controller....\n" 
           f"URL: {url}\n"
           f"Payload: {obj}"), flush=True)

    hub_auth._api_request(method='POST', url=url, json=obj)
    print("Sent", flush=True)

    cmd_path = which(sys.argv[1])
    sys.argv = sys.argv[1:] + ['--port=' + str(port)]
    run_path(cmd_path, run_name="__main__")
    pass

#
# XXX: command installed with `console_script` facility of setup-tools 
#
#if __name__ == "__main__":
#    main()
#
