#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, request, render_template
import meraki
import json
import functools
import time
import os


#----------------------------------------------------------------------------#
# App Config
#----------------------------------------------------------------------------#
org_id = os.getenv('ORG_ID')
app = Flask(__name__)
app_title = 'Switch Drag & Drop'
# Instantiate a Meraki dashboard API session
m = meraki.DashboardAPI(
    api_key='',
    base_url='https://api.meraki.com/api/v1/',
    output_log=False,
    # log_file_prefix=os.path.basename(__file__)[:-3],
    # log_path='',
    print_console=False
)

#----------------------------------------------------------------------------#
# Decorators
#----------------------------------------------------------------------------#

# API Wait Timer
def slow_down(_func=None, *, rate=1):
    """Sleep given amount of seconds before calling the function"""
    def decorator_slow_down(func):
        @functools.wraps(func)
        def wrapper_slow_down(*args, **kwargs):
            time.sleep(rate)
            return func(*args, **kwargs)
        return wrapper_slow_down

    if _func is None:
        return decorator_slow_down
    else:
        return decorator_slow_down(_func)
#----------------------------------------------------------------------------#
# Functions
#----------------------------------------------------------------------------#

# Read JSON File
def read_json_file(file):
    try:
        with open(f'static/{file}.json') as f:
            return json.load(f)
    except OSError as e: 
        print(e)
        return False

# Get Profile
def get_profile(profiles, profile):
    for p in profiles:
        if p["name"].lower() == profile.lower():
            port_params = ['name', 'tags', 'enabled', 'type', 'vlan', 'voiceVlan', 'allowedVlans', 'poeEnabled', 'isolationEnabled', 'rstpEnabled', 'stpGuard', 'linkNegotiation', 'portScheduleId', 'udld', 'accessPolicyType', 'accessPolicyNumber', 'macAllowList', 'stickyMacAllowList', 'stickyMacAllowListLimit', 'stormControlEnabled', 'flexibleStackingEnabled', ]
            payload = {k.strip(): v for k, v in p.items() if k.strip() in port_params}
            return payload

# Get Ports
def get_ports(serial):
    try:
        ports = m.switch.getDeviceSwitchPorts(serial)
    except meraki.APIError as e:
        print(f'Meraki API error: {e}')
        print(f'status code = {e.status}')
        print(f'reason = {e.reason}')
        print(f'error = {e.message}')
    except Exception as e:
        print(f'some other error: {e}')
    return ports

# Get Switch
def get_switch(serial):
    try:
        switch = m.devices.getDevice(serial)
    except meraki.APIError as e:
        print(f'Meraki API error: {e}')
        print(f'status code = {e.status}')
        print(f'reason = {e.reason}')
        print(f'error = {e.message}')
    except Exception as e:
        print(f'some other error: {e}')
    return switch
    
#----------------------------------------------------------------------------#
# Action Batch
#----------------------------------------------------------------------------#

def run_an_action_batch(org_id, actions_list, synchronous=False):
	# Create and run an action batch
	batch_response = m.organizations.createOrganizationActionBatch(
		organizationId=org_id,
		actions=actions_list,
		confirmed=True,
		synchronous=synchronous
	)

	return batch_response


def action_switch_port_data(**kwargs):
    body_params = ['name', 'tags', 'enabled', 'type', 'vlan', 'voiceVlan', 'allowedVlans', 'poeEnabled', 'isolationEnabled', 'rstpEnabled', 'stpGuard', 'linkNegotiation', 'portScheduleId', 'udld', 'accessPolicyType', 'accessPolicyNumber', 'macAllowList', 'stickyMacAllowList', 'stickyMacAllowListLimit', 'stormControlEnabled', 'adaptivePolicyGroupId', 'peerSgtCapable', 'flexibleStackingEnabled', ]
    payload = {k.strip(): v for k, v in kwargs.items() if k.strip() in body_params}
    return payload


def create_single_upgrade_action(serial, portId, data):
	# Create a single action
	# AB component parts, rename action
	resource = f'/devices/{serial}/switch/ports/{portId}'
	operation = 'update'
	action = {
		"resource": resource,
		"operation": operation,
		"body": data
	}
	return action

def create_action_list(serial, ports, profiles):
	# Creates a list of actions and returns it
	# Iterate through the list of ports and create an action for each, then collect it
	list_of_actions = list()

	for port in ports:
		profile = get_profile(profiles, port[1])
		if profile["name"].lower() == "reset":
			profile["name"] = ""
		portData = action_switch_port_data(**profile)
		# Create the action
		single_action = create_single_upgrade_action(serial, port[0], portData)
		list_of_actions.append(single_action)

	return list_of_actions

#----------------------------------------------------------------------------#
# Controllers
#----------------------------------------------------------------------------#

# Main Page
@app.route('/<serial>', methods=["GET"])
def switch(serial):
    # Get Switch
    try:
        switch = get_switch(serial)
    except:
        return render_template('base.html', app_title=app_title, contents='404.html', serial=serial)
    # Get Switchports
    try:
        ports = get_ports(serial)
    except:
        return render_template('base.html', app_title=app_title, contents='404.html', serial=serial)
    # Get Profiles
    profiles = read_json_file('profiles')
    return render_template('base.html', app_title=app_title, contents='switch.html', profiles=profiles, ports=ports, serial=serial, switch=switch)

# Ports
@slow_down(rate=0.25)
@app.route('/ports', methods=["PUT"])
def ports():
    # Update Port
    if request.method == "PUT":
        # URL Params
        serial = request.args.get('serial')
        port = request.args.get('port')
        profileName = request.args.get('profile')
        # Get Port Profiles
        profilesJSON = read_json_file('profiles')
        profile = get_profile(profilesJSON, profileName)
        if profile["name"].lower() == "reset":
            profile["name"] = ""
        try:
            updatePort = m.switch.updateDeviceSwitchPort(serial, port, **profile)
            return json.dumps(updatePort)
        except meraki.APIError as e:
            print(f'Meraki API error: {e}')
            print(f'status code = {e.status}')
            print(f'reason = {e.reason}')
            print(f'error = {e.message}')
            return f'reason = {e.reason}'
        except Exception as e:
            print(f'some other error: {e}')
            return f'reason = {e}'

@app.route('/updatePorts', methods=["PUT"])
def updatePorts():
	# Update Port
	if request.method == "PUT":
		data = request.json
		
		actions_list = create_action_list(
			data['serial'],
			data['ports'], 
			read_json_file('profiles')
		)
		result = run_an_action_batch(org_id, actions_list, synchronous=False)
		return {'success':True}


# 404
@app.errorhandler(404)
def page_not_found(error):
   return render_template('base.html', app_title=app_title, contents='404.html', serial='Alakazam!'), 404



#----------------------------------------------------------------------------#
# Launch
#----------------------------------------------------------------------------#

# Debug:
# if __name__ == "__main__":
#     app.run(debug=True, port=5001)

# Or specify port manually:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    app.run(host='0.0.0.0', port=port)

