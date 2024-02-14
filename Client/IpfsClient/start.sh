#!/bin/sh

# SERVER_IP="3.21.236.129"

ipfs init

ipfs bootstrap rm --all
export LIBP2P_FORCE_PNET=1

ipfs config Addresses.Gateway /ip4/0.0.0.0/tcp/8080
ipfs config Addresses.API /ip4/0.0.0.0/tcp/5001
ipfs config Routing.Type dht

wget $SERVER_IP:54000/getBootstrapAddress -O IpfsId
IPFSENDPOINT=$(cat IpfsId)
ipfs bootstrap add /ip4/$SERVER_IP/tcp/4001/p2p/$IPFSENDPOINT
rm IpfsId

wget $SERVER_IP:54000/getSwarmKey -O /data/ipfs/swarm.key

ipfs daemon
