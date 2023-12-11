#!/bin/python
from web3 import Web3
from web3.middleware import geth_poa_middleware
from flask import Flask
import json
import time
import re

with open("output/FirmwareUpdate.bin", "r") as bytecode_file:
    contractBytecode = bytecode_file.read()

with open("output/FirmwareUpdate.abi", "r") as abi_file:
    contractABI = json.load(abi_file)

while True:
    time.sleep(5)
    print("[deployContract.py] trying to connect to ethereum node...")
    try:
        web3Instance = Web3(Web3.HTTPProvider("http://0.0.0.0:8545"))
        
        if web3Instance.is_connected():
            print("[deployContract.py] Connected to Ethereum node successfully.")
            break
        
    except Exception as e:
        print(f"[deployContract.py] Connection failed: {str(e)}")
web3Instance.middleware_onion.inject(geth_poa_middleware, layer=0)

chainId = 54000
signerAddress = Web3.to_checksum_address("0xe58c5c83d7547f673cd6cae80445fa816fc00bf6")
with open('./data/keystore/UTC--2023-09-19T01-19-26.659673623Z--e58c5c83d7547f673cd6cae80445fa816fc00bf6') as keyfile:
    encrypted_key = keyfile.read()
    signerPrivateKey = web3Instance.eth.account.decrypt(encrypted_key, 'password0')

contract = web3Instance.eth.contract(abi=contractABI, bytecode=contractBytecode)
currentNonce = web3Instance.eth.get_transaction_count(signerAddress)

deploymentTransaction = contract.constructor().build_transaction({
    "chainId": chainId,
    "from": signerAddress,
    "nonce": currentNonce,
    "gasPrice": web3Instance.to_wei("1", "gwei"),
    "gas": 2000000
})

signedDeploymentTransaction = web3Instance.eth.account.sign_transaction(deploymentTransaction, private_key=signerPrivateKey)
transactionHash = web3Instance.eth.send_raw_transaction(signedDeploymentTransaction.rawTransaction)
transactionReceipt = web3Instance.eth.wait_for_transaction_receipt(transactionHash)
deployedContractAddress = transactionReceipt.contractAddress


webServer = Flask(__name__)

@webServer.route('/getContractAbi', methods=['GET'])
def get_contract_abi():
    with open("output/FirmwareUpdate.abi", "r") as abi_file:
        contractABI = json.load(abi_file)
    return contractABI

@webServer.route('/getContractAddress', methods=['GET'])
def get_contract_address():
    return deployedContractAddress

@webServer.route('/getEnodeAddress', methods=['GET'])
def get_enode_address():
    pattern = r'enode://([^@]*)@([^:]*):([0-9]*)\?discport=([0-9]*)'
    with open('log.txt', 'r') as file:
        for line in file:
            match = re.search(pattern, line)
            if match:
                # Extract the matched groups
                enode = match.group(0)
                pubkey = match.group(1)
                ip_address = match.group(2)
                port = match.group(3)
                discport = match.group(4)

                # return f'enode://{pubkey}@{ip_address}:{discport}'
                return pubkey
            else:
                return ''

webServer.run(host='0.0.0.0', port=54001)