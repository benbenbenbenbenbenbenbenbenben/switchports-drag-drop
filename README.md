# Meraki Switchport Drag & Drop 

Web App to easily configure switchports using premade port profiles. This uses Python Flask for backend with simple JSON file to store profiles. Front End uses native JS for drag and drop functionality and Bootstrap for styling.  


## Table of Contents
- [Examples](#examples)
- [Setup](#setup)
- [Profile Example JSON](#profile-example-json)

## Usage
Pass any serial number that your API key has access to - https://switchports-drag-drop-s7rhepsyzq-ey.a.run.app/Q2EW-ATJ2-QFN3.

App will get switchports and check for existing profiles.

Select and drag a profile and drop on a port.

Click save button to update changes.


## Demo Examples
https://switchports-drag-drop-s7rhepsyzq-ey.a.run.app/
- [8 Port Switch]()
- [24 Port Switch](https://switchports-drag-drop-s7rhepsyzq-ey.a.run.app/)
- [48 Port Switch]()

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
static/profiles.json
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
