import json
import logging
import re
from .datamodels import DiagnosticsConnection, NetworkDevice, SystemInfo


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


def get_network_devices(content):
    """Parse the network devices from the javascript content."""
    soup = BeautifulSoup(content, "html.parser")

    # Find the script tag containing our data
    script = soup.find("script", text=re.compile("var ethernet_data"))

    if not script:
        raise ValueError("Could not find the required script tag in the HTML")

    # Extract JavaScript variables
    js_vars = {}
    for var in [
        "ethernet_data",
        "wifi2_data",
        "wifi5_data",
        "guest_wifi2_data",
        "guest_wifi5_data",
    ]:
        match = re.search(rf"var {var} = (\[.*?\]);", script.string, re.DOTALL)
        if match:
            js_vars[var] = json.loads(match.group(1))
        else:
            js_vars[var] = []

    devices = []
    data_sources = [
        (js_vars.get("ethernet_data", []), "ethernet"),
        (js_vars.get("wifi2_data", []), "wifi2"),
        (js_vars.get("wifi5_data", []), "wifi5"),
        (js_vars.get("guest_wifi2_data", []), "guest_wifi2"),
        (js_vars.get("guest_wifi5_data", []), "guest_wifi5"),
    ]

    for data_list, interface_tag in data_sources:
        for device_data in data_list:
            devices.append(NetworkDevice.from_dict(device_data, interface_tag))
    return devices


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

    return SystemInfo.from_dict(data)


def get_diagnostics_connection_modal(content: str) -> DiagnosticsConnection:
    soup = BeautifulSoup(content, "html.parser")
    diagnostics_info = {}
    for div in soup.select("div.control-group"):
        label = div.select_one("label.control-label")
        span = div.select_one("span.simple-desc")
        if label and span:
            key = label.text.strip()
            value = span.text.strip()
            diagnostics_info[key] = value

    return DiagnosticsConnection.from_dict(diagnostics_info)
