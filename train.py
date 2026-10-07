import json

with open("intens.json", "r") as f:
    intents = json.load(f)

print(intents)
