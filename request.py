import json
import requests
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ValidationError


# Define the allowed request types with descriptions embedded in the enum.
class RequestType(str, Enum):
    CONVERSATIONAL = ("conversational", "For general inquiries or instructions.")
    DEVICE_CHANGE = ("device_change", "For adding or removing devices.")
    PRESET_CHANGE = ("preset_change", "For adding, removing, or modifying presets/scenes.")
    DEVICE_ACTION = ("device_action", "For turning devices on/off or performing direct actions.")

    def __new__(cls, value, description):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        return obj


# Pydantic model for the classification result.
class RequestClassification(BaseModel):
    request_type: RequestType
    description: Optional[str] = None


def llm_classification_request(
        user_input: str,
        mistral_endpoint: str = "http://localhost:11434/api/generate",
        model_name: str = "mistral",
        max_retries: int = 3
) -> RequestClassification:
    # Dynamically generate allowed request types from the enum.
    allowed_requests = "\n".join(
        [f"{rt.value}: {rt.description}" for rt in RequestType]
    )

    system_instructions = (
        "You are a helpful assistant that categorizes Home Assistant requests into one of the following types:\n"
        f"{allowed_requests}\n\n"
        "Return a JSON object with two fields:\n"
        "  'request_type': one of the above request types (only the key, e.g., 'device_action')\n"
        "  'description': a short explanation for your classification.\n"
        "Output ONLY the JSON without any extra text or markdown."
    )

    full_prompt = f"{system_instructions}\nUser input: {user_input}\n"

    payload = {
        "model": model_name,
        "prompt": full_prompt,
        "temperature": 0.0,
        "stream": False
    }

    for attempt in range(1, max_retries + 1):
        print(f"Attempt #{attempt} to classify request...")
        try:
            response = requests.post(mistral_endpoint, json=payload)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"HTTP error contacting LLM: {e}")
            continue

        try:
            content = response.json()
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from LLM response: {e}")
            continue

        if "response" not in content:
            print("LLM response missing 'response' field:")
            print(content)
            continue

        raw_text = content["response"].strip()
        print("LLM raw classification output:")
        print(raw_text)

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM output as JSON: {e}")
            print("LLM returned:")
            print(raw_text)
            continue

        try:
            classification = RequestClassification(**data)
            print("Successfully classified the request!")
            return classification
        except ValidationError as e:
            print("❌ Schema validation error:")
            print(e)
            print("Data returned by LLM:")
            print(json.dumps(data, indent=2))
            continue

    raise ValueError(f"Failed to classify request after {max_retries} attempt(s).")


# --- Handler for device action requests (renamed from 'action_request') ---
def handle_device_action_request(user_input: str):
    print("Handling device action request...")
    print(f"User input: {user_input}")
    # Stub: Here you would implement the logic to process a device action
    print("Stub: Executing device action (e.g., turning device on/off).")


# --- Dispatcher / Main Flow ---
def dispatch_request(user_input: str):
    try:
        classification = llm_classification_request(user_input)
    except ValueError as e:
        print("Error classifying request:", e)
        return

    print(f"Request classified as: {classification.request_type}")
    print(f"LLM explanation: {classification.description}")

    if classification.request_type == RequestType.DEVICE_ACTION:
        handle_device_action_request(user_input)
    else:
        print("Only device action requests are implemented at this time.")


if __name__ == "__main__":
    user_input = input("Enter your Home Assistant request: turn on the main light")
    dispatch_request(user_input)
