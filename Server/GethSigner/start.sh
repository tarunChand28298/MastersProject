#!/bin/sh
IP=$(ip addr show $(ip route | awk '/default/ { print $5 }') | grep "inet" | head -n 1 | awk '/inet/ {print $2}' | cut -d'/' -f1)

bootnode --genkey=boot.key
bootnode --nodekey=boot.key --writeaddress 
bootnode --nodekey=boot.key --addr="$IP":30301 > log.txt &
sleep 5

ENODEADDR=$(cat log.txt | sed -n 's/enode:\/\/\([^@]*\)@\(.*\):\(.*\)?discport=\([0-9]*\).*/enode:\/\/\1@\2:\4/p')

(/root/compileAndDeploy.sh) &

geth init --datadir ./data genesis.json
geth --datadir "./data" \
    --networkid 54000 \
    --bootnodes "$ENODEADDR" \
    --port 30302 \
    --ipcdisable \
    --syncmode full \
    --http \
    --allow-insecure-unlock \
    --http.corsdomain "*" \
    --http.vhosts="*" \
    --http.addr 0.0.0.0 \
    --http.port 8545 \
    --http.api "personal,db,eth,net,web3,txpool,miner" \
    --unlock 0xe58c5c83d7547f673cd6cae80445fa816fc00bf6 \
    --password password.txt \
    --mine --miner.etherbase 0xe58c5c83d7547f673cd6cae80445fa816fc00bf6
