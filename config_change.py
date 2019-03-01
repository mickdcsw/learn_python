from netmiko import Netmiko
from getpass import getpass

CSR1 = {
    "host": "10.104.15.36",
    "username": "admin",
    "password": getpass(),
    "device_type": "cisco_ios_ssh",
    "secret": "gam30n"
}

line_vty = ["line vty 0 15", "transport input telnet ssh"]
domain_name = ["ip domain-name durlab.local"]

net_connect = Netmiko(**CSR1)

net_connect.enable()

print()
print(net_connect.find_prompt())
output = net_connect.send_config_set(line_vty)
output += net_connect.send_config_set(domain_name)
output += net_connect.save_config()
print(output, "\n")

net_connect.config_mode()
keyout = net_connect.send_command_timing("crypto key generate rsa")
if "yes/no" in keyout:
    keyout += net_connect.send_command_timing("y")
    if "modulus" in keyout:
        keyout += net_connect.send_command_timing("2048", strip_command=False)
elif "modulus" in keyout:
    keyout += net_connect.send_command_timing("2048", strip_command=False)

net_connect.disconnect()

print(keyout)
print()
