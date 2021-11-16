#!/bin/bash


# NOTE: API Documentation
#   https://petstore.swagger.io/?url=https://raw.githubusercontent.com/jupyterhub/jupyterhub/master/docs/rest-api.yml
# 
HUB_ID=${HUB_ID:-DEV}
HUB_URL=$(etcdctl get --print-value-only \
            traefik/http/services/${HUB_ID}-public/loadbalancer/servers/0/url)

CURL="scripts/curl.sh"
SECRETS="etc/jupyterhub/private.sh"

# verify the script can access what we need exist
[ -x "$CURL" ] || (echo "Must run from git repo root"; exit 1)
[ -e "$SECRETS" ] || (echo "Cannont find secrets file"; exit 1)

# import private environment variables 
eval $(sed -ne 's/\(^[A-Z0-9a-z_-][^=]\+\)=\(.*\)/export \1="\2"/p' "${SECRETS}")

${CURL} hub-internal \
    -H "Authorization: token ${TEST_TOKEN}" \
    -X GET \
    "${HUB_URL}/hub/api/info" | jq '.' 

${CURL} hub-internal \
    -H "Authorization: token ${TEST_TOKEN}" \
    -X GET \
    "${HUB_URL}/hub/api/user" | jq '.' 


exit 0

${CURL} hub-internal \
    -H "Authorization: token ${TEST_TOKEN}" \
    -o "data.json" \
    -X GET \
    "${HUB_URL}/hub/api/users"

tee data.json <<EOF
{
    "usernames": [
        "student_test","student_test1",
        "student_test2","student_test3",
        "student_test6","student_test7",
        "student_test4","student_test5",
        "student_test8","student_test9",
        "student_test10","student_test11",
        "student_test12","student_test13",
        "student_test14","student_test15",
        "student_test16","student_test17",
        "student_test18","student_test19",
        "student_test20","student_test21",
        "student_test22","student_test23",
        "student_test24","student_test25"
    ],
    "admin": false
}
EOF

${CURL} hub-internal \
    -H "Authorization: token ${TEST_TOKEN}" \
    -H "Content-Type: application/json" \
    -d @data.json \
    -X POST \
    "${HUB_URL}/hub/api/users"

exit 0

${CURL} hub-internal \
    -H "Authorization: token ${TEST_TOKEN}" \
    -X GET \
    "${HUB_URL}/hub/api/users"

${CURL} hub-internal \
    -H "Authorization: token ${TEST_TOKEN}" \
    -d @data.json \
    -X DELETE \
    "${HUB_URL}/hub/api/users"

