#!/usr/bin/env bash

OS="$(cat /etc/*release | awk -F '=' '/^ID=/ {print $2}')"

{ sh "service_files/statusd.service.$OS" || exit 1; } > "service_files/statusd.service"
