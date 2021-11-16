#!/bin/bash

HUB_ID=${JUPYTERHUB_ID:-DEV}

cert_dnames() {
  tee -a /dev/null <<EOF
{
  "OU": "Technology and Innovation",
   "O": "Davidson College",
   "L": "Davidson",
  "ST": "North Carolina",
   "C": "US"  
}
EOF
}

# Certificate signing configuration
CONF=$(cfssl print-defaults config \
          | sed -e's/"www"/"peer"/g' -e's/\("server auth"\)/\1, "client auth"/g' \
          | jq -rc '.' | tee /tmp/config.json)

# Subject Names information
NS=$(cert_dnames)

for name in proxy-api proxy-client hub notebooks services; do

    # generate a self-signed root CA and `sub.json`
    CA=$(cfssl print-defaults csr \
        | jq -rc '{CN: $cn, key: .key, names: [$ns], hosts: []}' \
             --argjson ns "${NS}" \
             --arg cn "${name}-ca" \
        | tee /tmp/csr.json \
        | cfssl gencert -initca -)

    # push CA into the envionment 
    export CA

    # extract PEM encoded Cert & Private key
    jq -nrc 'env.CA|fromjson|.key'  | etcdctl put "/jupyterhub/${HUB_ID}/tls/ca/${name}/key"
    jq -nrc 'env.CA|fromjson|.cert' | etcdctl put "/jupyterhub/${HUB_ID}/tls/ca/${name}/cert"
    
    export CERT=$(etcdctl get --print-value-only "/jupyterhub/${HUB_ID}/tls/ca/${name}/cert")
    export KEY=$(etcdctl get --print-value-only "/jupyterhub/${HUB_ID}/tls/ca/${name}/key")

    ## use SLURM to grab list of hostnames
    hosts=`sinfo -p basic,gpus -N  --format "%N,%n,%o" --noheader`

    #cfssl gencert \
    #    -ca env:CERT \
    #    -ca-key env:KEY \
    #    -config /tmp/config.json -profile peer \
    #    -cn "${name}" -hostnames "${hosts//$'\n'/,}" \
    #    /tmp/csr.json
    
done
# $(etcdctl get /path/to/magic/CA)
# #################
#
# - Endpoint-1:  
#      cn: App-Proxy
#      user: System
#      hostnames: jupyterctl0,jupyterdev0,galaxydev0,galaxyctl0,shinyapp0
#
# - Endpoint-2:  
#      cn: User & App
#      user: 
#      hostnames:
#jq -nrc '$sub|={CN: ..endpoint-1-cn.., hosts: ...)

# XXX: 
#     cfssl gencert -ca=env:CERT -ca-key=env:KEY -profile=peer -config=config.json -

#for var in blank traefik hub dev; do
#    mkjson "${var}" | cfssl genkey - | cfssljson -bare "${var}"  
#done;

 