#!/bin/sh
set -eu

certificate_dir="/etc/letsencrypt/live/${DOMAIN}"
certificate_file="${certificate_dir}/fullchain.pem"

if [ ! -f "${certificate_file}" ]; then
    mkdir -p "${certificate_dir}"
    openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
        -keyout "${certificate_dir}/privkey.pem" \
        -out "${certificate_file}" \
        -subj "/CN=${DOMAIN}"
fi