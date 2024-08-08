import ipaddress
import re
from dataclasses import Field, dataclass
from datetime import datetime, timedelta

import macaddress


@dataclass
class NetworkDevice:
    host_name: str
    dhcp_vendor_class: str | None
    dhcp_lease_ip: ipaddress.IPv4Address
    l3_interface: str
    connected_time: datetime
    state: str
    dhcp_tag: str
    device_type: str | None
    bytes_sent: int
    ipv6: ipaddress.IPv6Address | None
    port: str | None
    interface_type: str
    speed: str | None
    priority: int
    ssid: str | None
    dhcp_lease_time: int
    bytes_received: int | None
    delete: str
    radio: str | None
    friendly_name: str
    ip_address: ipaddress.IPv4Address
    pkts_sent: int
    firewall_zone: str
    pkts_received: int
    mac_address: macaddress.MAC
    l2_interface: str
    lease_type: str
    product_class: str | None
    paramindex: str
    host_type: str | None
    ipv4: ipaddress.IPv4Address
    lease_time_remaining: int
    interface_tag: str  # New field for the interface tag
    is_ethernet: bool = False
    is_guest: bool = False
    is_5ghz: bool = False
    is_24ghz: bool = False
    is_satellite: bool = False

    @classmethod
    def from_dict(cls, data: dict, interface_tag: str) -> "NetworkDevice":
        # Convert ConnectedTime from Unix timestamp to datetime
        connected_time = datetime.fromtimestamp(int(data["ConnectedTime"]))

        # Convert numeric strings to appropriate types
        return cls(
            host_name=data["HostName"],
            dhcp_vendor_class=data["DhcpVendorClass"] or None,
            dhcp_lease_ip=(
                ipaddress.IPv4Address(data["DhcpLeaseIP"])
                if data["DhcpLeaseIP"]
                else None
            ),
            l3_interface=data["L3Interface"],
            connected_time=connected_time,
            state=data["State"],
            dhcp_tag=data["DhcpTag"],
            device_type=data["DeviceType"] or None,
            bytes_sent=int(data["BytesSent"]),
            ipv4=ipaddress.IPv4Address(data["IPv4"]) if data["IPv4"] else None,
            ipv6=ipaddress.IPv6Address(data["IPv6"]) if data["IPv6"] else None,
            port=data["Port"] or None,
            interface_type=data["InterfaceType"],
            speed=data["Speed"] or None,
            priority=int(data["Priority"]),
            ssid=data["SSID"] or None,
            dhcp_lease_time=int(data["DhcpLeaseTime"] or 0),
            bytes_received=int(data["BytesReceived"] or 0),
            delete=data["Delete"],
            radio=data["Radio"] or None,
            friendly_name=data["FriendlyName"],
            ip_address=(
                ipaddress.IPv4Address(data["IPAddress"]) if data["IPAddress"] else None
            ),
            pkts_sent=int(data["PktsSent"]),
            firewall_zone=data["FirewallZone"],
            pkts_received=int(data["PktsReceived"]),
            mac_address=macaddress.MAC(data["MACAddress"]),
            l2_interface=data["L2Interface"],
            lease_type=data["LeaseType"],
            product_class=data["ProductClass"] or None,
            paramindex=data["paramindex"],
            host_type=data["HostType"] or None,
            lease_time_remaining=int(data["LeaseTimeRemaining"]),
            interface_tag=interface_tag,  # Add the interface tag,
            is_ethernet="ethernet" in interface_tag,
            is_guest="guest" in interface_tag,
            is_5ghz="wifi5" in interface_tag,
            is_24ghz="wifi2" in interface_tag,
            is_satellite="cpewan-id" in data["DhcpTag"],
        )


@dataclass
class SystemInfo:
    product_vendor: str | None
    product_name: str | None
    serial_number: str | None
    software_version: str | None
    uptime_since_last_reboot: str | None
    uptime: timedelta | None
    firmware_version: str | None
    hardware_version: str | None
    mac_address: macaddress.MAC
    memory_usage: float | None
    cpu_usage: float | None
    reboot_cause: str | None

    @staticmethod
    def parse_time_string(time_string: str | None) -> timedelta | None:
        """Parse uptime time string into a timedelta object."""
        if not time_string:
            return None

        # Dictionary to map units to their singular form
        unit_mapping = {
            "days": "day",
            "hours": "hour",
            "minutes": "minute",
            "seconds": "second",
        }

        # Initialize time components
        components = {unit: 0 for unit in unit_mapping.keys()}

        # Regular expression to match number and unit pairs
        pattern = r"(\d+)\s+(day|hour|minute|second)s?"
        matches = re.findall(pattern, time_string, re.IGNORECASE)

        for value, unit in matches:
            # Convert unit to plural form for our dictionary
            unit_plural = next(
                plural
                for plural, singular in unit_mapping.items()
                if singular.startswith(unit.lower())
            )
            components[unit_plural] = int(value)

        return timedelta(
            days=components["days"],
            hours=components["hours"],
            minutes=components["minutes"],
            seconds=components["seconds"],
        )

    @staticmethod
    def parse_percent(percent_string: str | None) -> float | None:
        """Parse a percentage string into a float."""
        if not percent_string:
            return None
        match = re.match(r"(\d+(?:\.\d+)?)\s*%", percent_string)
        return float(match.group(1)) / 100 if match else None

    @classmethod
    def from_dict(cls, data: dict) -> "SystemInfo":
        """Create a SystemInfo instance from a dictionary."""
        uptime_str = data.get("Uptime since last reboot")
        return cls(
            product_vendor=data.get("Product Vendor"),
            product_name=data.get("Product Name"),
            serial_number=data.get("Serial Number"),
            software_version=data.get("Software Version"),
            uptime_since_last_reboot=uptime_str,
            uptime=cls.parse_time_string(uptime_str),
            firmware_version=data.get("Firmware Version"),
            hardware_version=data.get("Hardware Version"),
            mac_address=macaddress.MAC(data.get("MAC Address")),
            memory_usage=cls.parse_percent(data.get("Memory Usage")),
            cpu_usage=cls.parse_percent(data.get("CPU Usage")),
            reboot_cause=data.get("Reboot Cause"),
        )


@dataclass
class DiagnosticsConnection:
    wan_enable: str | None
    wan_available: str | None
    ip_version_4_address: ipaddress.IPv4Address | None
    ip_version_6_address: ipaddress.IPv6Address | None
    next_hop_ping: bool | None
    first_dns_server_ping: bool | None
    second_dns_server_ping: bool | None

    @staticmethod
    def parse_ping(ping_string: str | None) -> bool | None:
        """Parse a ping result string into a boolean"""
        if ping_string is None:
            return None
        elif ping_string == "Ongoing":
            return None
        return ping_string == "Success"

    @classmethod
    def from_dict(cls, data: dict) -> "DiagnosticsConnection":
        """Create a DiagnosticsConnection instance from a dictionary."""
        _ipv4 = data.get("IP Version 4 Address")
        _ipv6 = data.get("IP Version 6 Address")
        return cls(
            wan_enable=data.get("WAN Enable"),
            wan_available=data.get("WAN Available"),
            ip_version_4_address=(
                ipaddress.IPv4Address(_ipv4) if _ipv4 != "No Address Assigned" else None
            ),
            ip_version_6_address=(
                ipaddress.IPv4Address(_ipv6) if _ipv6 != "No Address Assigned" else None
            ),
            next_hop_ping=cls.parse_ping(data.get("Next Hop Ping")),
            first_dns_server_ping=cls.parse_ping(data.get("First DNS Server Ping")),
            second_dns_server_ping=cls.parse_ping(data.get("Second DNS Server Ping")),
        )
