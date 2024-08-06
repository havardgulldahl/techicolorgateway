from datetime import datetime, timedelta
from technicolorgateway.modal import (
    get_broadband_modal,
    get_device_modal,
    get_system_info_modal,
    SystemInfo,
    get_diagnostics_connection_modal,
    DiagnosticsConnection,
    get_network_devices,
    NetworkDevice,
)


class TestModal:
    def test_get_broadband_modal(self):
        with open('tests/resources/broadband-modal.lp', encoding='utf-8') as file:
            content = file.read()
        modal_dict = get_broadband_modal(content)
        print('\n')
        print(modal_dict)
        assert len(modal_dict) == 4
        assert modal_dict['us'] == '3.52'
        assert modal_dict['ds'] == '44.88'
        assert modal_dict['uploaded'] == '898.57'
        assert modal_dict['downloaded'] == '3973.16'

    def test_get_device_modal_fw_2_3_1(self):
        with open('tests/resources/device-modal_2_3_1_fw.lp', encoding='utf-8') as file:
            content = file.read()
        modal_list = get_device_modal(content)
        print('\n')
        print(modal_list)
        assert len(modal_list) == 27
        assert modal_list[0]['name'] == 'Unknown-3c:71:bf:39:ab:3b'
        assert modal_list[0]['ip'] == '192.168.1.53'
        assert modal_list[0]['mac'] == '3c:71:bf:39:ab:3b'
        assert modal_list[-1]['name'] == 'Cellulare-KKK'
        assert modal_list[-1]['ip'] == ''
        assert modal_list[-1]['mac'] == 'b4:cd:27:b0:1f:23'

    def test_get_device_modal_len6(self):
        with open('tests/resources/device-modal_len6.lp', encoding='utf-8') as file:
            content = file.read()
        modal_list = get_device_modal(content)
        print('\n')
        print(modal_list)
        assert len(modal_list) == 3
        assert modal_list[0]['name'] == 'hostname1'
        assert modal_list[0]['ip'] == '192.168.1.216'
        assert modal_list[0]['mac'] == 'c8:2b:96:11:09:59'
        assert modal_list[-1]['name'] == 'hostname3'
        assert modal_list[-1]['ip'] == '192.168.1.192'
        assert modal_list[-1]['mac'] == '24:62:ab:bb:65:30'

    def test_get_device_modal_len12(self):
        with open('tests/resources/device-modal_len_12.lp', encoding='utf-8') as file:
            content = file.read()
        modal_list = get_device_modal(content)
        print('\n')
        print(modal_list)
        assert len(modal_list) == 2
        assert modal_list[0]['name'] == 'hostname1_aqua'
        assert modal_list[0]['ip'] == '192.168.1.251'
        assert modal_list[0]['mac'] == 'e8:ab:fa:2b:ce:e0'
        assert modal_list[-1]['name'] == 'hostname2_aqua'
        assert modal_list[-1]['ip'] == '192.168.1.251'
        assert modal_list[-1]['mac'] == 'fc:8f:81:83:7f:1d'

    def test_get_device_modal_len8(self):
        with open('tests/resources/device-modal_len_8.lp', encoding='utf-8') as file:
            content = file.read()
        modal_list = get_device_modal(content)
        print('\n')
        print(modal_list)
        assert len(modal_list) == 1
        assert modal_list[0]['name'] == 'Mate'
        assert modal_list[0]['ip'] == '192.168.1.2'
        assert modal_list[0]['mac'] == '02:11:12:12:12:12'

    def test_get_device_modal_ipv6devices(self):
        with open('tests/resources/ipv6devices-modal.lp', encoding='utf-8') as file:
            content = file.read()
        modal_list = get_device_modal(content)
        print('\n')
        print(modal_list)
        assert len(modal_list) == 1
        assert modal_list[0]['name'] == 'DeviceHostName'
        assert modal_list[0]['ip'] == '192.168.1.111'
        assert modal_list[0]['mac'] == 'A4:83:e7:32:7e:11'

    def test_get_device_modal(self):
        with open('tests/resources/device-modal_.lp', encoding='utf-8') as file:
            content = file.read()
        modal_list = get_device_modal(content)
        print('\n')
        print(modal_list)
        assert modal_list[0]['name'] == 'Luce-Studio'
        assert modal_list[0]['ip'] == '*.*.*.158'
        assert modal_list[0]['mac'] == '10:5a:17:12:a0:d6'

    def test_get_device_modal_052823(self):
        with open('tests/resources/device-modal.lp.txt', encoding='utf-8') as file:
            content = file.read()
        modal_list = get_device_modal(content)
        print('\n')
        print(modal_list)
        assert modal_list[0]['name'] == 'EdgeRouter-X'
        assert modal_list[0]['ip'] == '192.168.0.152'
        assert modal_list[0]['mac'] == '74:83:c2:fd:e0:07'

    def test_get_system_info_modal(self):
        with open("tests/resources/system-info-modal.lp", encoding="utf-8") as file:
            content = file.read()
        modal_dict = get_system_info_modal(content)
        print("\n")
        print(modal_dict)
        assert isinstance(modal_dict, SystemInfo)
        assert modal_dict.product_vendor == "Technicolor"
        assert modal_dict.product_name == "Telia F1"
        assert modal_dict.serial_number == "CP2221ADU9K"
        assert modal_dict.software_version == "19.5"
        assert (
            modal_dict.uptime_since_last_reboot
            == "19 days 6 hours 13 minutes 8 seconds"
        )
        assert modal_dict.uptime == timedelta(days=19, seconds=22388)
        assert modal_dict.firmware_version == "19.5.1062-4581003"
        assert modal_dict.hardware_version == "GCNT-X"
        assert modal_dict.mac_address == "AA:BB:CC:45:18:0E"
        assert modal_dict.memory_usage == 0.86
        assert modal_dict.cpu_usage == 0.02
        assert modal_dict.reboot_cause == "Power"

    def test_get_diagnostics_connection_modal(self):
        with open(
            "tests/resources/diagnostics-connection-modal.lp", encoding="utf-8"
        ) as file:
            content = file.read()
        modal_dict = get_diagnostics_connection_modal(content)
        print("\n")
        print(modal_dict)
        assert isinstance(modal_dict, DiagnosticsConnection)
        assert modal_dict.wan_enable == "Interface Enabled"
        assert modal_dict.wan_available == "Link Up"
        assert modal_dict.ip_version_4_address == "82.133.131.13"
        assert modal_dict.ip_version_6_address == "No Address Assigned"
        assert modal_dict.next_hop_ping == True
        assert modal_dict.first_dns_server_ping == True
        assert modal_dict.second_dns_server_ping == True

    def test_get_detailed_network_devices(self):
        with open("tests/resources/device-modal.lp-script", encoding="utf-8") as file:
            content = file.read()
        devices = get_network_devices(content)
        print("\n")
        assert len(devices) == 5
        for device in devices:
            assert isinstance(device, NetworkDevice)

        device = devices[0]
        assert device.host_name == "Device1"
        assert device.dhcp_vendor_class == "udhcp 0.9.8"
        assert device.dhcp_lease_ip == "192.168.1.10"
        assert device.l3_interface == "br-lan"
        assert device.connected_time == datetime.fromtimestamp(1721497366)
        assert device.state == "1"
        assert device.dhcp_tag == "lan known br-lan"
        assert device.device_type == "router"
        assert device.bytes_sent == 0
        assert device.ipv6 == None
        assert device.port == "1"
        assert device.interface_type == "ethernet"
        assert device.speed == "1000"
        assert device.priority == 0
        assert device.ssid == None
        assert device.dhcp_lease_time == 3600
        assert device.bytes_received == 0
        assert device.delete == "0"
        assert device.radio == None
        assert device.friendly_name == "Device1"
        assert device.ip_address == "192.168.1.10"
        assert device.pkts_sent == 0
        assert device.firewall_zone == "LAN"
        assert device.pkts_received == 0
        assert device.mac_address == "XX:XX:XX:XX:XX:XX"
        assert device.l2_interface == "eth0"
        assert device.lease_type == "Static"
        assert device.product_class == None
        assert device.paramindex == "2"
        assert device.host_type == None
        assert device.ipv4 == "192.168.1.10"
        assert device.lease_time_remaining == 2110
        assert device.interface_tag == "ethernet"
        assert device.is_ethernet == True
        assert device.is_guest == False
        assert device.is_5ghz == False
        assert device.is_24ghz == False

        device2 = devices[4]
        assert device2.host_name == "Device8"
        assert device2.dhcp_vendor_class == None
        assert device2.dhcp_lease_ip == "192.168.1.222"
        assert device2.l3_interface == "br-lan"
        assert device2.connected_time == datetime.fromtimestamp(1722901121)
        assert device2.state == "1"
        assert device2.dhcp_tag == "lan br-lan"
        assert device2.device_type == None
        assert device2.bytes_sent == 0
        assert device2.ipv6 == None
        assert device2.port == None
        assert device2.interface_type == "wireless"
        assert device2.speed == None
        assert device2.priority == 0
        assert device2.ssid == "XX-XXXX"
        assert device2.dhcp_lease_time == 3600
        assert device2.bytes_received == 0
        assert device2.delete == "0"
        assert device2.radio == "radio_5G"
        assert device2.friendly_name == "Device9"
        assert device2.ip_address == "192.168.1.222"
        assert device2.pkts_sent == 0
        assert device2.firewall_zone == "LAN"
        assert device2.pkts_received == 0
        assert device2.mac_address == "XX:XX:XX:XX:XX:XX"
        assert device2.l2_interface == "wds1_2_2.10"
        assert device2.lease_type == "DHCP"
        assert device2.product_class == None
        assert device2.paramindex == "11"
        assert device2.host_type == None
        assert device2.ipv4 == "192.168.1.222"
        assert device2.lease_time_remaining == 2145
        assert device2.interface_tag == "wifi5"
        assert device2.is_ethernet == False
        assert device2.is_guest == False
        assert device2.is_5ghz == True
        assert device2.is_24ghz == False
