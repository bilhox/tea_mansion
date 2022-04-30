import json

a = open("./assets/levels/level_demo.json")
print(json.loads(a.read()))