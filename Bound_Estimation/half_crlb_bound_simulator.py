from half_crlb_init import *
from matfile_read import load_mat
from glob import glob
import math
import matplotlib.pyplot as plt

# Roberts' method, CRLB calculation for a single position estimation
def roberts_half_crlb_single_instance(crlb_inst, tx1, tx2, noise_factor):
    flag = False
    fim = np.zeros(shape=(2,2))

    for param1, param2 in zip(range(2), range(2)):
        for i in range(2):
            fim[param1][param2] -= 1 / noise_factor[i] * crlb_inst.d_ddist_d_param(param1 + 1, i, tx1, tx2) \
                                  * crlb_inst.d_ddist_d_param(param2 + 1, i, tx1, tx2)

    return np.linalg.inv(fim)


#  Bechadergue's method, CRLB calculation for a single position estimation
def bechadergue_half_crlb_single_instance(crlb_inst, tx1, tx2, noise_factor):
    fim = np.zeros(shape=(4, 4))

    for param1, param2 in zip(range(4), range(4)):
        for i in range(2):
            for j in range(2):
                ij = (i + 1) * 10 + j

                fim[param1][param2] -= 1 / noise_factor[i][j] * crlb_inst.d_dij_d_param(param1 + 1, ij, tx1, tx2) \
                                       * crlb_inst.d_dij_d_param(param2 + 1, ij, tx1, tx2)
    return np.linalg.inv(fim)


#  Soner's method, CRLB calculation for a single position estimation
def soner_half_crlb_single_instance(crlb_inst, tx1, tx2, noise_factor):
    fim = np.zeros(shape=(4, 4))

    for param1, param2 in zip(range(4), range(4)):
        for i in range(2):
            for j in range(2):
                ij = (i + 1) * 10 + j

                fim[param1][param2] -= 1 / noise_factor[i][j] * crlb_inst.d_theta_d_param(param1 + 1, ij, tx1, tx2) \
                                       * crlb_inst.d_theta_d_param(param2 + 1, ij, tx1, tx2)
    return np.linalg.inv(fim)


def deviation_from_actual_value(array, actual_val):
    return np.sqrt(np.mean(abs(array - actual_val) ** 2, axis=0))

def main():

    data = load_mat('../SimulationData/v2lcRun_sm3_comparisonSoA.mat')
    dp = 10
    # vehicle parameters
    L_1 = data['vehicle']['target']['width']
    L_2 = data['vehicle']['ego']['width']

    rx_area = data['qrx']['f_QRX']['params']['area']

    # time parameters
    time = data['vehicle']['t']['values'][::dp]
    dt = data['vehicle']['t']['dt'] * dp

    max_power = data['tx']['power']
    signal_freq = 1e6  # 1 MHz signal frequency
    measure_dt = 1 / 2.5e6  # 2.5 MHz measure frequency

    # relative tgt vehicle positions
    tx1_x = data['vehicle']['target_relative']['tx1_qrx4']['y'][::dp]
    tx1_y = data['vehicle']['target_relative']['tx1_qrx4']['x'][::dp]
    tx2_x = data['vehicle']['target_relative']['tx2_qrx3']['y'][::dp]
    tx2_y = data['vehicle']['target_relative']['tx2_qrx3']['x'][::dp]
    rel_heading = data['vehicle']['target_relative']['heading'][::dp]

    #print("deviation results: ", deviation_from_actual_value(np.asarray(x_becha)[:,:,0], -tx1_x))
    #print(deviation_from_actual_value(np.asarray(x_becha)[:,:,0], -tx1_x).shape)



    # noise params


    # other params
    rx_fov = 50  # angle
    tx_half_angle = 60  # angle

    # initalize crlb equations with given parameters
    half_crlb_init_object = half_crlb_init(L_1, L_2, rx_area, rx_fov, tx_half_angle)

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
        fim_inverse_rob = roberts_half_crlb_single_instance(half_crlb_init_object, tx1, tx2,noise)
        fim_inverse_becha = bechadergue_half_crlb_single_instance(half_crlb_init_object, tx1, tx2, noise)
        fim_inverse_soner = soner_half_crlb_single_instance(half_crlb_init_object, tx1, tx2, noise)

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

    np.savetxt('pose_crlb_x1.txt', soner_crlb_results[0], delimiter=',')
    np.savetxt('becha_crlb_x1.txt', becha_crlb_results[0], delimiter=',')
    np.savetxt('pose_crlb_x2.txt', soner_crlb_results[2], delimiter=',')
    np.savetxt('becha_crlb_x2.txt', becha_crlb_results[2], delimiter=',')
    np.savetxt('roberts_crlb_x.txt', robert_crlb_results[0], delimiter=',')

    np.savetxt('pose_crlb_y1.txt', soner_crlb_results[1], delimiter=',')
    np.savetxt('becha_crlb_y1.txt', becha_crlb_results[1], delimiter=',')
    np.savetxt('pose_crlb_y2.txt', soner_crlb_results[3], delimiter=',')
    np.savetxt('becha_crlb_y2.txt', becha_crlb_results[3], delimiter=',')
    np.savetxt('roberts_crlb_y.txt', robert_crlb_results[1], delimiter=',')

    print("finished")
    folder_name = '../GUI_data/means/3/'
    # x_becha, y_becha = np.loadtxt(folder_name+'x_becha_mean.txt', delimiter=','), np.loadtxt(folder_name+'y_becha_mean.txt',
    #                                                                                     delimiter=',')
    # x_roberts, y_roberts = np.loadtxt(folder_name+'x_roberts_mean.txt', delimiter=','), np.loadtxt(folder_name+'y_roberts_mean.txt',
    #                                                                                           delimiter=',')
    # x_soner, y_soner = np.loadtxt(folder_name+'x_pose_mean.txt', delimiter=','), np.loadtxt(folder_name+'y_pose_mean.txt', delimiter=',')




if __name__ == "__main__":
    main()