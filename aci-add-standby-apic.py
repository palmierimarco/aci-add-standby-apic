import requests
import json
import yaml
# from time import time
# import os
requests.urllib3.disable_warnings()

# Control functions

def yaml_to_json(file):
    '''Function to convert yaml to json'''
    with open(file, "r") as stream:
        try:
            parsed_yaml=yaml.safe_load(stream)
            return parsed_yaml
        except yaml.YAMLError as exc:
            print(exc)
    pass

def write_json_to_file(json_data, file):
    '''Function to write json to file'''
    with open(f'./{file}', 'w') as f:
        json_object = json.loads(json_data)
        f.write(json.dumps(json_object, indent=4))


def get_apic_token(url, apic_user, apic_pwd):
    ''' Get APIC Token'''
    login_url = f'{url}/aaaLogin.json'
    s = requests.Session()
    payload = {
         "aaaUser" : {
              "attributes" : {
                   "name" : apic_user,
                   "pwd" : apic_pwd
               }
           }
       }
    resp = s.post(login_url, json=payload, verify=False)
    resp_json = resp.json()
    token = resp_json['imdata'][0]['aaaLogin']['attributes']['token']
    cookie = {'APIC-cookie':token}
    cookie_file = json.dumps(resp_json['imdata'][0]['aaaLogin']['attributes'])
    return cookie, cookie_file


def check_cimc_validation(apic_ip, cookie, cimc_ip, cimc_user, cimc_pwd):
    '''Function to check if CIMC credentials are valid'''
    url = f'https://{apic_ip}/api/workflows/v1/controller/verify'
    body = {
        "address" : cimc_ip,
        "username" : cimc_user,
        "password" : cimc_pwd,
        "addressType" : "cimc",
        "controllerType" : "physical"
        }
    r_post = requests.post(url, json=body, cookies=cookie, verify=False)
    if r_post.status_code == 200:
        standby_apic_serial_number = r_post.json()['serialNumber']
        print("CIMC credentials are valid:\n")
        print(json.dumps(r_post.json(), indent=4))
        return standby_apic_serial_number
    else:
        print("CIMC credentials are invalid:\n")
        print(json.dumps(r_post.json(), indent=4))
        exit(1)

def add_standby_apic(apic_ip, cookie, 
                     standby_apic_name, 
                     standby_apic_node_id,
                     standby_apic_admin_pwd, 
                     standby_apic_cimc_ip, 
                     standby_apic_cimc_user, 
                     standby_apic_cimc_pwd, 
                     standby_apic_pod_id, 
                     standby_apic_oob_ip, 
                     standby_apic_oob_gw,
                     standby_apic_serial_number):
    '''Function to add standby APIC to existing APIC cluster'''
    url = f'https://{apic_ip}/api/workflows/v1/controller/add'
    body = {
        "adminPassword": standby_apic_admin_pwd,
        "force": False,
        "nodes": [
            {
                "nodeName": standby_apic_name,
                "controllerType": "physical",
                "nodeId": standby_apic_node_id,
                "serialNumber": standby_apic_serial_number,
                "podId": standby_apic_pod_id,
                "standby": True,
                "cimc": {
                    "address4": standby_apic_cimc_ip,
                    "username": standby_apic_cimc_user,
                    "password": standby_apic_cimc_pwd
                    },
                    "oobNetwork": {
                        "address4": standby_apic_oob_ip,
                        "gateway4": standby_apic_oob_gw,
                        "enableIPv4": True
                        }
                    }
                ]
            }
    r_post = requests.post(url, json=body, cookies=cookie, verify=False)
    if r_post.status_code == 200:
        print("\nStandby APIC added successfully!")
        print("\nOpen the APIC GUI and verify the Standby controller status. Standby APIC status shows as Booting Up")
        print("\nGo to System -> Controllers -> expand APIC node -> select 'Cluster As Seen By Node'")
    else:
        print("\nFailed to add Standby APIC:\n")
        print(json.dumps(r_post.json(), indent=4))
        exit(1)



# TODO: Work in progress: add function to check if cookie is expired and get new token if expired. Cookie expires after 10 minutes (600 seconds).
# def check_cookie_expiration(cookie_file):
#     '''Function to check if cookie is expired'''
#     with open(f'./{cookie_file}', 'r') as f:
#         cookie_data = json.load(f)
#         creationTime = cookie_data['creationTime']
#         current_time = int(time())
#         if current_time >= creationTime + 600:
#             return True
#         else:
#             return False


# Runtime

# Import APIC vars
apic_vars = yaml_to_json("apic.yaml")
apic_ip = apic_vars['apic_ip']
apic_user = apic_vars['apic_user']
apic_pwd = apic_vars['apic_pwd']
BASE_URL = 'https://' + apic_ip + '/api'

# Import Standby APIC CIMC vars
standby_apic_vars = yaml_to_json("apic_standby.yaml")
standby_apic_cimc_ip = standby_apic_vars['standby_apic_cimc_ip']
standby_apic_cimc_user = standby_apic_vars['standby_apic_cimc_user']
standby_apic_cimc_pwd = standby_apic_vars['standby_apic_cimc_pwd']
standby_apic_name = standby_apic_vars['standby_apic_name']
standby_apic_node_id = standby_apic_vars['standby_apic_node_id']
standby_apic_admin_pwd = standby_apic_vars['standby_apic_admin_pwd']
standby_apic_oob_ip = standby_apic_vars['standby_apic_oob_ip']
standby_apic_oob_gw = standby_apic_vars['standby_apic_oob_gw']
standby_apic_pod_id = standby_apic_vars['standby_apic_pod_id']

# Save cookie vars
cookie, cookie_file = get_apic_token(BASE_URL, apic_user, apic_pwd)

# Write cookie to file for future use. Cookie expires after 10 minutes (600 seconds).
write_json_to_file(cookie_file, "cookie.json")

# Make a post request for CIMC validation and get server serial number
print("\nCIMC credential validation in progress...\n")
standby_apic_serial_number = check_cimc_validation(apic_ip, cookie, standby_apic_cimc_ip, standby_apic_cimc_user, standby_apic_cimc_pwd)

# If CIMC validation is successful, make a post request to add standby APIC to existing APIC cluster
print(f"\nAdding Standby APIC with serial number {standby_apic_serial_number} to existing APIC cluster...\n")
add_standby_apic(apic_ip, cookie, 
                 standby_apic_name, 
                 standby_apic_node_id,
                 standby_apic_admin_pwd, 
                 standby_apic_cimc_ip, 
                 standby_apic_cimc_user, 
                 standby_apic_cimc_pwd, 
                 standby_apic_pod_id, 
                 standby_apic_oob_ip, 
                 standby_apic_oob_gw,
                 standby_apic_serial_number)
