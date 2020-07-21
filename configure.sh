#!/usr/bin/env bash

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

cat << EOF > "statusd.service"
[Unit]
Description=statusbar server for tmux and similar
Wants=network-online.target
After=network-online.target
Requires=$NM.service
PartOf=$NM.service

[Service]
ExecStart=$(which statusd)
Restart=always
User=root
Group=root

[Install]
WantedBy=multi-user.target
EOF
