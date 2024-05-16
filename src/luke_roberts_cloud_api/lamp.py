import aiohttp

from .const import BASE_URL


class Lamp:
    """Luke Roberts Luvo (Model F) Lamp"""
    _headers: dict


    """Safes the scenes internally, key is the scene id, value is the name"""
    _scenes = dict

    def __init__(self, lampInfo, headers) -> None:
        self._id = lampInfo["id"]
        self._name = lampInfo["name"]
        self._api_version = lampInfo["api_version"]
        self._serial_number = lampInfo["serial_number"]
        self._headers = headers
        self.power: bool = False
        self.brightness: int = 0
        self.colortemp_kelvin: int = 0
        self._online: bool = False

    async def _send_command(self, body):
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

    def getSerialNumber(self):
        return self._serial_number

    def getId(self):
        return self._id

    def getPower(self):
        return self.power

    def getBrightness(self):
        return self.brightness

    def getColorTemp(self):
        return self.colortemp_kelvin

    async def turn_on(self):
        body = {"power": "ON"}
        await self._send_command(body)
        await self.refresh()

    async def turn_off(self):
        body = {"power": "OFF"}
        await self._send_command(body)
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
        self.colortemp_kelvin = state["color"]["temperatureK"]
        self.power = state["on"]
        self._online = state["online"]
        return self

    def __str__(self):
        return (f"{self._name}, "
                f"Serial Number: {self._serial_number}, "
                f"ID: {self._id},")
