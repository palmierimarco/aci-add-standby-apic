### Introduction

This script makes it easy to add an APIC standby node using Python in the Application Centric Infrastructure (ACI) 6.x release, as an alternative to Postman as described in this [Cisco document](https://www.cisco.com/c/en/us/support/docs/cloud-systems-management/application-policy-infrastructure-controller-apic/224101-configure-a-standby-node-in-cisco-aci.html). This procedure is necessary as a workaround for this [BUG](https://bst.cloudapps.cisco.com/bugsearch/bug/CSCwo01130).

---

### Requirements

- Cisco APIC working cluster
- Cisco APIC standby server (1 or more)
- Workstation with Python 3.12+ installed.
- Python packages listed in `requirements.txt`:

  ```bash
  pip install -r requirements.txt
  ```

### Files in this repository

- `aci-add-standby-apic.py` : Main script that performs the API calls to add the standby node.
- `apic.yaml` : Primary APIC connection and credential configuration (edit to match your environment).
- `apic_standby.yaml` : Standby node configuration details used by the script (edit to match your environment).
- `cookie.json` : Session cookie file created/used by the script to persist APIC session (not yet implemented in this script).

### How the script works

- Reads configuration from `apic.yaml` and `apic_standby.yaml`.
- Authenticates to the primary working APIC.
- Sends the required API calls to add the standby node as defined in the standby YAML.
- Reports success or errors to the console.

### Configuration

- Update file `apic.yaml` with the primary APIC IP/hostname, username, and password.
- Update file `apic_standby.yaml` with the standby node IP/hostname and any required attributes.
> NOTE: All parameters are mandatory

### Usage

- Run the script directly with Python:

  ```bash
  python aci-add-standby-apic.py
  ```

### Notes & Troubleshooting

- Tested with Cisco ACI software version 6.0(9e)
- Make sure the APIC servers can reach the standby APIC's CIMC via ssh over the Out of Band network.
- This is intended for ACI 6.x as a workaround referenced in the this [Cisco document](https://www.cisco.com/c/en/us/support/docs/cloud-systems-management/application-policy-infrastructure-controller-apic/224101-configure-a-standby-node-in-cisco-aci.html)
- Inspect API responses printed by the script for hints when operations fail.

---

### Diagram

![diagram](diagram.jpg)

---
