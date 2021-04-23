#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, request, render_template
import meraki
import json
import functools
import time

#----------------------------------------------------------------------------#
# App Config
#----------------------------------------------------------------------------#

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

# 404
@app.errorhandler(404)
def page_not_found(error):
   return render_template('base.html', app_title=app_title, contents='404.html', serial='Alakazam!'), 404

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
# Launch
#----------------------------------------------------------------------------#

# Debug:
# if __name__ == "__main__":
#     app.run(debug=True, port=5001)

# Or specify port manually:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

