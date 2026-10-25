#!/usr/bin/env bash
# Creates the DNS record for coverly-shelf.maecly.com in the Cloudflare zone
# maecly.com, the same way coverly-roms.maecly.com is set (CNAME to the
# project's Vercel target, DNS only, TTL auto). Touches no other record.
# Then asks Vercel to verify the domain and polls HTTPS until it answers.
set -euo pipefail
ZONE=3fd532fe3ec5022c584073a96c3886e8
NAME=coverly-shelf.maecly.com
TARGET=378f9811384096f0.vercel-dns-016.com
eval "$(grep '^export CLOUDFLARE_API_TOKEN' ~/.zshrc)"
API="https://api.cloudflare.com/client/v4/zones/$ZONE/dns_records"
H=(-H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" -H "Content-Type: application/json")

existing=$(curl -s "${H[@]}" "$API?name=$NAME" | python3 -c 'import json,sys; r=json.load(sys.stdin)["result"]; print(r[0]["id"] if r else "")')
if [ -n "$existing" ]; then
  echo "Record already exists: $existing (left untouched)"
else
  curl -s -X POST "${H[@]}" "$API" \
    --data "{\"type\":\"CNAME\",\"name\":\"$NAME\",\"content\":\"$TARGET\",\"proxied\":false,\"ttl\":1,\"comment\":\"Vercel - coverly-shelf-landing\"}" |
    python3 -c 'import json,sys; d=json.load(sys.stdin); print("created" if d["success"] else d["errors"], (d.get("result") or {}).get("id"))'
fi

cd /Users/miguelangelesparzacalero/Documents/GitHub/coverly-shelf-landing
vercel domains verify "$NAME" --scope migelangelecs-projects >/dev/null 2>&1 || true
for i in $(seq 1 30); do
  es=$(curl -s -o /dev/null -w '%{http_code}' "https://$NAME/" || true)
  en=$(curl -s -o /dev/null -w '%{http_code}' "https://$NAME/en/" || true)
  echo "try $i: / -> $es, /en/ -> $en"
  [ "$es" = 200 ] && [ "$en" = 200 ] && exit 0
  sleep 10
done
echo "Not live yet; the certificate can take a few more minutes." >&2
exit 1
