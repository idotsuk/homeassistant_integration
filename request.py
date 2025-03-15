OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"

def query_llm(prompt, model="mistral"):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_ENDPOINT, json=payload)
    response.raise_for_status()
    return response.json()['response']

# Example usage:
result = query_llm("Turn on the living room lights.")
print(result)