import os, json

tags = json.loads(os.environ["INPUT_TAGS"])

print(tags)
print(type(tags))