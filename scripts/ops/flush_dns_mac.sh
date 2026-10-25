#!/usr/bin/env bash
# Clears macOS's DNS cache (it can keep a "does not exist" answer for a
# freshly created record) and checks the landing answers on its domain.
set -euo pipefail
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
sleep 2
for path in / /en/; do
  echo "https://coverly-shelf.maecly.com$path -> $(curl -s -o /dev/null -w '%{http_code}' "https://coverly-shelf.maecly.com$path")"
done
