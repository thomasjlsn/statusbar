#!/usr/bin/env bash

if [ -f statusd.service ]; then
  exit 0
fi

cat << EOF > "statusd.service"
[Unit]
Description=statusbar server for tmux and similar

[Service]
ExecStart=$(which statusd) -bcCdmn -w 10
Restart=always
User=root
Group=root

[Install]
WantedBy=multi-user.target
EOF
