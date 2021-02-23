#!/usr/bin/env python3
import constants
import numpy as np
import math
import scipy.integrate
import time
import datetime
import threading

from constants import Constants


class Propeller:
    def __init__(self):
        self.dia = Constants.PROP_DIA
        self.pitch = Constants.PROP_PITCH
        self.speed = 0 # RPM
        self.thrust = 0

    def set_speed(self,speed):
        self.speed = speed
        self.thrust = 4.392e-8 * self.speed * math.pow(self.dia,3.5)/(math.sqrt(self.pitch))
        self.thrust = self.thrust*(4.23e-4 * self.speed * self.pitch)


class Quadcopter:
    def __init__(self, n_quads):
        self.quads = n_quads
        self.thread_object = None
        self.ode = scipy.integrate.ode(self.state_dot).set_integrator('vode', nsteps=500, method='bdf')
        self.time = datetime.datetime.now()
        # Initialize all the params for all drones defined in quads.
        for key in self.quads:
            self.quads[key]['state'] = np.zeros(12)
            # Initail pose
            self.quads[key]['state'] = self.quads[key]['position']
            self.quads[key]['state'] = self.quads[key]['orientation']
            # initialze propellers
            self.quads[key]['m1'] = Propeller()
            self.quads[key]['m2'] = Propeller()
            self.quads[key]['m3'] = Propeller()
            self.quads[key]['m4'] = Propeller()
            # Structual compenents
            i_xx = ((2*Constants.WEIGHT*Constants.R**2)/5) + (2*Constants.WEIGHT*Constants.L**2)
            i_yy = i_xx
            i_zz = ((2*Constants.WEIGHT*Constants.R**2)/5) + (4*Constants.WEIGHT*Constants.L**2)
            self.quads[key]['I'] = np.array([
                [i_xx, 0, 0], [0, i_yy, 0], [0, 0, i_zz]
            ])
            self.quads[key]['invI'] = np.linalg.inv(self.quads[key]['I'])
        self.run = True

    def rotation_matrix(self, angles):
        ct, cp, cg = [math.cos(i) for i in angles]
        st, sp, sg = [math.sin(i) for i in angles]
        R_x = np.array([[1,0,0],[0,ct,-st],[0,st,ct]])
        R_y = np.array([[cp,0,sp],[0,1,0],[-sp,0,cp]])
        R_z = np.array([[cg,-sg,0],[sg,cg,0],[0,0,1]])

        R = np.dot(R_z, np.dot( R_y, R_x ))

        return R

    def wrap_angle(self, val):
        # Helper function for returns angles in deg
        return ((val + np.pi) % (2*np.pi) - np.pi)

    def state_dot(self, time, state, key):
        state_dot = np.zeros(12)
        breakpoint()
        state_dot[0:3] = [self.quads[key]['state'][i] for i in range(3, 6)]
        x_ddot = np.array([0, 0, -Constants.GRAVITY]) + \
            np.dot(
                self.rotation_matrix(
                    self.quads[key]['state'][6:9]), np.array([0, 0, (self.quads[key]['m1'].thrust +self.quads[key]['m2'].thrust+self.quads[key]['m3'].thrust+self.quads[key]['m4'].thrust)]
                    )
                ) / Constants.WEIGHT
        state_dot[3:6] = [x_ddot[i] for i in range(3)]
        state_dot[6:9] = [self.quads[key]['state'][i] for i in range(9, 12)]
        # Angular acceleration
        omega = self.quads[key]['state'][9:12]
        tau = np.array(
            [Constants.L*(self.quads[key]['m1'].thrust - self.quads[key]['m3.'].thrust), Constants.L*(self.quads[key]['m2'].thrust - self.quads[key]['m4'].thrust), Constants.B*(self.quads[key]['m1'].thrust - self.quads[key]['m2'].thrust + self.quads[key]['m3'].thrust - self.quads[key]['m4'].thrust)]
        )
        omega_dot = np.dot(self.quads[key]['invI'], (tau - np.cross(omega, np.dot(self.quads[key]['I'], omega))))
        state_dot[9:] = [omega[i] for i in range(3)]

        return state_dot

    def update(self, dt):

        for key in self.quads:
            self.ode.set_initial_value(self.quads[key]['state'], 0).set_f_params(key)
            self.quads[key]['state'] = self.ode.integrate(self.ode.t + dt)
            self.quads[key]['state'][6:9] = self.wrap_angle(self.quads[key]['state'][6:9])
            self.quads[key]['state'][2] = max(0, self.quads[key]['state'][2])


    def set_motor_speeds(self, quad, speeds):
        props = ['m1', 'm2', 'm3', 'm4']
        for props, i in zip(props, speeds):
            self.quads[quad][props].set_speed(speeds[i])


    def get_position(self, quad):
        return self.quads[quad]['state'][0:3]

    def get_linear_rate(self, quad):
        return self.quads[quad]['state'][3:6]

    def get_orientation(self, quad):
        return self.quads[quad]['state'][6:9]

    def get_angular_rate(self, quad):
        return self.quads[quad]['state'][9:12]

    def get_state(self, quad):
        return self.quads[quad]['state']

    def set_position(self, quad, position):
        self.quads[quad]['state'][0:3] = position[:]

    def set_orientation(self, quad, orientation):
        self.quads[quad]['state'][6:9] = orientation[:]

    def get_time(self):
        return self.time

    def thread_run(self, dt, time_scaling):
        rate = time_scaling * dt
        last_update = self.time
        while(self.run):
            time.sleep(0)
            self.time = datetime.datetime.now()
            if (self.time - last_update).total_seconds() > rate:
                self.update(dt)
                last_update = self.time

    def start_thread(self, dt=0.0002, time_scaling=1):
        self.thread_object = threading.Thread(target=self.thread_run, args=(dt, time_scaling), daemon=True)
        self.thread_object.start()

    def stop_thread(self):
        self.run = False
