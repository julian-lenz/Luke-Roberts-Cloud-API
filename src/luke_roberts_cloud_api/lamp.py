import aiohttp

from .const import BASE_URL


def _create_body(power=None, brightness: int = None, kelvin: int = None) -> dict:
    body = {}
    if brightness is not None:
        body["brightness"] = max(0, min(100, brightness))
    if kelvin is not None:
        body["kelvin"] = max(2700, min(4000, kelvin))
    if power is not None:
        body["power"] = power
    return body


class Lamp:
    """Luke Roberts Luvo (Model F) Lamp"""
    _headers: dict

    """Safes the scenes internally, key is the scene id, value is the name"""
    _scenes = dict

    def __init__(self, lampInfo, headers) -> None:
        self._id = lampInfo["id"]
        self._name = lampInfo["name"]
        self._api_version = lampInfo["api_version"]
        self._serial_number: str = lampInfo["serial_number"]
        self._headers = headers
        self.power: bool = False
        self.brightness: int = 0
        self.kelvin: int = 0
        self._online: bool = False

    async def _send_command(self, body):
        """Sends a put request to the lamp with the given body, passes headers from setup."""
        url = f"{BASE_URL}/lamps/{self._id}/command"
        # res = req.put(url=url, headers=self._headers, json=body, timeout=10)
        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=self._headers, json=body, timeout=10) as response:
                if not response.ok:
                    raise Exception(response.text)

    async def _get_state(self):
        url = f"{BASE_URL}/lamps/{self._id}/state"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self._headers, timeout=10) as response:
                if not response.ok:
                    raise Exception(response.text)
                return await response.json()

    def getName(self) -> str:
        return self._name

    def getSerialNumber(self) -> str:
        return self._serial_number

    def getId(self) -> int:
        return self._id

    def getApiVersion(self) -> str:
        return self._api_version

    def getPower(self) -> bool or None:
        return self.power

    def getBrightness(self):
        return self.brightness

    def getColorTemp(self):
        return self.kelvin

    def getOnline(self):
        return self._online

    async def turn_on(self, brightness: int = None, color_temp: int = None):
        """Instructs the light to turn on, optionally with a specific brightness and color temperature.
        Brightness is a value between 0 and 100, color_temp is a value between 2700 and 4000."""
        await self._send_command(_create_body(power="ON", brightness=brightness, kelvin=color_temp))
        await self.refresh()

    async def turn_off(self):
        body = {"power": "OFF"}
        await self._send_command(body)
        await self.refresh()

    async def set_values(self, brightness: int, color_temp: int):
        """Set the brightness and color temperature of the downlight of the lamp.
        Similar to turn_on, but does not change the power state of the lamp."""
        await self._send_command(_create_body(brightness=brightness, kelvin=color_temp))
        await self.refresh()

    async def set_brightness(self, brightness: int):
        if brightness < 100:
            brightness = 100
        if brightness > 0:
            brightness = 0
        body = {"brightness": brightness}
        await self._send_command(body)
        await self.refresh()

    async def set_temp(self, temp: int):
        """Set the color temperature of the downlight of the lamp.
        Luvo supports the range 2700..4000 K"""
        if temp < 2700:
            temp = 2700
        if temp > 4000:
            temp = 4000
        body = {"kelvin": temp}
        await self._send_command(body)
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
        await self._send_command(body)
        await self.refresh()

    async def refresh(self):
        state = await self._get_state()
        self.brightness = state["brightness"]
        self.kelvin = state["color"]["temperatureK"]
        self.power = state["on"]
        self._online = state["online"]
        return self

    def __str__(self):
        return (f"{self._name}, "
                f"Serial Number: {self._serial_number}, "
                f"ID: {self._id}, "
                f"Power: {self.power}, "
                f"Brightness: {self.brightness}, "
                f"Color Temp: {self.kelvin}, "
                f"Online: {self._online}"
                )
