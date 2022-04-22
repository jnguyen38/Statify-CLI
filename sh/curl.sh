#!/usr/bin/sh

curl --request GET \
  --url https://api.spotify.com/v1/me/top/type \
  --header 'Authorization: ' \
  --header 'Content-Type: application/json'
