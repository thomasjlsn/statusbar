#!/usr/bin/env bash

if [ -f pybar.service ]; then
  exit 0
fi

cat << EOF > "pybar.service"
[Unit]
Description=statusbar server for tmux and similar

[Service]
ExecStart=$(which pybar) -bcCdmn -a -w 10
Restart=always
User=root
Group=root

[Install]
WantedBy=multi-user.target
EOF
