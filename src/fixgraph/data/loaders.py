"""Robust loaders for challenge assets with fallback support."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from fixgraph.data.deeplink_catalog import DeeplinkCatalog, DeeplinkRecord
from fixgraph.data.fingerprints import compute_sha256_file, compute_sha256_json


FALLBACK_DEEPLINKS: List[Dict[str, Any]] = [
    {
        "id": "dl_location_01",
        "uri": "bixby://com.samsung.android.settings.location/LocationSettingsActivity",
        "name": "Location Settings",
        "description": "Location permissions, GPS toggle, location services, and location accuracy settings",
        "message": "Turn on or turn off location services and manage application location permissions",
        "qna_description": "How to fix location accuracy or enable location service",
        "classes": "LocationSettingsActivity",
        "controlType": "toggle",
        "category": "auto",
    },
    {
        "id": "dl_wifi_01",
        "uri": "bixby://com.samsung.android.settings.wifi/WifiSettingsActivity",
        "name": "Wi-Fi Settings",
        "description": "Wi-Fi connection, network scan, saved Wi-Fi networks, and Wi-Fi direct configurations",
        "message": "Connect to Wi-Fi networks and resolve network connectivity issues",
        "qna_description": "Fix Wi-Fi not connecting or network dropping",
        "classes": "WifiSettingsActivity",
        "controlType": "toggle",
        "category": "auto",
    },
    {
        "id": "dl_bluetooth_01",
        "uri": "bixby://com.samsung.android.settings.bluetooth/BluetoothSettingsActivity",
        "name": "Bluetooth Settings",
        "description": "Bluetooth device pairing, bluetooth toggle, connected devices, and audio codec settings",
        "message": "Pair new Bluetooth devices or disconnect existing devices",
        "qna_description": "Pair bluetooth earphone or fix bluetooth discovery issue",
        "classes": "BluetoothSettingsActivity",
        "controlType": "toggle",
        "category": "auto",
    },
    {
        "id": "dl_display_01",
        "uri": "bixby://com.samsung.android.settings.display/DisplaySettingsActivity",
        "name": "Display Settings",
        "description": "Screen brightness, dark mode, motion smoothness refresh rate, screen timeout, font size, and eye comfort shield",
        "message": "Adjust display parameters, refresh rate, or dark mode",
        "qna_description": "Fix screen flickering or battery drain due to refresh rate",
        "classes": "DisplaySettingsActivity",
        "controlType": "slider",
        "category": "auto",
    },
    {
        "id": "dl_battery_01",
        "uri": "bixby://com.samsung.android.settings.battery/BatteryProtectionActivity",
        "name": "Battery Protection Settings",
        "description": "Battery usage details, power saving mode, battery protection limit, fast charging toggle, and background app limits",
        "message": "Manage battery drain, protect battery health, and configure power saving mode",
        "qna_description": "Fix fast battery drain or configure power saver",
        "classes": "BatteryProtectionActivity",
        "controlType": "toggle",
        "category": "auto",
    },
    {
        "id": "dl_apps_01",
        "uri": "bixby://com.samsung.android.settings.apps/AppListActivity",
        "name": "Apps Management",
        "description": "App permissions, force stop apps, clear app cache, clear app data, and default application management",
        "message": "Manage installed applications, permissions, and app storage cache",
        "qna_description": "Clear app cache or reset app permissions",
        "classes": "AppListActivity",
        "controlType": "list",
        "category": "auto",
    },
    {
        "id": "dl_reset_network_01",
        "uri": "bixby://com.samsung.android.settings.reset/ResetNetworkSettingsActivity",
        "name": "Reset Mobile Network Settings",
        "description": "Reset Wi-Fi, Mobile Data, and Bluetooth settings to factory defaults",
        "message": "Reset network configurations to fix persistent connectivity issues",
        "qna_description": "Reset all network settings to fix no service or connection errors",
        "classes": "ResetNetworkSettingsActivity",
        "controlType": "button",
        "category": "critical",
    },
    {
        "id": "dl_reset_factory_01",
        "uri": "bixby://com.samsung.android.settings.reset/FactoryDataResetActivity",
        "name": "Factory Data Reset",
        "description": "Erase all data and reset phone to original factory default settings",
        "message": "Completely wipe device storage and restore initial factory image",
        "qna_description": "Perform full factory reset as last resort",
        "classes": "FactoryDataResetActivity",
        "controlType": "button",
        "category": "critical",
    },
]


def load_deeplink_catalog(file_path: Optional[str] = None) -> DeeplinkCatalog:
    """Load deeplink records from JSON file or return fallback catalog."""
    records: List[DeeplinkRecord] = []
    
    if file_path and Path(file_path).is_file():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                items = data.get("deeplinks", data) if isinstance(data, dict) else data
                for item in items:
                    rec_id = str(item.get("id") or item.get("record_id") or f"dl_{len(records)}")
                    uri = item.get("uri") or item.get("baseDeeplink", {}).get("uri", "")
                    if not uri:
                        continue
                    records.append(
                        DeeplinkRecord(
                            record_id=rec_id,
                            uri=uri,
                            name=item.get("name") or item.get("title") or rec_id,
                            description=item.get("description", ""),
                            message=item.get("message", ""),
                            qna_description=item.get("qna_description", ""),
                            classes=item.get("classes", ""),
                            control_type=item.get("controlType", ""),
                            original_type=item.get("originalType", ""),
                            category=item.get("category", "auto"),
                        )
                    )
        except Exception as e:
            records = []

    if not records:
        for item in FALLBACK_DEEPLINKS:
            records.append(
                DeeplinkRecord(
                    record_id=item["id"],
                    uri=item["uri"],
                    name=item["name"],
                    description=item["description"],
                    message=item.get("message", ""),
                    qna_description=item.get("qna_description", ""),
                    classes=item.get("classes", ""),
                    control_type=item.get("controlType", ""),
                    category=item.get("category", "auto"),
                )
            )

    return DeeplinkCatalog(records)
