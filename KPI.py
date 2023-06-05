import numpy as np
def Breakpoints(C_P):
    if C_P <= 54:
        BP_LO = 0
        BP_HI = 54
        I_LO = 0
        I_HI = 50
        category = "Good"
    elif 55 <= C_P <= 154:
        BP_LO = 55
        BP_HI = 154
        I_LO = 51
        I_HI = 100
        category = "Moderate"
    elif 155 <= C_P <= 254:
        BP_LO = 155
        BP_HI = 254
        I_LO = 101
        I_HI = 150
        category = "Unhealty for sensitive groups"
    elif 255 <= C_P <= 354:
        BP_LO = 255
        BP_HI = 354
        I_LO = 151
        I_HI = 200
        category = "Unhealty"
    elif 355 <= C_P <= 424:
        BP_LO = 355
        BP_HI = 424
        I_LO = 201
        I_HI = 300
        category = "Very unhealty"
    elif 425 <= C_P <= 504:
        BP_LO = 425
        BP_HI = 504
        I_LO = 301
        I_HI = 400
        category = "Hazardous"
    elif 505 <= C_P <= 604:
        BP_LO = 505
        BP_HI = 604
        I_LO = 401
        I_HI = 500
        category = "Hazardous"
    else:
        raise ValueError
    return BP_LO, BP_HI, I_LO, I_HI, category

def AIQ(C_P):
    #C_P is the rounded concentration of pollutant p
    #BP_HI is the breakpoint greater than or equal to C_P
    #BP_LO is the breakpoint less than or equal to C_P
    #I_HI = the AQI value corresponding to BP_HI
    #I_LO = the AQI value corresponding to BP_LO
    BP_LO, BP_HI, I_LO, I_HI, category = Breakpoints(C_P)
    AIQ = int((I_HI - I_LO)/(BP_HI - BP_LO) * (C_P - BP_LO) + I_LO)
    return AIQ, category

def HUMIDEX(T, RH):
    #T is the air temperature
    #RH is the relative humidity
    H = T + (0.5555 * (0.06 * RH/100 * 10**(0.03*T) - 10))
    if H < 27:
        category = "Comfort"
    elif 27 <= H < 30:
        category = "Cautela"
    elif 30 <= H < 40:
        category = "Estrema cautela"
    elif 40 <= H < 55:
        category = "Pericolo"
    else:
        category = "Estremo pericolo"
    return H, category

def MOCI(WS, RH, T_globe, T_a, I_cl = 3):
    #WS is the wind speed
    #Rh is the relative humidity
    #T_globe is the globe temperature (MRP)
    #T_a is the air temperature
    #I_cl is the thermal clothing insulation, we picked 3 as default values
    #Compute the T_mr (mean radiant temperature)
    epsilon = 0 #DA SETTARE
    D = 0 # DA SETTARE (DIAMETRO?)
    T_mr = ((T_globe + 273.15)**4 + ((1.1*10**8*WS**0.6)/(epsilon * D**0.4)) * (T_globe-T_a))**0.25 - 275.15
    moci = -4.068 - 0.272*WS + 0.05*RH + 0.083*T_mr + 0.058*T_a + 0.264*I_cl
    return moci

def AH(RH, T):
    ah = (RH/100) * 6.112 * np.exp(17.67*T/(T + 243.5)) * 1000/(461.5*(T + 273.15))
    return ah


if __name__ == "__main__":
    #Cp= 23
    #index, categ= AIQ(Cp)
    #print(index, categ)

    T = 55
    H = 0.7
    humidex, categ = HUMIDEX(T, H)
    print(humidex, categ)