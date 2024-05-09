import os, json

tags = json.loads(os.environ["INPUT_TAGS"])

print(tags)
print(type(tags))

print()

for tag in tags:
    print(f"Key {tag['Key']} has value {tag['Value']}\n")