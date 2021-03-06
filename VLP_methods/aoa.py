from Bound_Estimation.matfile_read import load_mat, rec_func
import math
import numpy as np
"""
*: coordinate center of cari

|--------|                     
| car1   |                      
|-------*|
         |
       y |                   |---------|
         |                   |  car2   |
         |-------------------|*--------|
                    d

"""
# loading the coefficients of piecewise continous transfer function
# breaks: the limits where corresponding coeeficients valid.
# coefs: corresponding coeefficients within that boundary.
data = load_mat('VLP_methods/aoa_transfer_function.mat')
rec_func(data, 0)
breaks = np.array(data['transfer_function']['breaks'])
coefficients = np.array(data['transfer_function']['coefs'])


class AoA:
    def __init__(self, a_m=2, f_m1=1000000, f_m2=2000000, measure_dt=5e-6, vehicle_dt=1e-2, w0=500, hbuf=1000,
                 car_dist=1.6, fov=80):
        # this where parameters are initialized according to input or set values.
        self.dt = measure_dt
        self.t = np.arange(0, vehicle_dt - self.dt, self.dt)
        self.w1 = 2 * math.pi * f_m1
        self.w2 = 2 * math.pi * f_m2
        self.a_m = a_m
        self.w0 = w0
        self.hbuf = hbuf
        self.car_dist = car_dist
        self.e_angle = fov

    # %%

    def estimate(self, delays, H_q, noise_variance):
        # In this function according to voltage readings in each quadrant and noise theta and pose estimation is calculated.
        # signal generated according to frequencies.
        s1_w1 = self.a_m * np.cos(self.w1 * self.t)
        s2_w2 = self.a_m * np.cos(self.w2 * self.t)

        # after going through ADC at receiver
        r1_w1_a = H_q[0][0][0] * np.cos(self.w1 * (self.t - delays[0][0])) + np.random.normal(0, math.sqrt(
            noise_variance[0][0][0]), len(self.t))
        r1_w1_b = H_q[0][0][1] * np.cos(self.w1 * (self.t - delays[0][0])) + np.random.normal(0, math.sqrt(
            noise_variance[0][0][1]), len(self.t))
        r1_w1_c = H_q[0][0][2] * np.cos(self.w1 * (self.t - delays[0][0])) + np.random.normal(0, math.sqrt(
            noise_variance[0][0][2]), len(self.t))
        r1_w1_d = H_q[0][0][3] * np.cos(self.w1 * (self.t - delays[0][0])) + np.random.normal(0, math.sqrt(
            noise_variance[0][0][3]), len(self.t))

        r2_w1_a = H_q[0][1][0] * np.cos(self.w1 * (self.t - delays[0][1])) + np.random.normal(0, math.sqrt(
            noise_variance[0][1][0]), len(self.t))
        r2_w1_b = H_q[0][1][1] * np.cos(self.w1 * (self.t - delays[0][1])) + np.random.normal(0, math.sqrt(
            noise_variance[0][1][1]), len(self.t))
        r2_w1_c = H_q[0][1][2] * np.cos(self.w1 * (self.t - delays[0][1])) + np.random.normal(0, math.sqrt(
            noise_variance[0][1][2]), len(self.t))
        r2_w1_d = H_q[0][1][3] * np.cos(self.w1 * (self.t - delays[0][1])) + np.random.normal(0, math.sqrt(
            noise_variance[0][1][3]), len(self.t))

        r1_w2_a = H_q[1][0][0] * np.cos(self.w2 * (self.t - delays[1][0])) + np.random.normal(0, math.sqrt(
            noise_variance[1][0][0]), len(self.t))
        r1_w2_b = H_q[1][0][1] * np.cos(self.w2 * (self.t - delays[1][0])) + np.random.normal(0, math.sqrt(
            noise_variance[1][0][1]), len(self.t))
        r1_w2_c = H_q[1][0][2] * np.cos(self.w2 * (self.t - delays[1][0])) + np.random.normal(0, math.sqrt(
            noise_variance[1][0][2]), len(self.t))
        r1_w2_d = H_q[1][0][3] * np.cos(self.w2 * (self.t - delays[1][0])) + np.random.normal(0, math.sqrt(
            noise_variance[1][0][3]), len(self.t))

        r2_w2_a = H_q[1][1][0] * np.cos(self.w2 * (self.t - delays[1][1])) + np.random.normal(0, math.sqrt(
            noise_variance[1][1][0]), len(self.t))
        r2_w2_b = H_q[1][1][1] * np.cos(self.w2 * (self.t - delays[1][1])) + np.random.normal(0, math.sqrt(
            noise_variance[1][1][1]), len(self.t))
        r2_w2_c = H_q[1][1][2] * np.cos(self.w2 * (self.t - delays[1][1])) + np.random.normal(0, math.sqrt(
            noise_variance[1][1][2]), len(self.t))
        r2_w2_d = H_q[1][1][3] * np.cos(self.w2 * (self.t - delays[1][1])) + np.random.normal(0, math.sqrt(
            noise_variance[1][1][3]), len(self.t))

        # eps readings will be calculated, so we initalized them to be empty np array.
        eps_a_s1, eps_b_s1, eps_c_s1, eps_d_s1, phi_h_s1 = np.array([0., 0.]), np.array(
            [0., 0.]), np.array([0., 0.]), np.array([0., 0.]), np.array([0., 0.])
        eps_a_s2, eps_b_s2, eps_c_s2, eps_d_s2, phi_h_s2 = np.array([0., 0.]), np.array(
            [0., 0.]), np.array([0., 0.]), np.array([0., 0.]), np.array([0., 0.])
        theta_l_r = np.array([[0., 0.], [0., 0.]]).astype(float)

        # the calculation of epsilon values for each quadrant. s1, s2 means right and left light.
        eps_a_s1[0] = np.sum(
            np.dot(r1_w1_a[self.w0: self.w0 + self.hbuf], s1_w1[self.w0: self.w0 + self.hbuf])) / self.hbuf
        eps_b_s1[0] = np.sum(
            np.dot(r1_w1_b[self.w0: self.w0 + self.hbuf], s1_w1[self.w0: self.w0 + self.hbuf])) / self.hbuf
        eps_c_s1[0] = np.sum(
            np.dot(r1_w1_c[self.w0: self.w0 + self.hbuf], s1_w1[self.w0: self.w0 + self.hbuf])) / self.hbuf
        eps_d_s1[0] = np.sum(
            np.dot(r1_w1_d[self.w0: self.w0 + self.hbuf], s1_w1[self.w0: self.w0 + self.hbuf])) / self.hbuf
        eps_a_s1[1] = np.sum(
            np.dot(r2_w1_a[self.w0: self.w0 + self.hbuf], s1_w1[self.w0: self.w0 + self.hbuf])) / self.hbuf
        eps_b_s1[1] = np.sum(
            np.dot(r2_w1_b[self.w0: self.w0 + self.hbuf], s1_w1[self.w0: self.w0 + self.hbuf])) / self.hbuf
        eps_c_s1[1] = np.sum(
            np.dot(r2_w1_c[self.w0: self.w0 + self.hbuf], s1_w1[self.w0: self.w0 + self.hbuf])) / self.hbuf
        eps_d_s1[1] = np.sum(
            np.dot(r2_w1_d[self.w0: self.w0 + self.hbuf], s1_w1[self.w0: self.w0 + self.hbuf])) / self.hbuf

        eps_a_s2[0] = np.sum(
            np.dot(r1_w2_a[self.w0: self.w0 + self.hbuf], s2_w2[self.w0: self.w0 + self.hbuf])) / self.hbuf
        eps_b_s2[0] = np.sum(
            np.dot(r1_w2_b[self.w0: self.w0 + self.hbuf], s2_w2[self.w0: self.w0 + self.hbuf])) / self.hbuf
        eps_c_s2[0] = np.sum(
            np.dot(r1_w2_c[self.w0: self.w0 + self.hbuf], s2_w2[self.w0: self.w0 + self.hbuf])) / self.hbuf
        eps_d_s2[0] = np.sum(
            np.dot(r1_w2_d[self.w0: self.w0 + self.hbuf], s2_w2[self.w0: self.w0 + self.hbuf])) / self.hbuf
        eps_a_s2[1] = np.sum(
            np.dot(r2_w2_a[self.w0: self.w0 + self.hbuf], s2_w2[self.w0: self.w0 + self.hbuf])) / self.hbuf
        eps_b_s2[1] = np.sum(
            np.dot(r2_w2_b[self.w0: self.w0 + self.hbuf], s2_w2[self.w0: self.w0 + self.hbuf])) / self.hbuf
        eps_c_s2[1] = np.sum(
            np.dot(r2_w2_c[self.w0: self.w0 + self.hbuf], s2_w2[self.w0: self.w0 + self.hbuf])) / self.hbuf
        eps_d_s2[1] = np.sum(
            np.dot(r2_w2_d[self.w0: self.w0 + self.hbuf], s2_w2[self.w0: self.w0 + self.hbuf])) / self.hbuf
        # phi values will be used to estimate thetas.
        phi_h_s1[0] = ((eps_b_s1[0] + eps_d_s1[0]) - (eps_a_s1[0] + eps_c_s1[0])) / (
                eps_a_s1[0] + eps_b_s1[0] + eps_c_s1[0] + eps_d_s1[0])
        phi_h_s1[1] = ((eps_b_s1[1] + eps_d_s1[1]) - (eps_a_s1[1] + eps_c_s1[1])) / (
                eps_a_s1[1] + eps_b_s1[1] + eps_c_s1[1] + eps_d_s1[1])
        phi_h_s2[0] = ((eps_b_s2[0] + eps_d_s2[0]) - (eps_a_s2[0] + eps_c_s2[0])) / (
                eps_a_s2[0] + eps_b_s2[0] + eps_c_s2[0] + eps_d_s2[0])
        phi_h_s2[1] = ((eps_b_s2[1] + eps_d_s2[1]) - (eps_a_s2[1] + eps_c_s2[1])) / (
                eps_a_s2[1] + eps_b_s2[1] + eps_c_s2[1] + eps_d_s2[1])
        # transfer function takes calculated phi and returns theta. theta_l_r[0] means s1, theta_l_r[:][0] means left.
        theta_l_r[0][0] = self.transfer_function(phi_h_s1[0]) * np.pi / 180
        theta_l_r[0][1] = self.transfer_function(phi_h_s1[1]) * np.pi / 180
        theta_l_r[1][0] = self.transfer_function(phi_h_s2[0]) * np.pi / 180
        theta_l_r[1][1] = self.transfer_function(phi_h_s2[1]) * np.pi / 180
        # pose estimations is made here with the usage of theta_l_r
        diff_1 = theta_l_r[0][0] - theta_l_r[0][1]
        t_x_1 = self.car_dist * (
                    1 + (math.sin(theta_l_r[0][1]) * math.cos(theta_l_r[0][0])) / (math.sin(diff_1))) if math.sin(
            diff_1) != 0 else None
        t_y_1 = self.car_dist * (
                    (math.cos(theta_l_r[0][1]) * math.cos(theta_l_r[0][0])) / (math.sin(diff_1))) if math.sin(
            diff_1) != 0 else None
        diff_2 = theta_l_r[1][0] - theta_l_r[1][1]
        t_x_2 = self.car_dist * (
                    1 + (math.sin(theta_l_r[1][1]) * math.cos(theta_l_r[1][0])) / (math.sin(diff_2))) if math.sin(
            diff_2) != 0 else None
        t_y_2 = self.car_dist * (
                    (math.cos(theta_l_r[1][1]) * math.cos(theta_l_r[1][0])) / (math.sin(diff_2))) if math.sin(
            diff_2) != 0 else None
        # this change of coordinates made for plotting in the same frame with other VLP_methods.
        tx_pos = self.change_cords(np.array([[t_x_1, t_y_1], [t_x_2, t_y_2]]))
        return tx_pos

    def find_nearest(self, array, value):
        # takes the array and returns the index of nearest one from specified value.
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return idx, array[idx]

    def transfer(self, coefficient, x, x1):
        # this is equation for piecewise transfer functipn.
        return (coefficient[0] * (x - x1) ** 3) + (coefficient[1] * (x - x1) ** 2) + (coefficient[2] * (x - x1) ** 1) + \
               coefficient[3]

    def transfer_function(self, phi):
        # since transfer function valid in boundary, we need to check that it is valid or not. IF it is higher than
        # limit it returns the max. boundary
        phi = 1.0000653324773283 if phi >= 1.0000653324773283 else phi
        phi = -1.0000980562352184 if phi <= -1.0000980562352184 else phi

        idx, lower_endpoint = self.find_nearest(breaks, phi)
        coefficient = coefficients[idx]
        return self.transfer(coefficient, phi, lower_endpoint)

    def change_cords(self, txpos):
        # changing coordinates as x->-y, y->x
        t_tx_pos = np.copy(txpos)
        t_tx_pos[0][0] = -txpos[0][1]
        t_tx_pos[1][0] = txpos[0][0]
        t_tx_pos[0][1] = -txpos[1][1]
        t_tx_pos[1][1] = txpos[1][0]
        return t_tx_pos
