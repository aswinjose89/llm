from openai import OpenAI
client = OpenAI()


prompt= """
Get a code fix for given vulnerable code\ndef unsafe_query(database, user_input):\n    return database.execute(\"SELECT * FROM users WHERE name = '\" + user_input + \"';\")
"""
response = client.completions.create(
  model="ft:davinci-002:quantum-ventura::8hHVVxiq",
  prompt=prompt,
  temperature=1,
  max_tokens=1000,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
)

print(response)