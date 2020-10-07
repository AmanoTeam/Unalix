import json

from ._config import data

with open(f"{data}/arguments.json", mode="r", encoding="utf-8") as arguments:
    arguments = json.loads(arguments.read())