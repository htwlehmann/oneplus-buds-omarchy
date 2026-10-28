from __future__ import annotations

from .lifecycle_trace import span

from dataclasses import dataclass
from typing import Any

BLUEZ_SERVICE = "org.bluez"
BLUEZ_ROOT = "/"
OBJECT_MANAGER = "org.freedesktop.DBus.ObjectManager"
DEVICE_INTERFACE = "org.bluez.Device1"
BATTERY_INTERFACE = "org.bluez.Battery1"

OPO_UUIDS = {
    "00001107-d102-11e1-9b23-00025b00a5a5",
    "0000079a-d102-11e1-9b23-00025b00a5a5",
}


@dataclass(frozen=True)
class Device:
    address: str
    name: str
    connected: bool
    uuids: tuple[str, ...]
    battery: int | None
    modalias: str | None = None
    services_resolved: bool = False
    # The user visible name of the device. BlueZ keeps the name reported by
    # the device and a separate alias that the user can rename, which is what
    # the phone shows as the device name.
    alias: str | None = None

    @property
    def looks_compatible(self) -> bool:
        brand = self.name.lower()
        return ("oneplus" in brand or "oppo" in brand) and bool(
            OPO_UUIDS.intersection(self.uuids)
        )


def _managed_objects() -> dict[Any, dict[Any, dict[Any, Any]]]:
    try:
        import dbus
    except ImportError as error:
        raise RuntimeError(
            "direct BlueZ discovery requires the system dbus-python binding"
        ) from error

    bus = dbus.SystemBus()
    manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE, BLUEZ_ROOT), OBJECT_MANAGER)
    with span("bluez_discovery"):
        return manager.GetManagedObjects()


def connected_devices() -> list[Device]:
    devices: list[Device] = []
    for interfaces in _managed_objects().values():
        properties = interfaces.get(DEVICE_INTERFACE)
        if properties is None or not bool(properties.get("Connected", False)):
            continue
        battery_properties = interfaces.get(BATTERY_INTERFACE, {})
        percentage = battery_properties.get("Percentage")
        devices.append(
            Device(
                address=str(properties.get("Address", "")),
                name=str(properties.get("Name") or properties.get("Alias") or "Unknown device"),
                alias=str(properties.get("Alias") or "") or None,
                connected=True,
                uuids=tuple(str(uuid).lower() for uuid in properties.get("UUIDs", ())),
                battery=int(percentage) if percentage is not None else None,
                modalias=str(properties["Modalias"]) if "Modalias" in properties else None,
                services_resolved=bool(properties.get("ServicesResolved", False)),
            )
        )
    return devices


def select_device(address: str | None = None) -> Device:
    matches = [device for device in connected_devices() if device.looks_compatible]
    if address is not None:
        normalized = address.upper()
        selected = next((device for device in matches if device.address.upper() == normalized), None)
        if selected is None:
            raise RuntimeError(
                f"selected device {address} is not a connected compatible OnePlus/OPPO device"
            )
        return selected
    if not matches:
        raise RuntimeError("no connected OPO-compatible OnePlus/OPPO earbuds found")
    if len(matches) > 1:
        raise RuntimeError("multiple compatible devices connected; select one with --device ADDRESS")
    return matches[0]


def read_device_alias(address: str) -> str | None:
    """Read the user visible name of a device from BlueZ."""
    import dbus

    try:
        bus = dbus.SystemBus(private=True)
        manager = dbus.Interface(
            bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
        for object_path, interfaces in manager.GetManagedObjects().items():
            properties = interfaces.get("org.bluez.Device1")
            if properties and str(properties.get("Address", "")).upper() == address.upper():
                alias = str(properties.get("Alias") or "")
                return alias or None
    except Exception:
        return None
    return None


def set_device_alias(address: str, alias: str) -> str:
    """Rename the device in BlueZ and read the alias back.

    The alias is the name the user gives the device; it is what the phone
    shows as the device name as well. BlueZ exposes it as a writable
    property of org.bluez.Device1, and the call goes to the adapter, so the
    earbuds are never addressed by this.
    """
    import dbus

    cleaned = alias.strip()
    if not cleaned:
        raise ValueError("the device name must not be empty")
    if len(cleaned) > 248:
        raise ValueError("the device name is too long")
    bus = dbus.SystemBus(private=True)
    manager = dbus.Interface(
        bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
    path = None
    for object_path, interfaces in manager.GetManagedObjects().items():
        properties = interfaces.get("org.bluez.Device1")
        if properties and str(properties.get("Address", "")).upper() == address.upper():
            path = object_path
            break
    if path is None:
        raise RuntimeError("the device is not known to BlueZ any more")
    device = bus.get_object("org.bluez", path)
    properties = dbus.Interface(device, "org.freedesktop.DBus.Properties")
    properties.Set("org.bluez.Device1", "Alias", dbus.String(cleaned))
    stored = str(properties.Get("org.bluez.Device1", "Alias"))
    return stored or cleaned
