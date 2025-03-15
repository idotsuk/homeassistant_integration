import os
import json
from typing import List, Dict, Any
from pydantic import BaseModel, Field, ValidationError

import openai  # requires openai>=1.0.0


# -----------------------------------------------------------------
# 1) Define a Pydantic Model for Home Assistant Commands
# -----------------------------------------------------------------
class HomeAssistantCommand(BaseModel):
    action: str
    devices: List[str] = Field(default_factory=list)
    params: Dict[str, Any] = Field(default_factory=dict)


# -----------------------------------------------------------------
# 2) LLM Function Using the New OpenAI API (>=1.0.0)
# -----------------------------------------------------------------
def generate_ha_command(user_input: str, model: str = "gpt-3.5-turbo") -> HomeAssistantCommand:
    """
    Takes a user input like 'Turn on the living room light' and returns
    a validated HomeAssistantCommand via the new ChatCompletion API.
    """

    # Set your API key (replace with your real key or environment variable)
    openai.api_key = os.getenv("OPENAI_API_KEY", "sk-REPLACE_ME")

    # Prompt: instruct the LLM to output strictly valid JSON matching our schema
    system_message = (
        "You are a helpful assistant that outputs ONLY valid JSON with the following schema:\n\n"
        "HomeAssistantCommand:\n"
        "  action (str)\n"
        "  devices (list of strings)\n"
        "  params (dict)\n\n"
        "Constraints:\n"
        "  - Do not include markdown, code blocks, or extra text.\n"
        "  - Output must be strictly valid JSON, nothing else.\n"
        "  - If unsure, make a best guess.\n"
    )

    user_message = (
        f"The user said: {user_input}\n"
        "Return a JSON object matching the schema above."
    )

    # Call the new ChatCompletion interface
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        temperature=0.0,  # 0.0 for the most deterministic response
    )

    # Extract the raw text (JSON) from the LLM
    raw_json = response.choices[0].message.content.strip()

    # -----------------------------------------------------------------
    # 3) Parse the JSON and Validate with Pydantic
    # -----------------------------------------------------------------
    try:
        data = json.loads(raw_json)  # Convert JSON string → dict
        command = HomeAssistantCommand(**data)  # Validate
        return command
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to decode JSON. LLM Output:\n{raw_json}") from e
    except ValidationError as e:
        raise ValueError(f"LLM JSON does not match the HomeAssistantCommand schema:\n{e}") from e


# -----------------------------------------------------------------
# 4) Example Usage
# -----------------------------------------------------------------
if __name__ == "__main__":
    user_request = "Turn on the living room light"
    ha_command = generate_ha_command(user_request)
    print("Parsed Home Assistant command:")
    print(ha_command.dict())
