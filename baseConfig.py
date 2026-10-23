# Writes a basic Cisco switch/router config to a .txt file
# MK1 (hostname) and Morgenkrydder1 (banner message) are user inputs

def main():
    hostname = input("Enter hostname (e.g. MK1): ").strip()
    banner_message = input("Enter banner message (e.g. Morgenkrydder1): ").strip()

    config = f"""!basic config
enable
conf t !enter global config layer
hostname {hostname} !skriv navn
enable secret class
service password-encryption
login
banner moto "{banner_message}" !skriv unik banner besked
no ip domain-lookup

"""

    filename = f"{hostname}_config.txt"

    with open(filename, "w") as file:
        file.write(config)

    print(f"Config written to {filename}")

if __name__ == "__main__":
    main()