## Technicolor Gateway Scraper library 
## Feature fork

This is a fork of https://github.com/shaiu/techicolorgateway with the intention to expose everything from the web gui that makes sense to add. 

### How to use it


    import technicolorgateway
    import os

    # Get the router's details from environment variables
    router_ip = os.getenv("ROUTER_IP", "192.168.1.1")
    router_port = os.getenv("ROUTER_PORT", "80")
    router_user = os.getenv("ROUTER_USER", "User")
    router_password = os.getenv("ROUTER_PASSWORD", "admin")


    router = technicolorgateway.TechnicolorGateway(
        router_ip, router_port, router_user, router_password
    )
    router.authenticate()

    # print all information about the router

    print(router.get_broadband_modal())
    print(router.get_device_modal())
    print(router.get_system_info_modal())
    print(router.get_diagnostics_connection_modal())
 

