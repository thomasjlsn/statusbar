#!/usr/bin/env bash

OS="$(cat /etc/*release | awk -F '=' '/^ID=/ {print $2}')"

case "$OS" in
  'arch') cp statusd.service.arch statusd.service ;;
  'ubuntu') cp statusd.service.ubuntu statusd.service ;;
esac
