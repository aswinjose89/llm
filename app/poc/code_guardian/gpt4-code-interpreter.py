
import openai

openai.api_key = "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"

# confirm authentication was successful
openai.Engine.list()['data'][0]


assistant = openai.ChatCompletion.create(
  instructions="You are a personal math tutor. When asked a math question, write and run code to answer the question.",
  model="gpt-4-1106-preview",
  tools=[{"type": "code_interpreter"}]
)
import pdb;pdb.set_trace()
print(assistant)