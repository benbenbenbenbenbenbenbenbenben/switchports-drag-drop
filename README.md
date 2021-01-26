# Meraki Switchport Drag & Drop 

Web App to easily configure switchports using premade port profiles. This uses Python Flask for backend with simple JSON file to store profiles. Front End uses native JS for drag and drop functionality and Bootstrap for styling.  

## Table of Contents
- [Examples](#examples)
- [Setup](#setup)
- [Profile Example JSON](#profile-example-json)


## Examples
- [8 Port Switch](/QBSB-S48U-VH7E)
- [24 Port Switch](/Q2EW-ATJ2-QFN3)
- [48 Port Switch](/QBSB-AU53-GZLN)

![Image of App](https://github.com/benbenbenbenbenbenbenbenbenben/switchports-drag-drop/blob/main/page.png?raw=true)

![Gif of App](https://github.com/benbenbenbenbenbenbenbenbenben/switchports-drag-drop/blob/main/demo.gif?raw=true)

## Setup
1. Ensure you have Python version 3 installed (If not download and install)
```bash
python3 -V
```
2. Create a Python 3 virtual environment
```bash
python3 -m venv meraki-venv
cd meraki-venv/
source bin/activate
```
3. Clone Github Repository
```bash
git clone https://github.com/benbenbenbenbenbenbenbenbenben/switchports-drag-drop.git
cd switchports-drag-drop/
```
4. Install project requirements into the virtual environment
```bash
pip install -r requirements.txt
```
5. Add Your Meraki API Key To Env Variables
```bash
export MERAKI_DASHBOARD_API_KEY=YOUR_API_KEY
```
6. Run the App
```bash
python app.py
```

## Profile Example JSON
Required keys for app are name, icon, hex. All other params are optional for port config- https://developer.cisco.com/meraki/api-v1/#!update-device-switch-port
```json
[
    {
        "name": "Wifi",
        "tags": ["wifi","profile"],
        "enabled": true,
        "poeEnabled": true,
        "type": "trunk",
        "vlan": "2",
        "icon": "wifi",
        "hex": "#57cc99"
    }
]
```