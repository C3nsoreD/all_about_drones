#! /usr/bin/env python3

"""
Data is a representation of data sent between drones.
Making it an object allows for easier implementation and maintanence.
"""
import json


class Data:
    def __init__(self, drone_id, action, header=None):
        self.data = {}
        self.data['drone_id'] = drone_id
        self.data['header']  = header if header != None else self._create_header(action)
        self.data['message'] = 'Nothing'

    def __str__(self):
        return json.dumps(self.__dict__, indent=2, separators=(',', ': '))

    def _create_header(self, action, _from=None, _to=None):
        # Responsible for creating the message header
        # useful for message packaging.
        _hdr = {
            'from': _from,
            'to': _to,
            'action': action,
        }
        return _hdr
