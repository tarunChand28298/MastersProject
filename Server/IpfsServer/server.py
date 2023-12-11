from flask import Flask, send_file
import subprocess
import json

webServer = Flask(__name__)

@webServer.route('/getSwarmKey')
def get_swarm_key():
    return send_file('/root/.ipfs/swarm.key')

@webServer.route('/getBootstrapAddress')
def get_bootstrap_address():
    try:
        # Run the 'ipfs id' command and capture its output
        ipfs_id_output = subprocess.check_output(['ipfs', 'id'], universal_newlines=True)

        # Parse the JSON output
        id_info = json.loads(ipfs_id_output)

        # Extract and return the 'ID' field
        ipfs_id = id_info['ID']
        return ipfs_id

    except subprocess.CalledProcessError as e:
        print(f"Error running 'ipfs id': {e}")
        return None
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing 'ipfs id' output: {e}")
        return None

webServer.run(host='0.0.0.0', port=54000)
