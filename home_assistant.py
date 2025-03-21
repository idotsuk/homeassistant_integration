import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BAE_URL = os.getenv("HOME_ASSISTANT_BAE_URL")
AUTH_TOEKN = os.getenv("HOME_ASSISTANT_TOEKN")

headers = {
    "Authorization": f"Bearer {AUTH_TOEKN}",
    "Content-Type": "application/json",
}

paths = {"services": "api/services", "states": "api/states"}
devices_path = {"media_player": "media_player"}
devices = {"TV": "media_player.samsung_7_series_55"}
commands = {"tv_toggle_on_of": "turn_off"}


def get_all_devices():
    """
    Get all devices from Home Assistant API
    """
    url = f"{BAE_URL}/{paths['states']}"
    return requests.get(url, headers=headers).json()


def toggle_tv_on_off():
    """
    Toggle the TV on/off
    """
    url = f"{BAE_URL}/{paths['services']}/{devices_path['media_player']}/{commands['tv_toggle_on_of']}"
    body = {"entity_id": devices["TV"]}
    response = requests.post(url, headers=headers, json=body)
    return response.json() if response.content else {"status": "success"}


# Example usage
if __name__ == "__main__":
    all_devices = get_all_devices()
    print(all_devices)
    
    toggle_response = toggle_tv_on_off()
    print(toggle_response) 