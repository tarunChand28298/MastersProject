#!/bin/sh

# SERVER_IP="3.21.236.129"

ENODE_PUBKEY=$(curl $SERVER_IP:54001/getEnodeAddress)
ENODEADDR=enode://$ENODE_PUBKEY@$SERVER_IP:30301

geth account new --datadir "./data" --password <(cat password.txt) > account.txt
ACCOUNT=$(cat account.txt | grep -oE '0x[0-9a-fA-F]+')

geth init --datadir "./data" genesis.json
geth --datadir "./data" \
     --networkid 54000 \
     --bootnodes $ENODEADDR \
     --port 30302 \
     --ipcdisable \
     --syncmode full \
     --http \
     --allow-insecure-unlock \
     --http.corsdomain "*" \
     --http.addr 0.0.0.0 \
     --http.port 8545 \
     --http.api "personal,db,eth,net,web3,txpool,miner" \
     --unlock $ACCOUNT \
     --password password.txt
