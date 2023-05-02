# Dynamic DNS Update Client (DUC)

## Audience

This repository is for **developers** who would like to extend the DDNS Update Client offered by Same Day Rules. Same Day Rules **customers** would not normally need access to the source code underlying the DDNS Update Client operation; they would instead download and install the update client from the [Same Day Rules website](https://samedayrules.com/) for the operating system of their choice.

## Overview

This repository holds software for the Dynamic Domain Name System (DDNS) Update Client (DUC) that is used to configure and start dynamic updates of hostnames and their associated IP addresses. The update client is integrated with the [DDNS service provided by Same Day Rules](https://samedayrules.com/using-a-dynamic-domain-name-system-ddns-service/).

DDNS services allow users to create customized names that can be used to access home network resources using standard URL's from the Internet. With DDNS, a user can create a custom domain name (e.g., myiot.samedayrules.net) that is associated with the IP address of their home network gateway (e.g., broadband cable modem). If the IP address of the home network gateway changes, special software running on the home network updates the customized name to point to the new IP address so that the customized name remains current. The special software running on the home network is called a DDNS Update Client or DUC, and that software is held in this repository.

The DDNS Update Client (DUC) interacts with a DDNS server to propagate changes in IP address settings to names held in the Internet Domain Name System. The Same Day Rules DUC interacts with the Same Day Rules DDNS server at **ht<span>tps://</span>samedayrules.net** using a standard DDNS API that is compatible with the [Dyn DNS standard](https://help.dyn.com/remote-access-api/).

Users can subscribe to the Same Day Rules DDNS Service at our [storefront](https://samedayrules.com/product/dynamic-domain-name-service/).

## KivyMD Application

The Same Day Rules DUC is provided as a Python [KivyMD](https://kivymd.readthedocs.io/en/1.1.1/) application that is packaged using [PyInstaller](https://pyinstaller.org/en/stable/) for use on multiple platforms (i.e., Windows, Linux, Mac OS).

## Using PyInstaller

https://pyinstaller.org/en/stable/usage.html#using-pyinstaller

### Supporting Multiple Python Environments

https://pyinstaller.org/en/stable/usage.html#supporting-multiple-python-environments

### Windows And Mac Os X Specific Options

https://pyinstaller.org/en/stable/usage.html#windows-and-mac-os-x-specific-options

### Using PyInstaller to Easily Distribute Python Applications

https://realpython.com/pyinstaller-python/

### Programming Guide » Create a Package for Windows

https://kivy.org/doc/stable/guide/packaging-windows.html?highlight=pyinstaller#create-a-package-for-windows

### KivyMD PyInstaller Hooks

https://kivymd.readthedocs.io/en/0.104.1/unincluded/kivymd/tools/packaging/pyinstaller/index.html

### Kivy to one exe can't find kv file

https://stackoverflow.com/questions/62019124/kivy-to-one-exe-cant-find-kv-file

### Command to Create Onefile Distrubution

pyinstaller --onefile --add-data "ddnsupdate.kv;." ddnsupdate.pyw
