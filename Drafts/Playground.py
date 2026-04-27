
import json


file_types = ""

with open('FileNameInformation.json', 'r', encoding='utf-8') as file:
    file_types = json.load(file)

print(file_types)

# Uses the 'id' attribute as the key and the object as the value
object_dict = {obj['Identifier']: obj for obj in file_types}

print(object_dict)

# write to file
with open('FileTypes.json', 'w', encoding='utf-8') as file:
    object_dict_json = json.dumps(object_dict, indent=4)
    file.write(object_dict_json)

# read from file
with open("FileTypes.json", "r", encoding='utf-8') as file:
    file_types = json.load(file)

print()
print()
print(object_dict["PY"])

