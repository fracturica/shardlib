from scipy.special import ellipe, ellipkm1
import numpy as np
import matplotlib.pyplot as plt


def calcK(axisA, axisB):
    assert axisA >= axisB
    assert axisB > 0
    a, b = float(axisA) / 2, float(axisB) / 2
    return np.sqrt(1 - (b / a)**2)


def calcR(k, v):
    assert v > 0 and v <= 0.5
    assert k >= 0 and k < 1
    if k > 0:
        E = ellipe(k)
        K = ellipkm1(1 - k)
        k1sq = 1.0 - k**2
        return k**2 / ((k**2 - v) * E + v * k1sq * K)
    else:
        return 2.0 / (np.pi * (1 - v))


def calcQ(k, v):
    assert v > 0 and v <= 0.5
    assert k >= 0 and k < 1
    if k > 0:
        E = ellipe(k)
        K = ellipkm1(1 - k)
        k1sq = 1.0 - k**2
        return k**2 / (E * k**2 + v * k1sq * (E - K))
    else:
        return 2.0 / np.pi


def calcStresses(tensileStress, gamma):
    """
    """
    gamma = gamma % 360
    assert gamma >= 0 and gamma <= 90
    gamma = np.radians(gamma)
    sigma = tensileStress * np.cos(gamma)**2
    tao = tensileStress * (np.cos(gamma) * np.sin(gamma))
    return sigma, tao


def calcK1(axisA, axisB, beta, sigma):
    """
    """
    a, b = float(axisA) / 2, float(axisB) / 2,
    beta = np.radians(beta)
    k = calcK(a, b)
    E = ellipe(k)
    term1 = sigma * np.sqrt(np.pi * (b / a)) / E
    term2 = ((a**4 * np.sin(beta)**2 + b**4 * np.cos(beta)**2) /
             (a**2 * np.sin(beta)**2 + b**2 * np.cos(beta)**2))**0.25
    K1 = term1 * term2
    return K1


def calcK2(axisA, axisB, v, beta, omega, tao):
    """
    """
    a, b = float(axisA) / 2, float(axisB) / 2
    beta, omega = (np.radians(beta), np.radians(omega))
    k = calcK(a, b)
    Q, R = calcQ(k, v), calcR(k, v)
    term1 = tao * np.sqrt(np.pi * b / a)
    term2 = (b**2 * R * np.cos(beta) * np.cos(omega) +
             a**2 * Q * np.sin(beta) * np.sin(omega))
    term3 = ((a**2 * np.sin(beta)**2 + b**2 * np.cos(beta)**2)**0.25 *
             (a**4 * np.sin(beta)**2 + b**4 * np.cos(beta)**2)**0.25)
    return - term1 * term2 / term3


def calcK3(axisA, axisB, v, beta, omega, tao):
    """
    """
    a, b = float(axisA) / 2, float(axisB) / 2
    beta, omega = np.radians(beta), np.radians(omega)
    k = calcK(a, b)
    E, K = ellipe(k), ellipkm1(1 - k)
    Q, R = calcQ(k, v), calcR(k, v)
    term1 = tao * (1 - v) * np.sqrt(np.pi * b / a)
    term2 = (a**2 * R * np.sin(beta) * np.cos(omega) -
             b**2 * Q * np.cos(beta) * np.sin(omega))
    term3 = ((a**2 * np.sin(beta)**2 + b**2 * np.cos(beta)**2)**0.25 *
             (a**4 * np.sin(beta)**2 + b**4 * np.cos(beta)**2)**0.25)
    return term1 * term2 / term3


def calcAnSolWrapper(sifKey, majorAxis, minorAxis, v, betas,
                     gamma, omega, tensileStress):
    sigma, tao = calcStresses(tensileStress=tensileStress, gamma=gamma)
    if sifKey == 'K1':
        return [
            calcK1(
                axisA=majorAxis,
                axisB=minorAxis,
                beta=beta,
                sigma=sigma) for beta in betas]
    elif sifKey == 'K2':
        return [calcK2(axisA=majorAxis, axisB=minorAxis, v=v, beta=beta,
                       omega=omega, tao=tao) for beta in betas]
    elif sifKey == 'K3':
        return [calcK3(axisA=majorAxis, axisB=minorAxis, v=v, beta=beta,
                       omega=omega, tao=tao) for beta in betas]
    else:
        raise KeyError(
            'Unrecognized analytical solution key {0}'.format(sifKey))
