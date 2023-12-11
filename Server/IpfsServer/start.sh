#!/bin/sh

ipfs init

ipfs bootstrap rm --all
export LIBP2P_FORCE_PNET=1

ipfs config Addresses.Gateway /ip4/0.0.0.0/tcp/8080
ipfs config Addresses.API /ip4/0.0.0.0/tcp/5001
ipfs config Routing.Type dht

echo "/key/swarm/psk/1.0.0/\n/base16/\n`tr -dc 'a-f0-9' < /dev/urandom | head -c64`" > /root/.ipfs/swarm.key

(python3 server.py) &

ipfs daemon
