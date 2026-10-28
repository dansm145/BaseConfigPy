# Writes a basic Cisco switch/router config to a .txt file
# MK1 (hostname) and Morgenkrydder1 (banner message) are user inputs

def main():
    hostname = input("Enter hostname (e.g. MK1): ").strip()
    banner_message = input("Enter banner message (e.g. Morgenkrydder1): ").strip()


    config = f"""!basic config
enable
conf t 
hostname {hostname} 
enable secret class
service password-encryption
login
banner motd "{banner_message}" 
no ip domain-lookup

line console 0
password cisco
login
exec-timeout 2

line vty 0 15
password CiscoSux
exec timeout 3

!interface vlan 1
!ip address 192.168.40.75 255.255.255.0 
!description Morgenkrydder 2 forbindelsen til PC
!no shutdown

exit
default-gateway 192.168.40.1

"""

    filename = f"{hostname}_config.txt"

    with open(filename, "w") as file:
        file.write(config)

    print(f"Config written to {filename}")

if __name__ == "__main__":
    main()