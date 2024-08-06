import logging
import re
from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

import html2text
from bs4 import BeautifulSoup

_LOGGER = logging.getLogger(__name__)

h = html2text.HTML2Text()
h.body_width = 0

regex_broadband_modal = re.compile(
    r" {2}Line Rate +(?P<us>[0-9.]+)"
    r" Mbps (?P<ds>[0-9.]+)"
    r" Mbps *Data Transferred +(?P<uploaded>[0-9.]+)"
    r" .Bytes (?P<downloaded>[0-9.]+) .Bytes "
)

regex_device_modal = re.compile(
    r"(?P<name>[\w\-_]+) ?\|"
    r" ?(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})? ?\|"
    r" ?(?P<mac>\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2})"
)


def get_broadband_modal(content):
    body = h.handle(content)
    body = body[body.find("DSL Status") : body.find("Close")]
    body = body.replace("_", "").replace("\n", " ")
    return regex_broadband_modal.search(body).groupdict()


def get_device_modal(content):
    data = []
    soup = BeautifulSoup(content, features="lxml")
    devices = soup.find_all("div", {"class": "popUp smallcard span4"})
    _LOGGER.debug("devices len %s" % len(devices))
    rows = soup.find_all("tr")
    _LOGGER.debug("rows len %s" % len(rows))
    if len(devices) > 0:
        get_data_from_devices(data, devices)
    elif len(rows) > 0:
        get_data_from_rows(data, rows)
    return data


def get_data_from_devices(data, devices):
    _LOGGER.debug("get_data_from_devices")
    _LOGGER.debug(f"first device {devices[0]}")
    for device in devices:
        device_contents = device.contents
        name = device_contents[1].contents[1].contents[1].text
        ip_address = device_contents[3].contents[3].contents[1].text
        mac = device_contents[3].contents[5].contents[1].text
        data.append({"name": name, "ip": ip_address, "mac": mac})


def get_data_from_rows(data, rows):
    _LOGGER.debug("get_data_from_rows")
    headers = [ele.text.strip().lower() for ele in rows[0].find_all("th")]
    name_index = headers.index("hostname")
    try:
        ip_index = headers.index("ip address")
    except ValueError:
        ip_index = headers.index("ipv4")
    try:
        mac_index = headers.index("mac address")
    except ValueError:
        mac_index = headers.index("mac")
    rows.pop(0)
    _LOGGER.debug(f"first row {rows[0]}")
    for row in rows:
        cols = row.find_all("td")
        cols = [ele.text.strip() for ele in cols]
        data.append(
            {"name": cols[name_index], "ip": cols[ip_index], "mac": cols[mac_index]}
        )


@dataclass
class SystemInfoModal:
    product_vendor: Optional[str]
    product_name: Optional[str]
    serial_number: Optional[str]
    software_version: Optional[str]
    uptime_since_last_reboot: Optional[str]
    uptime: Optional[timedelta]
    firmware_version: Optional[str]
    hardware_version: Optional[str]
    mac_address: Optional[str]
    memory_usage: Optional[float]
    cpu_usage: Optional[float]
    reboot_cause: Optional[str]

    @staticmethod
    def parse_time_string(time_string: Optional[str]) -> Optional[timedelta]:
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
    def parse_percent(percent_string: Optional[str]) -> Optional[float]:
        """Parse a percentage string into a float."""
        if not percent_string:
            return None
        match = re.match(r"(\d+(?:\.\d+)?)\s*%", percent_string)
        return float(match.group(1)) / 100 if match else None

    @classmethod
    def from_dict(cls, data: dict) -> "SystemInfoModal":
        """Create a SystemInfoModal instance from a dictionary."""
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
            mac_address=data.get("MAC Address"),
            memory_usage=cls.parse_percent(data.get("Memory Usage")),
            cpu_usage=cls.parse_percent(data.get("CPU Usage")),
            reboot_cause=data.get("Reboot Cause"),
        )


def get_system_info_modal(content):
    soup = BeautifulSoup(content, "html.parser")
    # Extract product information
    data = {}
    for div in soup.select("div.control-group"):
        label = div.select_one("label.control-label")
        span = div.select_one("span.simple-desc")
        if label and span:
            key = label.text.strip()
            value = span.text.strip()
            data[key] = value

    return SystemInfoModal.from_dict(data)


@dataclass
class DiagnosticsConnectionModal:
    wan_enable: Optional[str]
    wan_available: Optional[str]
    ip_version_4_address: Optional[str]
    ip_version_6_address: Optional[str]
    next_hop_ping: Optional[bool]
    first_dns_server_ping: Optional[bool]
    second_dns_server_ping: Optional[bool]

    @staticmethod
    def parse_ping(ping_string: Optional[str]) -> Optional[bool]:
        """Parse a ping result string into a boolean"""
        if ping_string is None:
            return None
        return ping_string == "Success"

    @classmethod
    def from_dict(cls, data: dict) -> "DiagnosticsConnectionModal":
        """Create a DiagnosticsConnectionModal instance from a dictionary."""
        return cls(
            wan_enable=data.get("WAN Enable"),
            wan_available=data.get("WAN Available"),
            ip_version_4_address=data.get("IP Version 4 Address"),
            ip_version_6_address=data.get("IP Version 6 Address"),
            next_hop_ping=cls.parse_ping(data.get("Next Hop Ping")),
            first_dns_server_ping=cls.parse_ping(data.get("First DNS Server Ping")),
            second_dns_server_ping=cls.parse_ping(data.get("Second DNS Server Ping")),
        )


def get_diagnostics_connection_modal(content: str) -> DiagnosticsConnectionModal:
    soup = BeautifulSoup(content, "html.parser")
    diagnostics_info = {}
    for div in soup.select("div.control-group"):
        label = div.select_one("label.control-label")
        span = div.select_one("span.simple-desc")
        if label and span:
            key = label.text.strip()
            value = span.text.strip()
            diagnostics_info[key] = value

    return DiagnosticsConnectionModal.from_dict(diagnostics_info)
