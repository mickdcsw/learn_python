
# Import argv to call csv file like 'python script.py devices.csv'
from sys import argv

from netmiko import Netmiko

# Import csv module to open and parse csv file
import csv

# Import getpass so password can be entered from prompt
import getpass

# Here we set what two variables we are going to put in the command line.
# 1st is always 'script' and then you can define as many as you want
script, csv_file = argv

# Now we want to define an object that contains our parsed csv file.
# We open the file with 'rb' tag (read binary) to ensure we get no funk formatting
reader = csv.DictReader(open(csv_file))

device_list = []

#takes our object we created from the parsed csv and makes a dict from each line
for line in reader:
    device_list.append(line)

print(device_list)
# Prompt for login credentials
username = input("Username? ")
password = getpass.getpass("Password? ")
enablepw = getpass.getpass("Enable Password? ")

#this is the block most of your code will go. This is to loop through every dictionary in the list
for device in device_list:

    #create a heading so if there are multiple devices, you know what the output is for
    print( "\n\n----------------------\nDevice: {0}\n----------------------\n".format(device['host']))

    # Use try so the the script won't fail if a device is not reachable
    try:
        #we need to set the various options Netmiko is expecting.
        #We use the variables we got from the user earlier
        device['device_type'] = 'cisco_ios_ssh'
        device['username'] = username
        device['password'] = password
        device['secret'] = enablepw
        #This command is when we are attempting to connect. If it fails, it will move on to the except block below
        net_connect = Netmiko(**device)
    except:
        #here we are saying "if ssh failed, TRY telnet"
        try:
            #same as before, but using the 'telnet' device type
            device['device_type'] = 'cisco_ios_telnet'
            device['username'] = username
            device['password'] = password
            device['secret'] = enablepw
            net_connect = Netmiko(**device)
        except:
            #this is the catch all except, if NOTHING works, tell the user and continue onto the next item in the for loop.
            print( "Unable to connect!")
            continue

    #breaking out of the "try" block, we now want to take the session into "enable mode" if it is not already
    net_connect.enable()

    #just printing a blank line. I like formatting the output neatly.
    print( "\n")

    #Now to run a command and do checks on the output.
    output = net_connect.send_command("show run | begin line vty")

    #we want to split the output into individual lines and find specific lines.
    for line in output.splitlines():
        #if we find the following string in the line, we are going to print the line
        if "vty" in line:
            print( "     " + line)
        elif "transport" in line:
            print ( "     " + line)
