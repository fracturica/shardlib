import numpy as np
import dbaccess as dba
import miscFuncs as mf
import anSol
import matplotlib.pyplot as plt


class AnalysisData(object):

    def __init__(
            self,
            uniqueEntryKey,
            sifs=[
                'K1',
                'K2',
                'K3'],
            loadFromDb=True,
            eSignFactor='areas'):
        self.uek = uniqueEntryKey
        self.eSignFactor = eSignFactor  # 'dotProd'
        self.data = {
            'a': None,
            'b': None,
            'omega': None,
            'gamma': None,
            'sigma': None,
            'h': None,
            'd': None,
            'E': None,
            'v': None,
            'material': None,
            'crackType': None,
            'crackRatio': None,
            'analysisType': None,
            'elements': None,
            'modelType': None,
            'transform': None,
            'analysisSuccess': None,
            'czrSeeds': None,
            'crSeeds': None,
            'czmSeeds': None,
            'arcSeeds': None,
            'allEdges': None,
            'crackEdges': None}
        self.sifs = sifs
        self.errors = {'areaDiff': {}, 'dotProd': {}, 'difference': {},
                       'avgNormError': {}, 'maxNormError': {}, 'rmsd': {}}
        self.calculatedErrors = False
        self.anSol = {}
        self.results = {}
        self.angles = []
        self.rawres = {}
        if loadFromDb:
            self.extractDataFromDb()

    def calcAnSol(self):
        for sif in self.sifs:
            self.anSol[sif] = anSol.calcAnSolWrapper(
                sifKey=sif,
                majorAxis=self.data['a'],
                minorAxis=self.data['b'],
                v=self.data['v'],
                betas=self.angles,
                gamma=self.data['gamma'],
                omega=self.data['omega'],
                tensileStress=self.data['sigma'])

    def extractDataFromDb(self):
        data = dba.getEntryData(self.uek)
        for key in self.data.keys():
            self.data[key] = dba.extractDataFromEntry(data, key)
        if self.data['analysisSuccess']:
            self.angles = dba.extractDataFromEntry(data, 'angles')
            for sif in self.sifs:
                self.rawres[sif] = dba.extractDataFromEntry(data, sif)

    def calculateStats(self):
        if self.data['analysisSuccess'] and not self.calculatedErrors:
            for sif in self.sifs:
                self.results[sif] = mf.contourAveraging(
                    self.rawres[sif], len(self.rawres[sif].keys()) - 2)
                for e in self.errors.keys():
                    try:
                        self.errors[e][sif] = mf.calcStatsWrapper(
                            statKey=e, angles=self.angles,
                            analytical=self.anSol[sif],
                            analysis=self.results[sif],
                            eSign=self.eSignFactor)
                    except ZeroDivisionError:
                        self.errors[e][sif] = float('NaN')
        self.calculatedErrors = True

    def getAnalysisSuccess(self):
        assert self.data['analysisSuccess'] is not None
        return self.data['analysisSuccess']

    def getErrorReports(self):
        return self.errors

    def getResults(self):
        return self.results

    def getAnSol(self):
        return self.anSol

    def getAngles(self):
        return self.angles

    def getAnSolParams(self):
        params = ['a', 'b', 'omega', 'gamma', 'sigma', 'v']
        return {key: self.data[key] for key in params}

    def getCrackRatio(self):
        return self.data['crackRatio']

    def getAnalysisType(self):
        return self.data['analysisType']

    def getTransformType(self):
        return self.data['transform']

    def getModelType(self):
        if self.getAnalysisType() == 'FEM':
            return self.getTransformType()
        else:
            return self.data['modelType']

    def getElementType(self):
        return self.data['elements']

    def getEntryKey(self):
        return self.uek

    def getContainerDiam(self):
        return self.data['d']

    def getContainerHeight(self):
        return self.data['h']

    def getParameter(self, parKey):
        paramPair = {'crackRatio': self.getCrackRatio,
                     'analysisType': self.getAnalysisType,
                     'modelType': self.getModelType,
                     'transform': self.getTransformType,
                     'elements': self.getElementType,
                     'entryKey': self.getEntryKey,
                     'diameter': self.getContainerDiam,
                     'height': self.getContainerHeight}
        return paramPair[parKey]()

    def get3dScatterPlotData(self):
        return self.data['d'], self.data['h'], self.data['allEdges']

    def getMeshParams(self):
        return {
            'crackEdges': self.data['crackEdges'],
            'allEdges': self.data['allEdges']}


class AnalysisNodeData(object):

    def __init__(self, node, sifs, eSignFactor='areas'):
        assert eSignFactor in ['areas', 'dotProd']
        self.eSignFactor = eSignFactor
        self.node = node
        self.sifs = sifs
        self.angles = np.array([])
        self.results = {s: np.array([]) for s in self.sifs}
        self.anSol = {s: np.array([]) for s in self.sifs}
        self.anSolParams = {
            'a': set([]), 'b': set([]),
            'omega': set([]), 'gamma': set([]),
            'sigma': set([]), 'v': set([])}
        self.errors = {}
        self.estimates = {
            e: {} for e in [
                'areaDiff',
                'dotProd',
                'avgNormError',
                'maxNormError',
                'rmsd']}

    def performOperations(self):
        self.extractDataFromSims()
        self.fixAngleValues()
        self.sortDataByAnglesData()
        self.verifyAnSolParams()
        self.calcErrors()
        self.calcEstimates()

    def extractDataFromSims(self):
        simsS = self.node.getSuccessfulMembers()
        for sim in simsS:
            self.extractDataFromSimId(sim)

    def extractDataFromSimId(self, simId):
        ad = AnalysisData(simId)
        ad.calcAnSol()
        ad.calculateStats()
        self.angles = np.concatenate(
            (self.angles, ad.getAngles()))
        for s in self.sifs:
            self.results[s] = np.concatenate(
                (self.results[s], ad.getResults()[s]))
            self.anSol[s] = np.concatenate(
                (self.anSol[s], ad.getAnSol()[s]))
        self.extractAnSolParams(ad)

    def extractAnSolParams(self, ad):
        params = ad.getAnSolParams()
        for key in params.keys():
            self.anSolParams[key].add(params[key])

    def verifyAnSolParams(self):
        for key in self.anSolParams.keys():
            assert len(self.anSolParams[key]) == 1
            self.anSolParams[key] = float(list(self.anSolParams[key])[0])

    def fixAngleValues(self):
        self.angles = np.array(self.angles) % 360

    def sortDataByAnglesData(self):
        ind = np.argsort(self.angles)
        self.angles = np.sort(self.angles)
        for s in self.sifs:
            self.anSol[s] = np.array([self.anSol[s][i] for i in ind])
            self.results[s] = np.array([self.results[s][i] for i in ind])

    def calcErrors(self):
        err = ['difference', 'normedDiff']
        self.errors = {e: {} for e in err}
        for s in self.sifs:
            self.errors['difference'][s] = mf.calcDiffErrors(
                self.anSol[s], self.results[s])

    def calcEstimates(self):
        for sif in self.sifs:
            for e in self.estimates.keys():
                try:
                    self.estimates[e][sif] = mf.calcStatsWrapper(
                        statKey=e, angles=self.angles,
                        analytical=self.anSol[sif],
                        analysis=self.results[sif],
                        eSign=self.eSignFactor)
                except ZeroDivisionError:
                    self.estimates[e][sif] = float('NaN')

    def getAngles(self):
        return self.angles

    def getAnSol(self):
        return self.anSol

    def getErrors(self):
        return self.errors

    def getEstimates(self):
        return self.estimates

    def getResults(self):
        return self.results

    def getAnSolParams(self):
        return self.anSolParams

    def getDataByType(self, dataType):
        if dataType == 'results':
            return self.results
        elif dataType == 'difference':
            return self.errors['difference']
        elif dataType == 'normedDif':
            return self.errors['normedDiff']

    def calcSIFsForSigmaAndSIF(self, sigma, sif):
        return anSol.calcAnSolWrapper(sifKey=sif,
                                      majorAxis=self.anSolParams['a'],
                                      minorAxis=self.anSolParams['b'],
                                      v=self.anSolParams['v'],
                                      betas=self.angles,
                                      gamma=self.anSolParams['gamma'],
                                      omega=self.anSolParams['omega'],
                                      tensileStress=sigma)


def getMeshParams(simId):
    ad = AnalysisData(simId)
    return ad.getMeshParams()
