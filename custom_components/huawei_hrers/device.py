import logging
import json
from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic

_LOGGER = logging.getLogger(__name__)

CHAR_INFO_UUID = "15f1e001-a277-43fc-a484-dd39ef8a9100"


def get_data(data: bytearray, T: type):
    if T == float:
        data = int.from_bytes(data, "little") / 100
    elif T == int:
        data = int.from_bytes(data, "little")
    elif T == str:
        data = data.decode()
    _LOGGER.error("parse data %s", data)
    return data


class HuaweiBottleMointor:
    def __init__(self, address: str, name: str, bleakclient: BleakClient) -> None:
        self.address = address
        self.inited = False
        self.name = name
        self.sensor_instances = []
        self.available = False
        self.ble_client: BleakClient = bleakclient
        _LOGGER.error("device created")
        self.waterintake = None
        self.battery = None

    def get_name(self):
        return self.name

    def disconect(self, client: BleakClient):
        self.available = False
        self.waterintake = None
        self.battery = None

    async def read_data(self, character: BleakGATTCharacteristic, data: bytearray):
        flag = None
        UUID = character.uuid
        T = float
        if UUID == CHAR_INFO_UUID:
            T = str
        st = get_data(data=data, T=T)
        st = (
            st.replace('"infoDisplay/currentMl":', '"infoDisplay/currentMl":"')
            .replace(',"infoDisplay/battery":', '","infoDisplay/battery":"')
            .replace("}", '"}')
        )
        data = json.loads(st)
        _LOGGER.error("trans data %s", st)
        self.waterintake = int(data["infoDisplay/currentMl"])
        self.battery = int(data["infoDisplay/battery"])
        self.available = True
        _LOGGER.error("%s get Data: %s", flag, data)

    @property
    def sensors_data(self):
        return {
            "bottle_waterintake": {
                "name": "Bottle Waterintake",
                "id": "bottle_waterintake",
                "state": self.waterintake,
            },
            "bottle_battery": {
                "name": "Bottle battery",
                "id": "bottle_battery",
                "state": self.battery,
            },
        }

    async def connect(self):
        _LOGGER.error("Connecting.. %s", self.name)
        client = self.ble_client
        client.set_disconnected_callback(self.disconect)
        self.inited = True
        connectable = await client.connect()
        if connectable:
            data = await client.read_gatt_char(CHAR_INFO_UUID)
            T = str
            st = get_data(data=data, T=T)
            st = (
                st.replace('"infoDisplay/currentMl":', '"infoDisplay/currentMl":"')
                .replace(',"infoDisplay/battery":', '","infoDisplay/battery":"')
                .replace("}", '"}')
            )
            _LOGGER.error("trans data %s", st)
            data = json.loads(st)
            self.waterintake = int(data["infoDisplay/currentMl"])
            self.battery = int(data["infoDisplay/battery"])
            self.available = True
            _LOGGER.error("first get Data: %s", data)
            await client.start_notify(CHAR_INFO_UUID, self.read_data)
            _LOGGER.error("Connected %s", self.name)
        else:
            raise RuntimeError("Can not connect device")
