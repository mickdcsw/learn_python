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

# Log success and failure
job_report = open("job_report.txt", mode="w")

conn_good = []
conn_fail = []
config_good = []

device_list = []

#takes our object we created from the parsed csv and makes a dict from each line
for line in reader:
    device_list.append(line)

# Prompt for login credentials
username = input("Username? ")
password = getpass.getpass("Password? ")
# enablepw = getpass.getpass("Enable Password? ")

# Define commands
vty_commands = ["line vty 0 15", "transport input telnet ssh"]
global_commands = ["ip ssh version 2", "ip domain-name isus.emc.com"]

#this is the block most of your code will go. This is to loop through every dictionary in the list
for device in device_list:

    #create a heading so if there are multiple devices, you know what the output is for
    print( "\n\n----------------------\nDevice: {0}\n----------------------\n".format(device['host']))

    # Use try so the the script won't fail if a device is not reachable
    try:
        #we need to set the various options Netmiko is expecting.
        #We use the variables we got from the user earlier
        device['device_type'] = 'cisco_ios_telnet'
        device['username'] = username
        device['password'] = password
        device['secret'] = password
        net_connect = Netmiko(**device)
        # conn_good.write(device[0])
        conn_good.append(device['host'])
    except:
        # Report to user if telnet doesn't work
        print("Unable to connect!")
        conn_fail.append(device['host'])
        # conn_fail.write(device[0],"\n")
        continue

    # breaking out of the "try" block, we now want to take the session into "enable mode" if it is not already
    net_connect.enable()

    #just printing a blank line. I like formatting the output neatly.

    print("The prompt is: ",net_connect.find_prompt())
    output = net_connect.send_config_set(vty_commands)
    output += net_connect.send_config_set(global_commands)
    output += net_connect.save_config()
    print(output, "\n")

    net_connect.config_mode()
    keyout = net_connect.send_command_timing("crypto key generate rsa")
    if "yes/no" in keyout:
        keyout += net_connect.send_command_timing("n")
    elif "modulus" in keyout:
        keyout += net_connect.send_command_timing("2048", strip_command=False)
    print(keyout)

    net_connect.disconnect()

    try:
        #we need to set the various options Netmiko is expecting.
        #We use the variables we got from the user earlier
        device['device_type'] = 'cisco_ios_ssh'
        device['username'] = username
        device['password'] = password
        device['secret'] = password
        #This command is when we are attempting to connect. If it fails, it will move on to the except block below
        net_connect = Netmiko(**device)
        config_good.append(device['host'])
    except:
        #here we are saying "if ssh failed, TRY telnet"
        print("\n Failure - Unable to connect via SSH")

    net_connect.disconnect()

print('\n\nConnection Good Devices\n', conn_good)
print('\n\nConnection Failed Devices\n', conn_fail)
print('\n\nCconfiguration Success Devices\n', config_good)

#results = [conn_good, conn_fail, config_good]

#job_report.write(results)
job_report.close()
