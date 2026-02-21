from openai import OpenAI
from apikeys import openrouter_api

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key = openrouter_api
  )

completion = client.chat.completions.create(
  model="arcee-ai/trinity-large-preview:free",
  messages=[
    {"role": "system", "content": "You are a virtual assistant named jarvis skilled in general tasks like Alexa and Google Cloud"},
    {"role": "user", "content": "what is coding"}
  ]
)

print(completion.choices[0].message.content)