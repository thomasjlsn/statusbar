#!/usr/bin/env bash

OS="$(cat /etc/*release | awk -F '=' '/^ID=/ {print $2}')"

cp -fv "service_files/statusd.service.$OS" "service_files/statusd.service" || exit 1
