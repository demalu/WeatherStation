import numpy as np
import pandas as pd


def kalmanFilter(val, old_v, range):
    
    delta_t = 5*60 # seconds
    transition_matrix = np.array([[1, delta_t, 0.5*delta_t**2], [0, 1, delta_t], [0, 0, 1]])
    observation_matrix = [1, 0, 0]

    state_matrix = np.zeros(3)
    
    if np.isnan(old_v[0]) == True:
        # se è il primo giro tutti e tre i valori saranno NaN quindi riempo il primo campo con il valore passato
        state_matrix[0] = val
        

    elif np.isnan(old_v[1]) == True:
        state_matrix[0] = old_v[0]

    elif np.isnan(old_v[2]) == True:
        state_matrix[0] = old_v[0]
        state_matrix[1] = (old_v[0] - old_v[1])/delta_t
    
    else:
        state_matrix[0] = old_v[0]
        state_matrix[1] = (old_v[0] - old_v[1])/delta_t
        state_matrix[2] = (state_matrix[1] - (old_v[1]-old_v[2])) / delta_t

    #--------PREDICTION-------

    prova = state_matrix[np.newaxis]
    prova = prova.T
    z_hat = np.dot(transition_matrix, prova)
    y_hat = np.dot(observation_matrix, z_hat)

    if np.isnan(old_v[0]) == False:
        #se il valore acquisito è in un determinato range --> va bene 
        if old_v[0] - range < val < old_v[0] + range:
            #shifto i valori di 1
            old_v = np.roll(old_v, 1)
            #sostituisco il primo (che shiftano corrisponde al più vecchio) con valore ricavato dal sensore
            old_v[0] = val

            return (val, old_v)
            
        else:
            #shifto i valori di 1
            old_v = np.roll(old_v, 1)
            #sostituisco il primo (che shiftano corrisponde al più vecchio) con la prediction
            old_v[0] = y_hat
            
            return (y_hat, old_v)
    else:
        old_v[0] = val
        return (val, old_v)