'''
Same Day Rules Dynamic Domain Name System Update Client
(SDR DDNS Update Client - DUC)

Python Kivy/KivyMD-based GUI that allows the user to input parameters
to control the SDR DUC. Once parameters are successfully applied, the
DUC periodically updates the IP address of the spcified host by calling
the SDR DDNS API that then updates the DNS tables for the SDR IoT domain
(samedayrules.net).

DDNS hostnames are managed (added, modified, deleted) on the Same Day Rules
store front at: https://samedayrules.com

The DUC application must be running (in the foreground) in order to make
periodic updates. See the following Same Day Rules blog post for more
information: https://samedayrules.com/using-a-dynamic-domain-name-system-ddns-service/
'''

TITLE = 'SDR DUC v1.0'

CONFIG_FILENAME = 'ddnsupdate.cfg'
ICON_FILENAME = 'favicon.ico'

# Prevent Kivy leaving debug messages
# https://stackoverflow.com/questions/50308757/prevent-kivy-leaving-debug-messages
import os
os.environ['KIVY_NO_CONSOLELOG'] = '1'

# How to change [Kivy] window size
# https://stackoverflow.com/questions/14014955/kivy-how-to-change-window-size
# Available configuration tokens
# https://kivy.org/doc/stable/api-kivy.config.html?highlight=config#available-configuration-tokens
from kivy import Config
Config.set('graphics', 'fullscreen', '0')
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '680')
Config.set('graphics', 'resizable', False)
Config.set('kivy', 'window_icon', ICON_FILENAME)

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.resources import resource_add_path

from kivymd.app import MDApp

import sys
import base64
import json
import socket
import string
import requests
import threading
import ipaddress
import time as ttime
from datetime import datetime

# Helper functions - colors are specified as fractional RGB[A] values
rgba = lambda x: x/255

# Retrieve the IP of the local machine
def my_local_ip():
    try:
        my_ip = socket.gethostbyname(socket.gethostname())
    except Exception as ex:
        my_ip = 'unknown'
        Logger.error('Exception getting my local IP address: ' + str(ex))
    return my_ip

# Query the outside world to retrieve the public-facing IP address of the machine
def my_public_ip():
    try:
        response = requests.get('https://samedayrules.net/myip')
        if response.status_code == 200:
            my_ip = str(response.text)
        else:
            my_ip = 'unknown'
    except Exception as ex:
        my_ip = 'unknown'
        Logger.error('Exception getting my public IP address: ' + str(ex))
    return my_ip

# Generate the base-64 encoding of the user_name/access_key pair for the DDNS API
def base64_encode(user_name, access_key):
    input_string = user_name + ':' + access_key
    input_string_bytes = input_string.encode('utf-8')
    base64_bytes = base64.b64encode(input_string_bytes)
    return base64_bytes.decode('ascii')

# Default update rate for the DDNS Update Client (DUC)
DEF_UPDATE_PERIOD = 60.0 # sec

# DDNS update client class that manages updates to the DDNS service
class DDNSUpdateClient(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.user_name = ''
        self.access_key = ''
        self.hostname = ''
        self.ip_address = ''
        self.update_period = DEF_UPDATE_PERIOD
        self.last_srv_update = datetime(1, 1, 1, 0, 0)
        self.last_srv_status = 'unknown'
        self.configured = False

    def stop(self):
        self.stop_event.set()

    def stopped(self):
        return self.stop_event.is_set()

    def configure(self, user_name, access_key, hostname, ip_address, update_period):
        # Assume failure
        success = False
        # Parameters must have been validated - trusting values
        self.lock.acquire() # control access to public vars
        try:
            self.user_name = user_name
            self.access_key = access_key
            self.hostname = hostname
            self.ip_address = ip_address
            self.update_period = update_period
            self.configured = True
            success = True
        except Exception as ex:
            self.last_srv_status = 'error'
            Logger.error('Exception configuring DDNS settings: ' + str(ex))
        self.lock.release()
        return success

    def update(self):
        if self.configured:
            self.lock.acquire() # control access to public vars
            Logger.info('DDNS Update Client making request')
            try:
                auth = base64_encode(self.user_name, self.access_key)
                url = 'https://samedayrules.net/api/v1/nic/update'
                headers = {
                    'User-Agent': 'SameDayRules - DDNS Update Client - 1.0',
                    'Authorization': 'Basic {}'.format(auth)}
                params = {'hostname': self.hostname, 'myip': self.ip_address}
                response = requests.get(url=url, headers=headers, params=params)
                if response.status_code == 200:
                    self.last_srv_status = str(response.text).strip()
                    self.last_srv_update = datetime.now()
                else:
                    self.last_srv_status = 'unknown'
            except Exception as ex:
                self.last_srv_status = 'error'
                Logger.error('Exception updating DDNS settings: ' + str(ex))
            self.lock.release()

    def run(self):
        while not self.stopped():
            try:
                self.update()
            except Exception as ex:
                Logger.error('Exception running thread: ' + str(ex))
            ttime.sleep(self.update_period)

# User input field validators
RESERVED_LABELS = []
RESERVED_FQDNS = ['samedayrules.com.', 'samedayrules.net.']
RESERVED_IPS = ['144.208.66.36', '209.182.193.230', '192.249.114.148', '209.182.194.166']

MAX_LABEL_LEN = 63
MAX_DOMAIN_LEN = 255

VALID_LABEL_CHARS = set(string.ascii_letters + string.digits + '-')
VALID_USER_NAME_CHARS = set(string.ascii_letters + string.digits + '-' + '_')

def valid_label(label):
    # Ignoring upper/lower case chars
    # Can't be blank or non-string
    if label is None or type(label) != str:
        return False
    # Remove whitespace
    label = label.strip()
    # Check length bounds
    if len(label) == 0 or len(label) > MAX_LABEL_LEN:
        return False
    # Can't have beginnig/trailing '-'
    if label[0] == '-' or label[-1] == '-':
        return False
    # Check for valid chars
    if not all(c in VALID_LABEL_CHARS for c in label):
        return False
    # Can't be one of our reserved labels
    if label.lower() in RESERVED_LABELS:
        return False
    return True

def valid_domain_name(name, fqdn = False, level = 2):
    # Can't be blank or non-string
    if name is None or type(name) != str:
        return False
    # Remove whitespace
    name = name.strip()
    # Check length bounds
    if len(name) == 0 or len(name) > MAX_DOMAIN_LEN:
        return False
    # Can't be one of our reserved FQDNs - check before split()
    if name.lower() in RESERVED_FQDNS:
        return False
    # If FQDN, then it must end in a period
    # Remove the period or split() won't work
    if fqdn:
        if name[-1] != '.':
            return False
        else:
            name = name[:-1]
    # Split the domain name into parts
    # Must have at least 'level' number of parts
    parts = name.split('.')
    num_parts = len(parts)
    if num_parts < level:
        return False
    # Length of last part (TLD) must be >= 2
    tld = parts[-1]
    if len(tld) < 2:
        return False
    # Last part must only contain a-z
    if not tld.isalpha():
        return False
    # Remaining parts must be valid labels
    for p in range(0, num_parts-1):
        if not valid_label(parts[p]):
            return False
    return True

ACCESS_KEY_SIZE = 32

def valid_access_key(access_key):
    try:
        if len(access_key) == ACCESS_KEY_SIZE:
            return True
    except:
        pass
    return False

def valid_ip_address(ip, v4v6 = '?'):
    # Can't be one of our reserved IPs
    if ip.lower() in RESERVED_IPS:
        return False
    # The ipaddress module does all the work...
    try:
        if v4v6.upper() == 'V4':
            ipv4 = ipaddress.IPv4Address(ip)
            return True
        elif v4v6.upper() == 'V6':
            ipv6 = ipaddress.IPv6Address(ip)
            return True
        else:
            # Not sure which type - try v4 then v6
            try:
                ipv4 = ipaddress.IPv4Address(ip)
                return True
            except:
                pass
            try:
                ipv6 = ipaddress.IPv6Address(ip)
                return True
            except:
                pass
    except:
        pass
    return False

MIN_USER_NAME_SIZE = 5
MAX_USER_NAME_SIZE = 60

def valid_user_name(user_name):
    try:
        if not all(c in VALID_USER_NAME_CHARS for c in user_name):
            return False
        if len(user_name) >= MIN_USER_NAME_SIZE and len(user_name) <= MAX_USER_NAME_SIZE:
            return True
    except:
        pass
    return False

MIN_UPDATE_PERIOD = 30 # sec
MAX_UPDATE_PERIOD = 86400 # one day

def valid_update_period(period):
    try:
        if period >= MIN_UPDATE_PERIOD and period <= MAX_UPDATE_PERIOD:
            return True
    except:
        pass
    return False

def to_int(str):
    try:
        x = int(str)
    except:
        x = None
    return x

# Class to manage loading/saving local DDNS configuration settings
class DDNSConfig():
    def __init__(self):
        self.user_name = ''
        self.access_key = ''
        self.hostname = ''
        self.public_ip_address_active = False
        self.local_ip_address_active = False
        self.other_ip_address_active = False
        self.other_ip_address = ''
        self.ip_address = ''
        self.update_period = ''
        self.loaded = False

    # Load configuration file if present - file is JSON encoded
    def load(self, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                # Assume success
                success = True
                # Validate before storing
                user_name = data.get('user_name')
                access_key = data.get('access_key')
                hostname = data.get('hostname')
                update_period = data.get('update_period')
                other_ip_address = data.get('other_ip_address')
                public_ip_active = data.get('public_ip_address_active')
                local_ip_active = data.get('local_ip_address_active')
                other_ip_active = data.get('other_ip_address_active')
                if valid_user_name(user_name):
                    self.user_name = user_name
                else:
                    success = False
                if valid_access_key(access_key):
                    self.access_key = access_key
                else:
                    success = False
                if valid_domain_name(hostname, level=3):
                    self.hostname = hostname
                else:
                    success = False
                if valid_update_period(update_period):				
                    self.update_period = update_period
                else:
                    success = False
                # Handle IP address differently due to checkboxes
                if public_ip_active:
                    self.public_ip_address_active = True
                    self.ip_address = my_public_ip
                elif local_ip_active:
                    self.local_ip_address_active = True
                    self.ip_address = my_local_ip
                elif other_ip_active:
                    if valid_ip_address(other_ip_address):
                        self.other_ip_address_active = True
                        self.ip_address = other_ip_address
                    else:
                        success = False
                # Set other_ip_address (will get re-validated when user submits)
                self.other_ip_address = other_ip_address
                if success:
                    self.loaded = True
                    # Object as dict is returned on success
                    return data				
        except:
            pass
        return None

    # Save configuration file - file is JSON encoded
    def save(self, filename):
        try:
            with open(filename, 'w') as f:
                data = {
                    "user_name": self.user_name,
                    "access_key": self.access_key,
                    "hostname": self.hostname,
                    "update_period": self.update_period,
                    "other_ip_address": self.other_ip_address,
                    "public_ip_address_active": self.public_ip_address_active,
                    "local_ip_address_active": self.local_ip_address_active,
                    "other_ip_address_active": self.other_ip_address_active
                }
                json.dump(data, f)
                # Object as dict is returned on success
                return data				
        except:
            pass
        return None

# Class that manages all interaction with user (via the GUI)
class MainGUI(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = TITLE
        self.gui = None
        self.event = Clock.schedule_interval(self.update_server_status, 5.0)

    def build(self):
        self.theme_cls.theme_style='Light'
        self.gui = Builder.load_file('ddnsupdate.kv')
        self.gui.ids['user_name'].text = ddns_config.user_name
        self.gui.ids['access_key'].text = ddns_config.access_key
        self.gui.ids['hostname'].text = ddns_config.hostname
        self.gui.ids['update_period'].text = str(ddns_config.update_period)
        self.gui.ids['public_ip_address'].text = my_public_ip
        self.gui.ids['local_ip_address'].text = my_local_ip
        self.gui.ids['other_ip_address'].text = ddns_config.other_ip_address
        self.gui.ids['public_ip_address_active'].active = ddns_config.public_ip_address_active
        self.gui.ids['local_ip_address_active'].active = ddns_config.local_ip_address_active
        self.gui.ids['other_ip_address_active'].active = ddns_config.other_ip_address_active
        self.gui.ids['apply_button'].on_press = self.apply_settings
        return self.gui

    def update_server_status(self, dt = 5.0):
        self.gui.ids['last_srv_update'].text = ddns_service.last_srv_update.strftime("%m/%d/%Y %H:%M:%S")
        self.gui.ids['last_srv_status'].text = ddns_service.last_srv_status

    def apply_settings(self):
        try:
            # Assume validation success
            validates = True
            # Extract fields
            user_name = self.gui.ids['user_name'].text
            access_key = self.gui.ids['access_key'].text
            hostname = self.gui.ids['hostname'].text
            update_period = to_int(self.gui.ids['update_period'].text)
            # Determine which IP address is active
            if self.gui.ids['public_ip_address_active'].active:
                ip_address = self.gui.ids['public_ip_address'].text
            elif self.gui.ids['local_ip_address_active'].active:
                ip_address = self.gui.ids['local_ip_address'].text
            elif self.gui.ids['other_ip_address_active'].active:
                ip_address = self.gui.ids['other_ip_address'].text
            else:
                ip_address = my_public_ip
            # Check for required fields
            if not user_name:
                self.gui.ids['user_name'].helper_text = 'This field is required'
                self.gui.ids['user_name'].error = True
                validates = False
            elif not valid_user_name(user_name):
                self.gui.ids['user_name'].helper_text = 'Invalid username'
                self.gui.ids['user_name'].error = True
                validates = False
            if not access_key:
                self.gui.ids['access_key'].helper_text = 'This field is required'
                self.gui.ids['access_key'].error = True
                validates = False
            elif not valid_access_key(access_key):
                self.gui.ids['access_key'].helper_text = 'Invalid access key'
                self.gui.ids['access_key'].error = True
                validates = False
            if not hostname:
                self.gui.ids['hostname'].helper_text = 'This field is required'
                self.gui.ids['hostname'].error = True
                validates = False
            elif not valid_domain_name(hostname, level=3):
                self.gui.ids['hostname'].helper_text = 'Malformed hostname'
                self.gui.ids['hostname'].error = True
                validates = False
            if not valid_ip_address(ip_address):
                self.gui.ids['other_ip_address'].helper_text = 'Invalid IP address'
                self.gui.ids['other_ip_address'].error = True
                validates = False
            if not update_period:
                self.gui.ids['update_period'].helper_text = 'This field is required'
                self.gui.ids['update_period'].error = True
                validates = False
            elif not valid_update_period(update_period):
                self.gui.ids['update_period'].helper_text = 'Outside acceptable range'
                self.gui.ids['update_period'].error = True
                validates = False
            if validates:
                if ddns_service.configure(user_name, access_key, hostname, ip_address, update_period):
                    ddns_service.update()
                    self.event = Clock.schedule_interval(self.update_server_status, update_period)
                    ddns_config.user_name = user_name
                    ddns_config.access_key = access_key
                    ddns_config.hostname = hostname
                    ddns_config.update_period = update_period
                    ddns_config.other_ip_address = self.gui.ids['other_ip_address'].text
                    ddns_config.public_ip_address_active = self.gui.ids['public_ip_address_active'].active
                    ddns_config.local_ip_address_active = self.gui.ids['local_ip_address_active'].active
                    ddns_config.other_ip_address_active = self.gui.ids['other_ip_address_active'].active
                    ddns_config.save(CONFIG_FILENAME)
        except:
            Logger.error('Exception applying settings')

if __name__ == '__main__':
    # Kivy: Bundling Data Files
    # https://kivy.org/doc/stable/guide/packaging-windows.html?highlight=pyinstaller#bundling-data-files
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    # Start update thread now
    ddns_service = DDNSUpdateClient()
    ddns_service.start()
    # Fetch public and local IP addresses
    my_public_ip = my_public_ip()
    my_local_ip = my_local_ip()
    # Load configuration (if it exists)
    ddns_config = DDNSConfig()
    if ddns_config.load(CONFIG_FILENAME):
        # Configure DDNS service with saved data and update
        ddns_service.configure(
            ddns_config.user_name,
            ddns_config.access_key,
            ddns_config.hostname,
            ddns_config.ip_address,
            ddns_config.update_period)
        ddns_service.update()
    # Show the main GUI
    main_gui = MainGUI()
    main_gui.run()
