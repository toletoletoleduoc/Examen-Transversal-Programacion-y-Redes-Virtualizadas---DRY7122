solicita_vlan = int(input('Ingrese su número de puerto: '))

if solicita_vlan >= 1 and solicita_vlan <= 1005:
    print(f'--- Su vlan número {solicita_vlan} corresponde al rango normal de VLANs (1-1005) ---')

elif solicita_vlan >= 1006 and solicita_vlan <= 4094:
    print(f'--- Su vlan número {solicita_vlan} corresponde al rango extendido de VLANs (1006-4094) ---')

else:
    print(f'--- El número {solicita_vlan} no corresponde a ningún rango de VLANs válido ---')