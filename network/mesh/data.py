"""
Data is a representation of data sent between drones.
Making it an object allows for easier implementation and maintanence.
"""
import json


class Data:
    def __init__(self, drone_id=None, action=None):
        self.data = {}
        self.data["drone_id"] = drone_id
        self.data["header"]  = action
        self.data["message"] = {}

    def __repr__(self):
        return f"Data from {self.data[drone_id]}\n"

    def __str__(self):
        _print = self.__repr__() + str(self.data[message])
        parsed = json.loads(_print)
        return json.dumps(parsed, indent=2, sort_keys=False)
