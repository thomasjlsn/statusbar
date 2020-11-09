#!/usr/bin/env bash

CONFIG='pybar.conf'

if [ -f "$CONFIG" ]; then
  exit 0
fi

{

printf '#!/usr/bin/env sh

# ==========================================================================
#                               pybar config
# ==========================================================================

'

command grep -horP 'getenv(.*PYBAR_[A-Z_][^)]*)' | sort | uniq |
  sed "
    s/.*(//g;
    s/).*//g;
    s/[\"']//;
    s/[\"']//;
    s/, \?/=/;
    s/\ *=\ */=/;
  "

} | tee "$CONFIG"
