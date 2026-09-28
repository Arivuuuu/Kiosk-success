import uuid
import requests
import json

API_ENDPOINT = 'http://0.0.0.0:8001/api/'

def get_mac():
    mac = hex(uuid.getnode()).replace('0x', '').zfill(12)
    mac_address = ':'.join(mac[i:i+2] for i in range(0, 12, 2))  
    url = API_ENDPOINT+'create-new-mac/'
    data = {'machine_id': mac_address}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    return requests.post(url, data=json.dumps(data), headers=headers)

if __name__ == "__main__":
    result = get_mac()
    print(result)
    print(result.text)