#!/usr/bin/env python3

"""
Tests for messaging protocol used between server and drone
"""

# from drone import Message
from mesh import data

drone_data_1 = data.Data(drone_id="drone_1", action='start')

print(drone_data_1)
