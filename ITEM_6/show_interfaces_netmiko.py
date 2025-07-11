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
output1 = net_connect.send_command('show ip int bri')
output2 = net_connect.send_command('show ipv6 int bri')
print('--- INICIO DE PROGRAMA NETMIKO ---\n')
print(output1, '\n\n------------------------\n\n', output2)
print('\n\n--- FIN DE PROGRAMA NETMIKO ---\n\n')
net_connect.disconnect()
