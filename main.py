import os
from dotenv import load_dotenv
import requests

load_dotenv()

BAE_URL = os.getenv("HOME_ASSISTANT_BAE_URL")
AUTH_TOEKN = GCP_PROJECT_ID = os.getenv("HOME_ASSISTANT_TOEKN")

headers = {
    "Authorization": f"Bearer {AUTH_TOEKN}",
    "Content-Type": "application/json",
}

paths = {"services": "api/services", "states": "api/states"}
devices_path = {"media_player": "media_player"}
devices = {"TV": "media_player.samsung_7_series_55"}
commands = {"tv_toggle_on_of": "turn_off"}


def get_all_devices():
    url = f"{BAE_URL}/{paths['states']}"
    return requests.get(url, headers=headers).json()


all_devices = get_all_devices()
print(all_devices)


def toggle_tv_on_off():
    url = f"{BAE_URL}/{paths['services']}/{devices_path['media_player']}/{commands['tv_toggle_on_of']}"
    body = {"entity_id": devices["TV"]}
    requests.post(url, headers=headers, json=body)


toggle_tv_on_off()