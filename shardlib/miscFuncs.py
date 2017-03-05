import numpy as np


def dotProd(a, b):
    a = np.array(a)
    b = np.array(b)
    assert a.shape == b.shape
    assert len(a.shape) == 1
    return sum(np.prod([a, b], axis=0))


def calcAbsoluteArea(x, y):
    x = np.array(x)
    y = np.array(y)
    assert x.shape == y.shape
    assert len(x.shape) == 1
    assert min(x) >= 0
    area = 0
    for i in range(len(x) - 1):
        a = x[i + 1] - x[i]
        assert a >= 0
        area += 0.5 * (abs(y[i]) + abs(y[i + 1])) * a
    return area


def calcDotProdDiff(analysisData, analyticalData):
    assert len(analysisData) == len(analyticalData)
    analysisProd = dotProd(analysisData, analysisData)
    analyticalProd = dotProd(analyticalData, analyticalData)
    return float(analysisProd - analyticalProd) / float(analyticalProd)


def calcAreaDiff(angles, analysisData, analyticalData):
    assert len(analysisData) == len(analyticalData)
    assert len(angles) == len(analyticalData)
    analysisArea = calcAbsoluteArea(angles, analysisData)
    analyticalArea = calcAbsoluteArea(angles, analyticalData)
    return float(analysisArea - analyticalArea) / float(analyticalArea)


def contourAveraging(contoursDict, numCont):
    assert len(contoursDict.keys()) >= numCont
    assert numCont >= 1
    start = int((len(contoursDict.keys()) - numCont) / 2)
    end = start + numCont
    keys = sorted(contoursDict.keys())[start:end]
    return np.sum([contoursDict[k] for k in keys], axis=0) / float(len(keys))


def calcErrors(analytical, analysis):
    a = np.array(analytical)
    f = np.array(analysis)
    assert a.shape == f.shape
    assert len(a.shape) == 1
    return np.abs(f) - np.abs(a)  # f-a


def calcDiffErrors(analytical, analysis):
    errs = calcErrors(analytical, analysis)
    analytical = np.array(analytical)
    return errs  # /max(abs(analytical))


def calcRMSD(analytical, analysis):
    """Return the Root Mean Square Deviation"""
    a = np.array(analytical)
    a_hat = np.array(analysis)
    assert a.shape == a_hat.shape
    assert len(a.shape) == 1
    rmsd = np.sqrt(sum((a - a_hat)**2) / float(len(a)))
    return rmsd


def calcNormErrors(analytical, analysis, domain, eSignFactor):
    """
    (array, array, array, str) -> array, array
    """
    assert len(analytical) == len(analysis)
    assert len(domain) == len(analysis)
    a = np.array(analytical)
    f = np.array(analysis)
    e = [float(fi - ai) / max(abs(a)) for ai, fi in zip(a, f)]
    if eSignFactor == 'dotProd':
        s = (-1 if dotProd(a, a) > dotProd(f, f) else 1)
    elif eSignFactor == 'areas':
        areaDiff = calcAreaDiff(domain, analysis, analytical)
        s = (-1 if areaDiff < 0 else 1)
    else:
        raise KeyError(eSignFactor)
    return np.array(e), s


def calcAvgNormError(analytical, analysis, domain, eSignFactor):
    """
    (array, array, array, string) -> float
    Returns the averaged normalized difference between the
    corresponding members of analytical and analysis arrays.
    The domain is used to determine the integrals (areas) of analytical
    and analysis. eSignFactor determines how the sign of the returned
    value is determined by 'areas' or 'dotProd' subtraction.
    >>> calcAvgNormError([1,2,3,4,5],[-1,2,3,6,7])
    >>> 0.24
    """
    errors, sign = calcNormErrors(
        analytical, analysis, domain, eSignFactor)
    return sign * sum(abs(errors)) / float(len(domain))


def calcMaxNormError(analytical, analysis, domain, eSignFactor):
    """
    (array, array, array, string) -> float

    """
    errors, sign = calcNormErrors(
        analytical, analysis, domain, eSignFactor)
    maxE = 0
    for e in errors:
        if abs(e) > abs(maxE):
            maxE = e
    return maxE


def calcStatsWrapper(statKey, angles, analytical, analysis, eSign):
    if statKey == 'areaDiff':
        return calcAreaDiff(angles=angles, analysisData=analysis,
                            analyticalData=analytical)
    elif statKey == 'dotProd':
        return calcDotProdDiff(analysisData=analysis,
                               analyticalData=analytical)
    elif statKey == 'avgNormError':
        return calcAvgNormError(
            analytical=analytical,
            analysis=analysis,
            domain=angles,
            eSignFactor=eSign)
    elif statKey == 'maxNormError':
        return calcMaxNormError(
            analytical=analytical,
            analysis=analysis,
            domain=angles,
            eSignFactor=eSign)
    elif statKey == 'difference':
        return calcDiffErrors(analytical=analytical, analysis=analysis)
    elif statKey == 'rmsd':
        return calcRMSD(analytical=analytical, analysis=analysis)
    else:
        raise KeyError('{0} does not correspond to a function'.format(statKey))
