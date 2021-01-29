from CRLB_init import *
from matfile_read import load_mat
from glob import glob
import math
import matplotlib.pyplot as plt

# Roberts' method, CRLB calculation for a single position estimation
def roberts_crlb_single_instance(crlb_obj, tx1, tx2, delays, curr_t, dt_vhc, max_pow, sig_freq, meas_dt, T, i_bg, noise_factors, powers):
    flag = False
    fim = np.zeros(shape=(2,2))

    for param1, param2 in zip(range(2), range(2)):
        for i in range(2):
            for j in range(2):
                ij = (i + 1)*10 + (j + 1)
                E_1, E_2, E_3 = signal_generator(curr_t, dt_vhc, max_pow, sig_freq, delays[i][j], meas_dt)
                h_ij = crlb_obj.get_h_ij(ij, tx1, tx2, flag)
                dh_dk1 = crlb_obj.get_d_hij_d_param(param1 + 1, ij, tx1, tx2, flag)
                dh_dk2 = crlb_obj.get_d_hij_d_param(param2 + 1, ij, tx1, tx2, flag)
                dtau_dk1 = crlb_obj.get_d_tau_d_param(param1 + 1, ij, tx1, tx2, flag)
                dtau_dk2 = crlb_obj.get_d_tau_d_param(param2 + 1, ij, tx1, tx2, flag)

                dh_dk1_dh_dk2 = dh_dk1 * dh_dk2
                h_dh_dk1_dtau_dk2 = - h_ij * dh_dk1 * dtau_dk2
                h_dh_dk2_dtau_dk1 = - h_ij * dh_dk2 * dtau_dk1
                hsq_dtau_dk1_dtau_dk2 = h_ij ** 2 * dtau_dk1 * dtau_dk2

                p_r = np.sum(powers[i][j])
                noise_effect = 1 / (p_r * noise_factors[0] + i_bg * noise_factors[1] + T * (noise_factors[2] + noise_factors[3]))

                fim[param1][param2] += noise_effect * (dh_dk1_dh_dk2 * E_2 \
                                       + (h_dh_dk1_dtau_dk2 + h_dh_dk2_dtau_dk1) * E_3 \
                                       + hsq_dtau_dk1_dtau_dk2 * E_1)
    return np.linalg.inv(fim)


#  Bechadergue's method, CRLB calculation for a single position estimation
def bechadergue_crlb_single_instance(crlb_obj, tx1, tx2, delays, curr_t, dt_vhc, max_pow, sig_freq, meas_dt, T, i_bg, noise_factors, powers):
    fim = np.zeros(shape=(4, 4))

    for param1, param2 in zip(range(4), range(4)):
        for i in range(2):
            for j in range(2):
                ij = (i + 1) * 10 + (j + 1)
                h_ij = crlb_obj.get_h_ij(ij, tx1, tx2)
                E_1, E_2, E_3 = signal_generator(curr_t, dt_vhc, max_pow, sig_freq, delays[i][j], meas_dt)
                dh_dk1 = crlb_obj.get_d_hij_d_param(param1 + 1, ij, tx1, tx2)
                dh_dk2 = crlb_obj.get_d_hij_d_param(param2 + 1, ij, tx1, tx2)
                dtau_dk1 = crlb_obj.get_d_tau_d_param(param1 + 1, ij, tx1, tx2)
                dtau_dk2 = crlb_obj.get_d_tau_d_param(param2 + 1, ij, tx1, tx2)

                dh_dk1_dh_dk2 = dh_dk1 * dh_dk2
                h_dh_dk1_dtau_dk2 = - h_ij * dh_dk1 * dtau_dk2
                h_dh_dk2_dtau_dk1 = - h_ij * dh_dk2 * dtau_dk1
                hsq_dtau_dk1_dtau_dk2 = h_ij ** 2 * dtau_dk1 * dtau_dk2

                p_r = np.sum(powers[i][j])
                noise_effect = 1 / (p_r * noise_factors[0] + i_bg * noise_factors[1] + T * (
                            noise_factors[2] + noise_factors[3]))

                fim[param1][param2] += noise_effect * (dh_dk1_dh_dk2 * E_2 \
                                       + (h_dh_dk1_dtau_dk2 + h_dh_dk2_dtau_dk1) * E_3 \
                                       + hsq_dtau_dk1_dtau_dk2 * E_1)
    return np.linalg.inv(fim)


#  Soner's method, CRLB calculation for a single position estimation
def soner_crlb_single_instance(crlb_obj, tx1, tx2, delays, curr_t, dt_vhc, max_pow, sig_freq, meas_dt, T, i_bg, noise_factors, powers):
    fim = np.zeros(shape=(4, 4))

    for param1, param2 in zip(range(4), range(4)):
        for i in range(2):
            for j in range(2):
                for qrx in range(4):
                    ij = (i + 1) * 10 + (j + 1)
                    q = qrx + 1
                    E_1, E_2, E_3 = signal_generator(curr_t, dt_vhc, max_pow, sig_freq, delays[i][j], meas_dt)

                    h_ijq = crlb_obj.get_h_ijq(ij, q, tx1, tx2)
                    dh_dk1 = crlb_obj.get_d_hij_q_d_param(param1 + 1, ij, q, tx1, tx2)
                    dh_dk2 = crlb_obj.get_d_hij_q_d_param(param2 + 1, ij, q, tx1, tx2)
                    dtau_dk1 = crlb_obj.get_d_tau_d_param(param1 + 1, ij, tx1, tx2)
                    dtau_dk2 = crlb_obj.get_d_tau_d_param(param2 + 1, ij, tx1, tx2)

                    dh_dk1_dh_dk2 = dh_dk1 * dh_dk2
                    h_dh_dk1_dtau_dk2 = h_ijq * dh_dk1 * dtau_dk2
                    h_dh_dk2_dtau_dk1 = h_ijq * dh_dk2 * dtau_dk1
                    hsq_dtau_dk1_dtau_dk2 = h_ijq ** 2 * dtau_dk1 * dtau_dk2

                    p_r = powers[i][j][qrx]
                    noise_effect = 1 / (p_r * noise_factors[0] + i_bg * noise_factors[1] + T * (
                                noise_factors[2] + noise_factors[3]/ 16))  # /16 comes from capacitance division

                    fim[param1][param2] += noise_effect * (dh_dk1_dh_dk2 * E_2 \
                                           + (h_dh_dk1_dtau_dk2 + h_dh_dk2_dtau_dk1) * E_3 \
                                           + hsq_dtau_dk1_dtau_dk2 * E_1)
    return np.linalg.inv(fim)


def signal_generator(current_time, dt_vhc, max_power, signal_freq, delay, measure_dt):
    time = np.arange(current_time - dt_vhc + measure_dt, current_time + measure_dt, measure_dt)

    s = max_power * np.sin((2 * np.pi * signal_freq * (time - delay)) % (2 * np.pi))
    d_s_d_tau = - max_power * 2 * np.pi * signal_freq * np.cos((2 * np.pi * signal_freq * (time - delay)) % (2 * np.pi))

    e_1 = np.sum(np.dot(d_s_d_tau, d_s_d_tau))
    e_2 = np.sum(np.dot(s, s))
    e_3 = np.sum(np.dot(s, d_s_d_tau))

    return e_1, e_2, e_3


def main():

    dir = '../GUI_data/100_point_'
    files = glob(dir + '*/3/')
    x_pose, y_pose = [], []
    x_becha, y_becha = [], []
    x_roberts, y_roberts = [], []
    print(len(files))
    for folder_name in files:
        x_pose.append(np.loadtxt(folder_name+'x_pose.txt', delimiter=','))
        y_pose.append(np.loadtxt(folder_name+'y_pose.txt', delimiter=','))
        x_roberts.append(np.loadtxt(folder_name+'x_roberts.txt', delimiter=','))
        y_roberts.append(np.loadtxt(folder_name+'y_roberts.txt', delimiter=','))
        x_becha.append(np.loadtxt(folder_name+'x_becha.txt', delimiter=','))
        y_becha.append(np.loadtxt(folder_name+'y_becha.txt', delimiter=','))
    # print(np.shape(np.asarray(y_pose)))
    data = load_mat('../SimulationData/v2lcRun_sm3_comparisonSoA.mat')
    dp = 10
    # vehicle parameters
    L_1 = data['vehicle']['target']['width']
    L_2 = data['vehicle']['ego']['width']

    rx_area = data['qrx']['f_QRX']['params']['area']

    # time parameters
    time = data['vehicle']['t']['values'][::dp]
    dt = data['vehicle']['t']['dt'] * dp
    start_time = data['vehicle']['t']['start']
    stop_time = data['vehicle']['t']['stop']

    max_power = data['tx']['power']
    signal_freq = 1e6  # 1 MHz signal frequency
    measure_dt = 1 / 2.5e6  # 2.5 MHz measure frequency

    # relative tgt vehicle positions
    tx1_x = data['vehicle']['target_relative']['tx1_qrx4']['y'][::dp]
    tx1_y = data['vehicle']['target_relative']['tx1_qrx4']['x'][::dp]
    tx2_x = data['vehicle']['target_relative']['tx2_qrx3']['y'][::dp]
    tx2_y = data['vehicle']['target_relative']['tx2_qrx3']['x'][::dp]
    rel_heading = data['vehicle']['target_relative']['heading'][::dp]

    # delay parameters
    delay_11 = data['channel']['qrx1']['delay']['tx1'][::dp]
    delay_12 = data['channel']['qrx1']['delay']['tx2'][::dp]
    delay_21 = data['channel']['qrx2']['delay']['tx1'][::dp]
    delay_22 = data['channel']['qrx2']['delay']['tx2'][::dp]

    # received power of QRXes
    pow_qrx1_tx1 = np.array([data['channel']['qrx1']['power']['tx1']['A'][::dp], data['channel']['qrx1']['power']['tx1']['B'][::dp],
                             data['channel']['qrx1']['power']['tx1']['C'][::dp], data['channel']['qrx1']['power']['tx1']['D'][::dp]])
    pow_qrx1_tx2 = np.array([data['channel']['qrx1']['power']['tx2']['A'][::dp], data['channel']['qrx1']['power']['tx2']['B'][::dp],
                             data['channel']['qrx1']['power']['tx2']['C'][::dp], data['channel']['qrx1']['power']['tx2']['D'][::dp]])
    pow_qrx2_tx1 = np.array([data['channel']['qrx2']['power']['tx1']['A'][::dp], data['channel']['qrx2']['power']['tx1']['B'][::dp],
                             data['channel']['qrx2']['power']['tx1']['C'][::dp], data['channel']['qrx2']['power']['tx1']['D'][::dp]])
    pow_qrx2_tx2 = np.array([data['channel']['qrx2']['power']['tx1']['A'][::dp], data['channel']['qrx2']['power']['tx1']['B'][::dp],
                             data['channel']['qrx2']['power']['tx1']['C'][::dp], data['channel']['qrx2']['power']['tx1']['D'][::dp]])

    # noise params
    T = 298  # Kelvin
    I_bg = 750e-6  # 750 uA
    p_r_factor = data['qrx']['tia']['shot_P_r_factor']
    i_bg_factor = data['qrx']['tia']['shot_I_bg_factor']
    t_factor1 = data['qrx']['tia']['thermal_factor1']
    t_factor2 = data['qrx']['tia']['thermal_factor1']
    noise_factors = [p_r_factor, i_bg_factor, t_factor1, t_factor2]

    # other params
    rx_fov = 50  # angle
    tx_half_angle = 60  # angle

    # initalize crlb equations with given parameters
    crlb_init_object = CRLB_init(L_1, L_2, rx_area, rx_fov, tx_half_angle)

    # calculate bounds for all elements
    robert_crlb_results = [np.array([]), np.array([])]
    becha_crlb_results = [np.array([]), np.array([]), np.array([]), np.array([])]
    soner_crlb_results = [np.array([]), np.array([]), np.array([]), np.array([])]

    for i in range(len(tx1_x)):
        tx1 = np.array([tx1_x[i], tx1_y[i]])
        tx2 = np.array([tx2_x[i], tx2_y[i]])
        curr_t = time[i]
        delays = np.array([[delay_11[i], delay_12[i]], [delay_21[i], delay_22[i]]])
        powers = np.array([[pow_qrx1_tx1[:, i], pow_qrx1_tx2[:, i]], [pow_qrx2_tx1[:, i], pow_qrx2_tx2[:, i]]])
        fim_inverse_rob = roberts_crlb_single_instance(crlb_init_object, tx1, tx2, delays,
                                     curr_t, dt, max_power, signal_freq, measure_dt, T, I_bg, noise_factors, powers)
        fim_inverse_becha = bechadergue_crlb_single_instance(crlb_init_object, tx1, tx2, delays,
                                     curr_t, dt, max_power, signal_freq, measure_dt, T, I_bg, noise_factors, powers)
        fim_inverse_soner = soner_crlb_single_instance(crlb_init_object, tx1, tx2, delays,
                                     curr_t, dt, max_power, signal_freq, measure_dt, T, I_bg, noise_factors, powers)

        robert_crlb_results[0] = np.append(robert_crlb_results[0], np.sqrt(fim_inverse_rob[0][0]))
        robert_crlb_results[1] = np.append(robert_crlb_results[1], np.sqrt(fim_inverse_rob[1][1]))

        becha_crlb_results[0] = np.append(becha_crlb_results[0], np.sqrt(fim_inverse_becha[0][0]))
        becha_crlb_results[1] = np.append(becha_crlb_results[1], np.sqrt(fim_inverse_becha[1][1]))
        becha_crlb_results[2] = np.append(becha_crlb_results[2], np.sqrt(fim_inverse_becha[2][2]))
        becha_crlb_results[3] = np.append(becha_crlb_results[3], np.sqrt(fim_inverse_becha[3][3]))

        soner_crlb_results[0] = np.append(soner_crlb_results[0], np.sqrt(fim_inverse_soner[0][0]))
        soner_crlb_results[1] = np.append(soner_crlb_results[1], np.sqrt(fim_inverse_soner[1][1]))
        soner_crlb_results[2] = np.append(soner_crlb_results[2], np.sqrt(fim_inverse_soner[2][2]))
        soner_crlb_results[3] = np.append(soner_crlb_results[3], np.sqrt(fim_inverse_soner[3][3]))
        print(i)

    print("finished")
    folder_name = '../GUI_data/means/3/'
    # x_becha, y_becha = np.loadtxt(folder_name+'x_becha_mean.txt', delimiter=','), np.loadtxt(folder_name+'y_becha_mean.txt',
    #                                                                                     delimiter=',')
    # x_roberts, y_roberts = np.loadtxt(folder_name+'x_roberts_mean.txt', delimiter=','), np.loadtxt(folder_name+'y_roberts_mean.txt',
    #                                                                                           delimiter=',')
    # x_soner, y_soner = np.loadtxt(folder_name+'x_pose_mean.txt', delimiter=','), np.loadtxt(folder_name+'y_pose_mean.txt', delimiter=',')

    plt.close("all")
    plot1 = plt.figure(1)
    becha_x1, = plt.plot(time[0:i+1], becha_crlb_results[0])
    soner_x1, = plt.plot(time[0:i+1], soner_crlb_results[0])
    ten_cm_line, = plt.plot(time[0:i + 1], 0.1*np.ones(i+1),'--')
    roberts_x1, = plt.plot(time[0:i + 1], robert_crlb_results[0])
    plt.ylabel('Standard Deviation (m)')
    plt.xlabel('Time (s)')
    plt.title('CRLB for x1')
    plt.legend([becha_x1, soner_x1, roberts_x1, ten_cm_line], ['RToF', 'AoA', 'TDoA', '10 cm line'])
    plt.ylim(1e-5,10)
    plt.yscale('log')
    plt.savefig('crlb_x1.png')

    plot2 = plt.figure(2)
    becha_y1, = plt.plot(time[0:i+1], becha_crlb_results[1])
    soner_y1, = plt.plot(time[0:i+1], soner_crlb_results[1])
    ten_cm_line, = plt.plot(time[0:i + 1], 0.1*np.ones(i+1),'--')
    roberts_y1, = plt.plot(time[0:i + 1], robert_crlb_results[1])
    plt.ylabel('Standard Deviation (m)')
    plt.xlabel('Time (s)')
    plt.title('CRLB for y1')
    plt.legend([becha_y1, soner_y1, roberts_y1, ten_cm_line], ['RToF', 'AoA', 'TDoA', '10 cm line'])
    plt.ylim(1e-5,10)
    plt.yscale('log')
    plt.savefig('crlb_y1.png')

    plot3 = plt.figure(3)
    becha_x2, = plt.plot(time[0:i + 1], becha_crlb_results[2])
    soner_x2, = plt.plot(time[0:i + 1], soner_crlb_results[2])
    ten_cm_line, = plt.plot(time[0:i + 1], 0.1*np.ones(i+1),'--')
    plt.ylabel('Standard Deviation (m)')
    plt.xlabel('Time (s)')
    plt.title('CRLB for x2')
    plt.legend([becha_x2, soner_x2, ten_cm_line], ['RToF', 'AoA', '10 cm line'])
    plt.ylim(1e-5,10)
    plt.yscale('log')
    plt.savefig('crlb_x2.png')

    plot4 = plt.figure(4)
    becha_y2, = plt.plot(time[0:i + 1], becha_crlb_results[3])
    soner_y2, = plt.plot(time[0:i + 1], soner_crlb_results[3])
    ten_cm_line, = plt.plot(time[0:i + 1], 0.1*np.ones(i+1),'--')
    plt.ylabel('Standard Deviation (m)')
    plt.xlabel('Time (s)')
    plt.title('CRLB for y2')
    plt.legend([becha_y2, soner_y2, ten_cm_line], ['RToF', 'AoA', '10 cm line'])
    plt.ylim(1e-5,10)
    plt.yscale('log')
    plt.savefig('crlb_y2.png')

    x1_becha, x2_becha = np.asarray(x_becha)[:,:,0], np.asarray(x_becha)[:,:,1]
    y1_becha, y2_becha = np.asarray(y_becha)[:,:,0], np.asarray(y_becha)[:,:,1]
    print(np.shape(x1_becha))
    print(np.shape(x2_becha))
    print(np.shape(y1_becha))
    print(np.shape(y2_becha))

    plot5 = plt.figure(5)
    th_becha_x1, = plt.plot(time[0:i+1], becha_crlb_results[0], '--')
    th_becha_x2, = plt.plot(time[0:i + 1], becha_crlb_results[2], '--')
    th_becha_y1, = plt.plot(time[0:i+1], becha_crlb_results[1], '--')
    th_becha_y2, = plt.plot(time[0:i + 1], becha_crlb_results[3], '--')
    # sim_becha_x1, = plt.plot(time[0:i + 1], abs(tx1_x + x1_becha)[0:i + 1])
    sim_becha_x1, = plt.plot(time[0:i + 1], np.std(x1_becha, axis=0))
    # sim_becha_x2, = plt.plot(time[0:i + 1], abs(tx2_x + x2_becha)[0:i + 1])
    sim_becha_x2, = plt.plot(time[0:i + 1], np.std(x2_becha, axis=0))
    # sim_becha_y1, = plt.plot(time[0:i + 1], abs(tx1_y - y1_becha)[0:i + 1])
    sim_becha_y1, = plt.plot(time[0:i + 1], np.std(y1_becha, axis=0))
    # sim_becha_y2, = plt.plot(time[0:i + 1], abs(tx2_y - y2_becha)[0:i + 1])
    sim_becha_y2, = plt.plot(time[0:i + 1], np.std(y2_becha, axis=0))
    plt.ylabel('Error (m)')
    plt.xlabel('Time (s)')
    plt.title('CRLB vs. Simulation Results for RToF')
    # plt.legend([th_becha_x1, th_becha_x2, th_becha_y1, th_becha_y2, sim_becha_x1 , sim_becha_x2, sim_becha_y1,
    #             sim_becha_y2], ['x1 (theoretical)', 'x2 (theoretical)', 'y1 (theoretical)', 'y2 (theoretical)',
    #                             'x1 (simulation)', 'x2 (simulation)', 'y1 (simulation)', 'y2 (simulation)'],
    #            ncol=4,loc=3)
    # plt.ylim(1e-5,2)
    # plt.yscale('log')
    plt.savefig('crlb_becha_lin.png')
    plt.yscale('log')
    plt.savefig('crlb_becha_log.png')

    x1_roberts, x2_roberts = np.asarray(x_roberts)[:,:,0], np.asarray(x_roberts)[:,:,1]
    y1_roberts, y2_roberts = np.asarray(y_roberts)[:,:,0], np.asarray(y_roberts)[:,:,1]

    plot6 = plt.figure(6)
    th_roberts_x1, = plt.plot(time[0:i+1], robert_crlb_results[0], '--')
    th_roberts_y1, = plt.plot(time[0:i+1], robert_crlb_results[1], '--')
    xr_mask = np.isfinite(np.std(x1_roberts, axis=0))
    yr_mask = np.isfinite(np.std(y1_roberts, axis=0))
    # sim_roberts_x1, = plt.plot(time[0:i + 1][xr_mask], abs(tx1_x + x1_roberts)[0:i + 1][xr_mask])
    sim_roberts_x1, = plt.plot(time[0:i + 1][xr_mask], np.std(x1_roberts, axis=0)[xr_mask])
    # sim_roberts_y1, = plt.plot(time[0:i + 1][yr_mask], abs(tx1_y - y1_roberts)[0:i + 1][yr_mask])
    sim_roberts_y1, = plt.plot(time[0:i + 1][yr_mask], np.std(y1_roberts, axis=0)[yr_mask])
    plt.ylabel('Error (m)')
    plt.xlabel('Time (s)')
    plt.title('CRLB vs. Simulation Results for TDoA')
    plt.legend([th_roberts_x1, th_roberts_y1, sim_roberts_x1 , sim_roberts_y1],
               ['x1 (theoretical)', 'y1 (theoretical)', 'x1 (simulation)', 'y1 (simulation)'],ncol=2,loc=3)
    plt.ylim(1e-5,2)
    plt.yscale('log')
    plt.savefig('crlb_roberts.png')

    x1_soner, x2_soner = np.asarray(x_pose)[:,:,0], np.asarray(x_pose)[:,:,1]
    y1_soner, y2_soner = np.asarray(y_pose)[:,:,0], np.asarray(y_pose)[:,:,1]

    plot7 = plt.figure(7)
    th_soner_x1, = plt.plot(time[0:i+1], soner_crlb_results[0], '--')
    th_soner_x2, = plt.plot(time[0:i + 1], soner_crlb_results[2], '--')
    th_soner_y1, = plt.plot(time[0:i+1], soner_crlb_results[1], '--')
    th_soner_y2, = plt.plot(time[0:i + 1], soner_crlb_results[3], '--')
    # sim_soner_x1, = plt.plot(time[0:i + 1], abs(tx1_x + x1_soner)[0:i + 1])
    sim_soner_x1, = plt.plot(time[0:i + 1], np.std(x1_soner, axis=0))
    # sim_soner_x2, = plt.plot(time[0:i + 1], abs(tx2_x + x2_soner)[0:i + 1])
    sim_soner_x2, = plt.plot(time[0:i + 1], np.std(x2_soner, axis=0))
    # sim_soner_y1, = plt.plot(time[0:i + 1], abs(tx1_y - y1_soner)[0:i + 1])
    sim_soner_y1, = plt.plot(time[0:i + 1], np.std(y1_soner, axis=0))
    # sim_soner_y2, = plt.plot(time[0:i + 1], abs(tx2_y - y2_soner)[0:i + 1])
    sim_soner_y2, = plt.plot(time[0:i + 1], np.std(y2_soner, axis=0))
    plt.ylabel('Error (m)')
    plt.xlabel('Time (s)')
    plt.title('CRLB vs. Simulation Results for AoA')
    plt.legend([th_soner_x1, th_soner_x2, th_soner_y1, th_soner_y2, sim_soner_x1 , sim_soner_x2, sim_soner_y1,
                sim_soner_y2], ['x1 (theoretical)', 'x2 (theoretical)', 'y1 (theoretical)', 'y2 (theoretical)',
                                'x1 (simulation)', 'x2 (simulation)', 'y1 (simulation)', 'y2 (simulation)'],
               ncol=4,loc=3)
    plt.ylim(1e-5,2)
    plt.yscale('log')
    plt.savefig('crlb_soner.png')
    plt.show()




if __name__ == "__main__":
    main()