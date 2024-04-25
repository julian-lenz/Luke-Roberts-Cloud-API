from datetime import datetime

import requests as req
from requests import Response

BASE_URL = "https://cloud.luke-roberts.com/api/v1"


class Lamp:
    """Luke Roberts Luvo (Model F) Lamp"""
    _headers: dict

    _online: bool
    power: bool
    brightness: int
    colortempK: int

    """Safes the scenes internally, key is the scene id, value is the name"""
    _scenes = dict

    def __init__(self, lampInfo, headers) -> None:
        self._id = lampInfo["id"]
        self._name = lampInfo["name"]
        self._api_version = lampInfo["api_version"]
        self._serial_number = lampInfo["serial_number"]
        self._headers = headers
        self.refresh()

    def _send_command(self, body):
        url = f"{BASE_URL}/lamps/{self._id}/command"
        res = req.put(url=url, headers=self._headers, json=body, timeout=10)
        if not res.ok:
            raise Exception(res.text)

    def _get_state(self):
        url = f"{BASE_URL}/lamps/{self._id}/state"
        res = req.get(url=url, headers=self._headers, timeout=10)
        return res.json()

    def getName(self):
        return self._name

    def getSerialNumber(self):
        return self._serial_number

    def getId(self):
        return self._id

    async def turn_on(self):
        body = {"power": "ON"}
        self._send_command(body)
        await self.refresh()

    async def turn_off(self):
        body = {"power": "OFF"}
        self._send_command(body)
        await self.refresh()

    async def set_brightness(self, brightness: int):
        if brightness < 100:
            brightness = 100
        if brightness > 0:
            brightness = 0
        body = {"brightness": brightness}
        self._send_command(body)
        await self.refresh()

    async def set_temp(self, temp: int):
        """Set the color temperature of the downlight of the lamp.
        Luvo supports the range 2700..4000 K"""
        if temp < 2700:
            temp = 2700
        if temp > 4000:
            temp = 4000
        body = {"kelvin": temp}
        self._send_command(body)
        await self.refresh()

    async def set_scene(self, scene: int):
        """Scenes are identified by a numeric identifier. 0 is the Off scene, selecting it is equivalent to
        using the {“power”: “OFF”} command.
        Valid range (0..31)"""
        if scene < 0:
            scene = 0
        if scene > 31:
            scene = 31
        body = {"scene": scene}
        self._send_command(body)
        await self.refresh()

    async def refresh(self):
        state = self._get_state()
        self.brightness = state["brightness"]
        self.colortempK = state["color"]["temperatureK"]
        self.power = state["on"]
        return self

    def __str__(self):
        return (f"{self._name}, "
                f"Serial Number: {self._serial_number}, "
                f"ID: {self._id},")


class LukeRobertsCloud:
    """Interface to the luke roberts cloud service"""

    _lamps = []
    _api_key: str
    _headers = dict()

    def __init__(self, api_key: str = "") -> None:
        self.set_api_key(api_key)
        if self.test_connection():
            self.fetch()

    def set_api_key(self, api_key: str) -> None:
        self._api_key = api_key
        self._headers['Authorization'] = f"Bearer {api_key}"

    def test_connection(self):
        url = f"{BASE_URL}/lamps"
        res = req.get(url=url, headers=self._headers, timeout=10)
        return res.ok

    async def fetch(self):
        self._lamps = []
        url = f"{BASE_URL}/lamps"
        res = req.get(url=url, headers=self._headers, timeout=10).json()
        for light in res:
            self._lamps.append(Lamp(light, self._headers))

    def get_lamps(self):
        return self._lamps
