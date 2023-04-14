import pytest
import responses

from technicolorgateway import TechnicolorGateway


@responses.activate
def test_srp6authenticate_no_token():
    with open("resources/login_page_no_token.html", encoding='utf-8') as file:
        htm = file.read()
    responses.add(responses.POST, 'http://192.168.1.2:80/', htm, status=200)
    tech_gateway = TechnicolorGateway('192.168.1.2', 80, "admin", "aaaaaa")
    tech_gateway.authenticate()
    with pytest.raises(TypeError) as err:
        tech_gateway.srp6authenticate()
    assert "'NoneType' object is not subscriptable" in str(err.value)
