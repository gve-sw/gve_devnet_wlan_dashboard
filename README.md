# GVE_DevNet_WLAN_Dashboard
Dashboard to display Meraki Wireless Statistics

## Contacts
* Jorge Banegas (jbanegas@cisco.com)

## Solution Components
* Meraki
* Python 
* HTML
* Javascript

## Installation/Configuration

Edit the Excel file sheet so the first row contains the Meraki network names for each column and the rest of the columns to include the mac address of the client devices to track in the Meraki network 


![/IMAGES/device_file.png](/IMAGES/device_file.png)

If you have not already, generate an API key from your Meraki dashboard 


![/IMAGES/generate_api_key.png](/IMAGES/generate_api_key.png)

Edit the config.py file to include your Meraki API key and Meraki Org ID (https://developer.cisco.com/meraki/api-v1/#!get-organizations)

```python
# insert Meraki key from Dashboard
api_key = ''
meraki_org_id = ''
device_file_path = 'file.xlsx'

```
create virtual environment and name it env, then activate it

```console
foo@bar:~$ virtualenv env
foo@bar:~$ source env/bin/activate
```

4. install the dependencies required for the python script
```console
foo@bar(env):~$ pip install -r requirements.txt
```

5. run python script
```console
foo@bar(env):~$ python main.py
```

# Screenshots
Device Usage Page

![/IMAGES/device_usage.png](/IMAGES/device_usage.png)

Latency Page

![/IMAGES/latency.png](/IMAGES/latency.png)

Network Usage Page

![/IMAGES/network_usage.png](/IMAGES/network_usage.png)



![/IMAGES/0image.png](/IMAGES/0image.png)

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.
