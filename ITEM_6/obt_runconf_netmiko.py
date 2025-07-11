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
output = net_connect.send_command('show running-config')
print(output)
net_connect.disconnect()
