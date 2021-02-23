#!/usr/bin/env python3

from Quad import Quadcopter
from constants import Constants


GOALS = []
QUADCOPTER={
    'q1' : {
        'position':[1,0,4],'orientation':[0,0,0]
    },
}
quad = Quadcopter(QUADCOPTER)

quad.start_thread(dt=Constants.QUAD_DYNAMICS_UPDATE,time_scaling=Constants.TIME_SCALING)
