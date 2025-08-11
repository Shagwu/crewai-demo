# main.py
import requests

def chat_with_qwen(prompt):
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "qwen:7b",
        "stream": False,  # force Ollama to send one JSON object
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

        if "message" in data and "content" in data["message"]:
            return data["message"]["content"]
        else:
            return data
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Ollama: {e}"

if __name__ == "__main__":
    prompt = "Say hello from Qwen"
    answer = chat_with_qwen(prompt)
    print("Qwen says:", answer)