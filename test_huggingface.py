import requests
import json
from keys import HUGGING_FACE_KEY

url = "https://api-inference.huggingface.co/models/openchat_3.5"
url = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {HUGGING_FACE_KEY}"
}
data = {
    "inputs": {
        "messages": [{"role": "user", "content": "You are a large language model named OpenChat. Write a poem to describe yourself"}]
    }
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.json())

# def query_asr(filename):
#     with open(filename, "rb") as f:
#         data = f.read()
#     response = requests.post(
#         "https://api-inference.huggingface.co/models/openai/whisper-large-v3", 
#         headers=headers, 
#         data=data
#     )
#     return response.json()