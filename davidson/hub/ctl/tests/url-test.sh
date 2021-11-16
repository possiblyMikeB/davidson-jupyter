#!/bin/bash -l
# Id of the hub to test
HUB_ID=DEV

# location jupyterhub stores generated certs
CERT_STORE="${HOME}/workspace/build/debug/run/${HUB_ID}/internal-tls"

# list of keys dealing with this hub instance 
URLS=(`etcdctl get --prefix --print-value-only "traefik/http/services/${HUB_ID}-"|sed -ne /^http/p`)
CERTS=(`ls -1 ${CERT_STORE}/*/*.crt`)

for url in "${URLS[@]}"; do
    for cert in "${CERTS[@]}"; do
        key="$( dirname $cert )/$( basename $cert .crt ).key"
        ca="$( dirname $cert )-ca_trust.crt"

        curl -L ${url} \
            --cacert "${ca}" \
            --cert "${cert}" \
	        --key "${key}" \
	        -vvvv  
    done
done

