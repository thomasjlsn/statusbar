#!/usr/bin/env bash

if [ -f pybar.service ]; then
  exit 0
fi

function installed {
  2>/dev/null 1>&2 command -v "${1?}"
}

if installed 'network-manager'; then
  NM='network-manager'
elif installed 'NetworkManager'; then
  NM='NetworkManager'
else
  2>/dev/null echo 'no network manager installed'
  exit 1
fi

cat << EOF > "pybar.service"
[Unit]
Description=pybar: statusbar server
Wants=network-online.target
After=network-online.target
Requires=$NM.service
PartOf=$NM.service

[Service]
ExecStart=$(which pybar) start
Restart=always
User=root
Group=root

[Install]
WantedBy=multi-user.target
EOF
