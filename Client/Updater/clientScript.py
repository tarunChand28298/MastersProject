from web3 import Web3
from web3.middleware import geth_poa_middleware
from flask import Flask, render_template, request, jsonify
from ipfshttpclient import Client
import requests
import time
import socket
import os

# SERVER_IP = "3.21.236.129"
SERVER_IP = os.getenv("SERVER_IP")

def connect_to_ethereum():
    while True:
        time.sleep(5)
        print("trying to connect to ethereum node...")
        try:
            web3Instance = Web3(Web3.HTTPProvider(f"http://{SERVER_IP}:8545"))
            
            if web3Instance.is_connected():
                print("Connected to Ethereum node successfully.")
                break
            
        except Exception as e:
            print(f"Connection failed: {str(e)}")
    web3Instance.middleware_onion.inject(geth_poa_middleware, layer=0)
    
    return web3Instance

def get_contract_abi():
    url = f"http://{SERVER_IP}:54001/getContractAbi"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            contract_abi = response.json()
            return contract_abi
        else:
            raise Exception(f"Failed to fetch contract ABI. Status code: {response.status_code}")
    except Exception as e:
        raise Exception(f"Error fetching contract ABI: {str(e)}")

def get_contract_address():
    url = f"http://{SERVER_IP}:54001/getContractAddress"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            contract_address = response.text.strip()
            return contract_address
        else:
            raise Exception(f"Failed to fetch contract address. Status code: {response.status_code}")
    except Exception as e:
        raise Exception(f"Error fetching contract address: {str(e)}")

def connect_to_ipfs():
    ipAddress = socket.gethostbyname("ipfs_client")
    ipfs = Client(f'/ip4/{ipAddress}/tcp/5001')
    return ipfs

def update_firmware(firmware_bytes):
    # Implement firmware update logic here
    print(firmware_bytes)
    print("Firmware updated")

def InvokeUpdate(device):
    web3 = connect_to_ethereum()
    contract_abi = get_contract_abi()
    contract_address = get_contract_address()
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    latest_firmware_hash = contract.functions.getLatestFirmwareHash(device).call()

    ipfs = connect_to_ipfs()
    latest_firmware = ipfs.cat(latest_firmware_hash)

    update_firmware(latest_firmware)
    return {'status': latest_firmware_hash, 'data': latest_firmware.decode('utf-8')}

##########################################################################################################################

webServer = Flask(__name__)

@webServer.route('/')
def index():
    return render_template("index.html")

@webServer.route('/update', methods=['POST'])
def update():
    device_name = request.form['deviceName']
    result = InvokeUpdate(device_name)
    return jsonify(result)

webServer.run(host='0.0.0.0', port=54000)
