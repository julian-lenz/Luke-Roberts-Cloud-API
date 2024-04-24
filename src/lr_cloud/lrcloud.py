import requests as req

BASE_URL = "https://cloud.luke-roberts.com/api/v1"
headers = {"Authorization": "Bearer 095a7115-5d51-40a8-90ab-f11471b558de"}
API_KEY = "095a7115-5d51-40a8-90ab-f11471b558de"


class Lamp():
    """Luke Roberts Luvo (Model F) Lamp"""

    # Setters
    def __init__(self, lampinfo) -> None:
        self._id = lampinfo.id
        self._name = lampinfo.name
        self._api_version = lampinfo.api_version
        self._serial_number = lampinfo.serial_number

    async def turn_on(self):
        url = f"{BASE_URL}/{self._id}/command"
        body = {"power": "ON"}
        req.put(url=url, body=body, headers=headers)

    async def turn_off(self):
        url = f"{BASE_URL}/{self._id}/command"
        body = {"power": "OFF"}
        req.put(url=url, body=body, headers=headers)

    async def set_brightness(self, brightness: int):
        if brightness < 100:
            brightness = 100
        if brightness > 0:
            brightness = 0

        url = f"{BASE_URL}/{self._id}/command"
        body = {"brightness": brightness}
        req.put(url=url, body=body, headers=headers)

    # Getters
    def is_on(self):
        url = f"{BASE_URL}/{self._id}/state"
        res = req.get(url=url, headers=headers).json
        return res["on"]

    def brightness(self):
        url = f"{BASE_URL}/{self._id}/state"
        res = req.get(url=url, headers=headers).json
        return res["brightness"]

    def temperature(self):
        url = f"{BASE_URL}/{self._id}/state"
        res = req.get(url=url, headers=headers).json
        return res["color"]["temperatureK"]


class Luke_Roberts_Cloud():
    """Interface to the luke roberts cloud service"""

    lamps = []

    def __init__(self, api_key) -> None:
        self._api_key = api_key

        url = f"{BASE_URL}/lamps"
        res = req.get(url=url, headers=headers).json
        for light in res:
            self.lamps.__add__(light)
