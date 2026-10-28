# Writes a basic Cisco switch/router config to a .txt file
# Device type (switch/router) and IP version (IPv4/IPv6/both)
# are chosen by the user; follow-up questions depend on the choice.

import ipaddress


def ask_choice(prompt, options):
    """Keep asking until the user picks a valid numbered option."""
    print(prompt)
    for i, option in enumerate(options, start=1):
        print(f"  {i}. {option}")
    while True:
        answer = input(f"Choose 1-{len(options)}: ").strip()
        if answer.isdigit() and 1 <= int(answer) <= len(options):
            return options[int(answer) - 1]
        print("Invalid choice, try again.")


def ask_ip(prompt, version):
    """Keep asking until a valid IPv4/IPv6 address is entered.
    IPv4 accepts: '192.168.1.1/24', '192.168.1.1 255.255.255.0'
    or '192.168.1.1/255.255.255.0'. IPv6 accepts '2001:db8::1/64'.
    Returns an IPv4Interface/IPv6Interface object."""
    while True:
        answer = input(prompt).strip()
        if not answer:
            print("Empty input, try again.")
            continue
        try:
            if version == "ipv4":
                # subnet mask notation with a space -> CIDR-style for parsing
                if " " in answer:
                    answer = answer.replace(" ", "/")
                return ipaddress.IPv4Interface(answer)
            return ipaddress.IPv6Interface(answer)
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError, ValueError) as e:
            print(f"Invalid {version.upper()} address: {e}")
            print(f"Try again, e.g. "
                  f"{'192.168.1.1/24 or 192.168.1.1 255.255.255.0' if version == 'ipv4' else '2001:db8::1/64'}")


def main():
    hostname = input("Enter hostname (e.g. MK1): ").strip()
    banner_message = input("Enter banner message (e.g. Morgenkrydder1): ").strip()

    device_type = ask_choice(
        "Is this device a switch or a router?",
        ["switch", "router"]
    )
    ip_mode = ask_choice(
        "Which IP version(s) should be configured?",
        ["ipv4", "ipv6", "both"]
    )

    # Consecutive questions based on the choices above
    ipv4 = ip_mode in ("ipv4", "both")
    ipv6 = ip_mode in ("ipv6", "both")

    mgmt_vlan = "1"
    if device_type == "switch":
        vlan = input("Enter management VLAN (default 1): ").strip()
        if vlan.isdigit():
            mgmt_vlan = vlan

    # exec-timeout per line layer; typing 0 means the command (and its
    # line section) is not added to the config
    def ask_exec_timeout(layer, with_header=True):
        timeout_min = input(
            f"Enter exec-timeout minutes for {layer} (0 = do not add): ").strip()
        if not (timeout_min.isdigit() and int(timeout_min) > 0):
            return ""
        timeout_sec = input("Enter exec-timeout seconds (default 0): ").strip()
        if not timeout_sec.isdigit():
            timeout_sec = "0"
        line = f" exec-timeout {timeout_min} {timeout_sec}\n"
        if not with_header:
            return line
        return f"line {layer}\n{line}exit\n"

    # console merges into the existing "line console 0" section;
    # vty only appears when a timeout is actually set
    exec_timeout_con = ask_exec_timeout("console 0", with_header=False)
    exec_timeout_vty = ask_exec_timeout("vty 0 4")

    ipv4_config = ""
    ipv6_config = ""

    if ipv4:
        interface = ask_ip(
            "Enter IPv4 address and subnet mask "
            "(e.g. 192.168.1.1/24 or 192.168.1.1 255.255.255.0): ", "ipv4")
        if device_type == "switch":
            ipv4_config = (
                f"interface vlan {mgmt_vlan} \n"
                f" ip address {interface.ip} {interface.netmask}\n"
                f" no shutdown\n"
            )
        else:
            ipv4_config = (
                f"interface gigabitEthernet0/0\n"
                f" ip address {interface.ip} {interface.netmask}\n"
                f" no shutdown\n"
            )

    if ipv6:
        ipv6_interface = ask_ip(
            "Enter IPv6 address with prefix (e.g. 2001:db8::1/64): ", "ipv6")
        if ipv6_interface.ip.is_link_local:
            # Link-local (fe80::/10): Cisco requires the link-local keyword,
            # and a global unicast address is still needed for connectivity.
            ipv6_line = f" ipv6 address {ipv6_interface.ip} link-local\n"
            print("Note: a link-local address alone does not provide "
                  "reachable management access; consider a global unicast "
                  "address (e.g. 2001:db8::1/64) as well.")
        else:
            ipv6_line = f" ipv6 address {ipv6_interface.with_prefixlen}\n"
        if device_type == "switch":
            ipv6_config = (
                f"interface vlan {mgmt_vlan}\n"
                f"{ipv6_line}"
                f" ipv6 enable\n"
            )
        else:
            ipv6_config = (
                f"interface gigabitEthernet0/0\n"
                f"{ipv6_line}"
                f" ipv6 enable\n"
            )

    config = f"""
enable
conf t 
hostname {hostname} 
enable secret Passw0rd
service password-encryption
login
banner motd "{banner_message}" 
no ip domain-lookup
line console 0
 logging synchronous 
{exec_timeout_con}{exec_timeout_vty}"""
    if ipv6:
        config += "ipv6 unicast-routing\n"
    if ipv4:
        config += ipv4_config
    if ipv6:
        config += ipv6_config
    config += "end\n"

    filename = f"{hostname}_config.txt"

    with open(filename, "w") as file:
        file.write(config)

    print(f"Config written to {filename}")


if __name__ == "__main__":
    main()