from netmiko import ConnectHandler

# --- Información del dispositivo ---
CSR1000v = {
    'device_type': 'cisco_xe',
    'host': '192.168.56.102',
    'username': 'cisco', 
    'password': 'cisco123!',
    'port': 22,
}

net_connect = ConnectHandler(**CSR1000v)
net_connect.send_config_from_file(config_file="comandosparaeigrp.txt")
output = net_connect.send_command('show running-config | section eigrp')
print(output)
net_connect.disconnect()
