import json

with open("file.json") as json_file:
    json_data = json.load(json_file)
    print(json_data)
    print(json_data['nodes'])