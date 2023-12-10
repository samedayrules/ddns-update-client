# Dynamic DNS Update Client (DUC)

## Audience

This repository is for **developers** who would like to extend the Dynamic DNS Update Client offered by Same Day Rules. Same Day Rules **customers** would not normally need access to the source code underlying the DDNS Update Client operation; they would instead download and install the update client from the [Same Day Rules website](https://samedayrules.com/) for the operating system of their choice.

## Overview

This repository holds software for the Dynamic Domain Name System (DDNS) Update Client (DUC) that is used to configure and start dynamic updates of hostnames and their associated IP addresses. The update client is integrated with the [DDNS service provided by Same Day Rules](https://samedayrules.com/using-a-dynamic-domain-name-system-ddns-service/).

DDNS services allow users to create customized names that can be used to access home network resources using standard URL's from the Internet. With DDNS, a user can create a custom domain name (e.g., myiot.samedayrules.net) that is associated with the IP address of their home network gateway (e.g., broadband cable modem). If the IP address of the home network gateway changes, special software running on the home network updates the customized name to point to the new IP address so that the customized name remains current. The special software running on the home network is called a DDNS Update Client or DUC, and that software is held in this repository.

The DDNS Update Client (DUC) interacts with a DDNS server to propagate changes in IP address settings to names held in the Internet Domain Name System. The Same Day Rules DUC interacts with the Same Day Rules DDNS server at **ht<span>tps://</span>samedayrules.net** using a standard DDNS API that is compatible with the [Dyn DNS standard](https://help.dyn.com/remote-access-api/).

**Users can subscribe to the Same Day Rules DDNS Service at our [storefront](https://samedayrules.com/product/dynamic-domain-name-service/).**

## KivyMD Application

The Same Day Rules DUC is provided to end-users as a Python [KivyMD](https://kivymd.readthedocs.io/en/1.1.1/) application that is packaged using [PyInstaller](https://pyinstaller.org/en/stable/) for use on multiple platforms (i.e., Windows, Linux, Mac OS).

Developers seeking to install and extend the Same Day Rules DUC can follow the instructions below to clone and then run the DUC under different operating systems.

## Developer Notes
Regarding the Python requirements:
1. `kivy-deps.angle` is only required for Windows.
2. `kivy-deps.angle` is only required for Windows.
 
## Windows: Downloading and Running the DUC

To modify and run the DUC software, you must have:

1. Python installed (version 3.11 used).
2. Python virtual environment module installed (version 20.17.1 used).
3. Git installed (version 2.38.1 used).
4. Access to a command shell (e.g., cmd.exe).

The general process is:

1. Open Windows command prompt.
2. Change to your development directory.
3. Clone the software repository.
4. Make a Python virtual environment.
5. Install the required Python modules.
6. Run the software, either as-needed or upon startup each time you login.

Assuming you have opened a Windows command prompt and you have navigated to your development directory:

`C:>git clone https://github.com/samedayrules/ddns_update_client.git`<br>
`C:>cd ddns_update_client`<br>
`C:>virtualenv venv`<br>
`C:>venv\Scripts\activate`<br>
`(venv) C:>pip install -r requirements.txt`

You should have the most recent copy of the DUC software within the target virtual environment on your machine.

To run the software, simply execute the script:

`(venv) C:>python ddnsupdate.pyw`

The Python DUC application does not output anything to the console window when executed nor does it create a console window when launched.

To make a shortcut to the DUC that can then be executed at startup:

1. Right-click on your Windows desktop, and choose `New > Shortcut`.
2. Browse to the location where the Python DUC application resides.
3. Then browse further to the `venv\Scripts` directory and select the `pythonw.exe` application.
4. Click `Next` in the `Create Shortcut` dialog box.
5. Type a name for the new shortcut, and then select `Finish`.
6. On your Windows desktop, right-click the new shortcut that you just made and select `Properties`.
7. In the `Target` field, append the full path to the Python DUC application.
8. Select `Ok` in the shortcut properties dialog box.

The command in the `Target` field above should look something like this:

`C:\Users\me\ddns_update_client\venv\Scripts\pythonw.exe C:\Users\me\ddns_update_client\ddnsupdate.pyw`

And, you should now be able to launch the DUC from your desktop by double-clicking the shortcut icon. To run the Python DUC application at startup, when you login into Windows, copy the shortcut to your `Startup` directory (or follow [these directions](https://www.dell.com/support/kbdoc/en-us/000124550/how-to-add-app-to-startup-in-windows-10) to copy it to your Windows 10 startup area).

## Using PyInstaller

For developers interested in creating a Python executable that can be shared with other users (who don't necessarily have a Python development environment), you can use the PyInstaller application. Below are various resources that desctribe how to do that.

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

### Command to Create One File Distrubution

To produce a single executeable **file** that is decompressed and run in-place:

`pyinstaller --clean --log-level WARN --onefile --icon favicon.256x256.ico --add-data "ddnsupdate.kv;." ddnsupdate.pyw`

### Command to Create One Folder Distrubution

To create a single **folder** where the executeable Python program will be stored:

`pyinstaller --clean --log-level WARN --onedir --icon favicon.256x256.ico --add-data "ddnsupdate.kv;." ddnsupdate.pyw`

### Manual Changes Required for Kivy

If manual changes are made to the `.spec` file, then run this afterwards:

`pyinstaller --log-level WARN ddnsupdate.spec`

Add these lines if the `.spec` file is changed:

 `-*- mode: python ; coding: utf-8 -*-`<br>
<br>
**`# Fixes for Kivy`<br>**
**`import os`<br>**
**`from kivy_deps import sdl2, glew`<br>**
**`from kivymd import hooks_path as kivymd_hooks_path`<br>**
**`path = os.path.abspath(".")`<br>**
<br>
`block_cipher = None`<br>

`a = Analysis(`<br>
`    ['ddnsupdate.pyw'],`<br>
**`    pathex=[path],`<br>**
`    binaries=[],`<br>
`    datas=[('ddnsupdate.kv', '.')],`<br>
`    hiddenimports=[],`<br>
**`    hookspath=[kivymd_hooks_path],`<br>**

`coll = COLLECT(`<br>
`    exe,`<br>
**`    Tree(path),`<br>**
`    a.binaries,`<br>
`    a.zipfiles,`<br>
`    a.datas,`<br>
**`    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],`<br>**
