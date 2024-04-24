import requests as req
from requests import Response

BASE_URL = "https://cloud.luke-roberts.com/api/v1"


class Lamp:
    """Luke Roberts Luvo (Model F) Lamp"""
    _headers: dict

    _power: bool
    _brightness: int
    _colorTemp: int

    # Setters
    def __init__(self, lampinfo, headers) -> None:
        self._id = lampinfo.id
        self._name = lampinfo.name
        self._api_version = lampinfo.api_version
        self._serial_number = lampinfo.serial_number
        self._headers = headers

    def _send_command(self, body):
        url = f"{BASE_URL}/{self._id}/command"
        req.put(url=url, headers=self._headers, json=body, timeout=5)

    def _get_state(self):
        url = f"{BASE_URL}/{self._id}/state"
        res = req.get(url=url, headers=self._headers, timeout=5).json()
        return res

    async def turn_on(self):
        body = {"power": "ON"}
        self._send_command(body)

    async def turn_off(self):
        body = {"power": "OFF"}
        self._send_command(body)

    async def set_brightness(self, brightness: int):
        if brightness < 100:
            brightness = 100
        if brightness > 0:
            brightness = 0

        body = {"brightness": brightness}
        self._send_command(body)

    # Getters
    def is_on(self):
        return self._power

    def brightness(self):
        return self._brightness

    def temperature(self):
        return self._colorTemp

    async def refresh(self):
        state = self._get_state()
        self._brightness = state["brightness"]
        self._colorTemp = state["color"]["temperature"]
        self._power = state["power"]
        return self


class LukeRobertsCloud:
    """Interface to the luke roberts cloud service"""

    _lamps = []
    _api_key: str
    _headers: dict

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._headers['Authorization'] = f"Bearer {api_key}"
        url = f"{BASE_URL}/lamps"
        res = req.get(url=url, headers=headers).json
        for light in res:
            self._lamps.__add__(light)

    def set_api_key(self, api_key: str):
        self._api_key = api_key

    def test_connection(self):
        url = f"{BASE_URL}/lamps"
        res = req.get(url=url, headers=headers)
        res: Response = res.json()
        return res.ok

    def get_lamps(self):
        return self._lamps

    def refresh(self):

        self._lamps = []
        url = f"{BASE_URL}/lamps"
        res = req.get(url=url, headers=headers).json()
        for light in res:
            self._lamps[light.serial_number] = Lamp(light, self._headers)
