#! /bin/bash

curl --request PUT \
    --data-binary @${1} \
    --header "X-ApiKey: "${2} \
    --verbose \
    http://api.cosm.com/v2/feeds/${3}
