from web3 import Web3
from web3.middleware import geth_poa_middleware
from flask import Flask, render_template, request, jsonify
from ipfshttpclient import Client
import requests
import time
import socket

def connect_to_ethereum():
    while True:
        time.sleep(5)
        print("trying to connect to ethereum node...")
        try:
            web3Instance = Web3(Web3.HTTPProvider("http://geth_signer:8545"))
            
            if web3Instance.is_connected():
                print("Connected to Ethereum node successfully.")
                break
            
        except Exception as e:
            print(f"Connection failed: {str(e)}")
    web3Instance.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    return web3Instance

def get_account():
    account_address = Web3.to_checksum_address("0xe58c5c83d7547f673cd6cae80445fa816fc00bf6")
    return account_address

def get_contract_abi(max_retries=20, retry_interval=5):
    url = "http://geth_signer:54001/getContractAbi"
    retries = 0

    while retries < max_retries:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                contract_abi = response.json()
                return contract_abi
            else:
                raise Exception(f"Failed to fetch contract ABI. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error fetching contract ABI (Attempt {retries + 1}): {str(e)}")
            retries += 1
            time.sleep(retry_interval)

    raise Exception(f"Max retries reached. Unable to fetch contract ABI.")


def get_contract_address(max_retries=20, retry_interval=5):
    url = "http://geth_signer:54001/getContractAddress"
    retries = 0

    while retries < max_retries:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                contract_address = response.text.strip()
                return contract_address
            else:
                raise Exception(f"Failed to fetch contract address. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error fetching contract address (Attempt {retries + 1}): {str(e)}")
            retries += 1
            time.sleep(retry_interval)

    raise Exception(f"Max retries reached. Unable to fetch contract address.")

def connect_to_ipfs():
    ipAddress = socket.gethostbyname("ipfs_server")
    ipfs = Client(f'/ip4/{ipAddress}/tcp/5001')
    return ipfs

# Main script
def Upload(firmwareFile, deviceName):
    web3 = connect_to_ethereum()
    account = get_account()
    contract_abi = get_contract_abi()
    contract_address = get_contract_address()
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)

    ipfs = connect_to_ipfs()
    ipfs_hash = ipfs.add_bytes(firmwareFile)

    transaction_hash = contract.functions.storeFirmware(ipfs_hash, deviceName).transact({'from': account})

    receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)
    return {'status': receipt.status, 'hash': ipfs_hash}


##########################################################################################################################

webServer = Flask(__name__)

@webServer.route('/')
def index():
    return render_template("index.html")

@webServer.route('/upload', methods=['POST'])
def upload():
    firmware_file = request.files['firmwareFile']
    device_name = request.form['deviceName']

    if firmware_file and device_name:
        result = Upload(firmware_file, device_name)
        return jsonify(result)
    else:
        return jsonify({'error': 'No file or device name provided in the request.'})
        
webServer.run(host='0.0.0.0', port=54002)
