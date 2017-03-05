import shelve
import os
import numpy as np

resultsDb = 'resultsDb'
dbRepoDir = 'db'
unionSym = '$'
dbEntyKeysToSkip = ['metadata']


def getDbRepoDir():
    filepath = os.path.abspath(__file__)
    modulesdir = os.path.dirname(filepath)
    root, tdir = os.path.split(modulesdir)
    rootparent, tdir = os.path.split(root)
    for dbdir in [root, rootparent]:
        dbpath = os.path.join(dbdir, dbRepoDir)
        if os.path.exists(dbpath):
            return dbpath
    raise IOError('Cannot find db directory')


def getShelvePathByName(dbName):
    dbRepoDir = getDbRepoDir()
    if checkIfValidShelvePath(dbName):
        dbDir = os.path.join(dbRepoDir, dbName)
        resDir = os.path.join(dbDir, resultsDb)
        return os.path.join(resDir, dbName)
    else:
        return ''


def checkIfValidShelvePath(dbName):
    dbRepoDir = getDbRepoDir()
    dbDir = os.path.join(dbRepoDir, dbName)
    resDb = os.path.join(dbDir, resultsDb)
    shelvePath = os.path.join(resDb, dbName)
    if (os.path.exists(resDb) and
        (dbName in [f.rsplit('.', 1)[0] for f in os.listdir(resDb)] or
         dbName in os.listdir(resDb))):
        return True
    else:
        return False


def verifyIfShelve(dbName):
    dbPath = getShelvePathByName(dbName)
    try:
        db = shelve.open(dbPath, 'r')
        db.close()
        return True
    except:
        return False


def isValidDbName(dbName):
    return (checkIfValidShelvePath(dbName) and verifyIfShelve(dbName))


def getShelveNames():
    return [dbName for dbName in os.listdir(getDbRepoDir())
            if isValidDbName(dbName)]


def getAllShelvePaths():
    return [getShelvePathByName(dbName) for dbName in getShelveNames()]


def createUniqueEntryKey(dbName, entry):
    return dbName + unionSym + entry


def splitUniqueEntryKey(entry):
    return entry.split(unionSym)


def getEntryData(entry):
    dbName, entry = splitUniqueEntryKey(entry)
    dbPath = getShelvePathByName(dbName)
    db = shelve.open(dbPath, 'r')
    data = db[entry]
    db.close()
    return data


def getDbEntryKeys(dbName):
    dbPath = getShelvePathByName(dbName)
    db = shelve.open(dbPath, 'r')
    keys = list(db.keys())
    db.close()
    return keys


def getAllShelveKeys():
    dbNames = getShelveNames()
    keys = set()
    for dbName in dbNames:
        dbPath = getShelvePathByName(dbName)
        db = shelve.open(dbPath, 'r')
        for key in db.keys():
            uniqueKey = createUniqueEntryKey(dbName, key)
            keys.add(uniqueKey)
        db.close()
    return filterDbKeys(keys)


def filterDbKeys(keys):
    return {key for key in keys
            if not splitUniqueEntryKey(key)[1] in dbEntyKeysToSkip}


def getDbKeysFromSubset(subset):
    dbNames = {splitUniqueEntryKey(k)[0] for k in subset}
    dbKeys = {
              dbName: {
                       splitUniqueEntryKey(k)[1] for k in subset
                       if splitUniqueEntryKey(k)[0] == dbName}
              for dbName in dbNames}
    return dbKeys


def getParameterRange(subset, parameterKey):
    simIdVals = extractSimIdParamValuesFromSubset(subset, parameterKey)
    return set(simIdVals.values())


def getSubsetByCriterion(subset, parameterKey, criterion):
    simIdVals = extractSimIdParamValuesFromSubset(subset, parameterKey)
    return {simId for simId in simIdVals.keys()
            if simIdVals[simId] == criterion}


def extractSimIdParamValuesFromSubset(subset, parameterKey):
    dbKeys = getDbKeysFromSubset(subset)
    simIdVals = {}
    for dbName in dbKeys.keys():
        dbPath = getShelvePathByName(dbName)
        db = shelve.open(dbPath, 'r')
        for key in dbKeys[dbName]:
            simId = createUniqueEntryKey(dbName, key)
            simIdVals[simId] = extractDataFromEntry(db[key], parameterKey)
        db.close()
    return simIdVals


def extractDataFromEntry(entryData, keyword):
    inp = entryData['input']
    rep = entryData['reports']
    try:
        res = entryData['odb']['results']
    except KeyError:
        pass

    if keyword == 'analysisSuccess':
        return rep['successfulAnalysis']
    if keyword == 'crackRatio':
        a = inp['crackParameters']['a']
        b = inp['crackParameters']['b']
        return float(a)/float(b)
    if keyword == 'a':
        return inp['crackParameters']['a']
    if keyword == 'b':
        return inp['crackParameters']['b']
    if keyword == 'sigma':
        return inp['analysisParameters']['sigma']
    if keyword == 'gamma':
        return inp['analysisParameters']['gamma']
    if keyword == 'omega':
        return inp['analysisParameters']['omega']
    if keyword == 'analysisType':
        return inp['analysisType']
    if keyword == 'modelType':
        return inp['modelType']
    if keyword == 'transform':
        try:
            return inp['meshParameters']['transformationType']
        except KeyError:
            return None
    if keyword == 'elements':
        return inp['meshParameters']['elements']
    # Seed parameters
# FEM
    if keyword == 'czrSeeds':
        try:
            return inp['seedParameters']['crackZoneRefinementSeeds']
        except KeyError:
            return None
    if keyword == 'crSeeds':
        try:
            return inp['seedParameters']['containerRefinementSeeds']
        except KeyError:
            return None
    if keyword == 'czmSeeds':
        try:
            return inp['seedParameters']['crackZoneMainSeeds']
        except KeyError:
            return None
    if keyword == 'arcSeeds':
        try:
            return inp['seedParameters']['arcSeeds']
        except KeyError:
            return None
    # XFEM CP
    if keyword == 'allEdges':
        try:
            return inp['seedParameters']['allEdges']
        except KeyError:
            return None
    if keyword == 'crackEdges':
        try:
            return inp['seedParameters']['crackEdges']
        except KeyError:
            return None
    # TODO XFEM MP & XFEM simple

    if keyword == 'h':
        return inp['geometricParameters']['containerHeight']
    if keyword == 'd':
        return 2*inp['geometricParameters']['containerRadius']
    if keyword == 'crackType':
        return inp['crackParameters']['crackType']
    if keyword == 'E':
        return inp['material']['E']
    if keyword == 'v':
        return inp['material']['v']
    if keyword == 'timeToCalcInSec':
        return (rep['analysis']['timeOfCalculation'] -
                rep['analysis']['creationTime'])

    if keyword == 'angles':
        try:
            return res['sortedBetaAngles']
        except KeyError:
            return None
    if keyword == 'K1':
        try:
            return res['sortedSIFs']['K1']
        except KeyError:
            return None
    if keyword == 'K2':
        try:
            return res['sortedSIFs']['K2']
        except KeyError:
            return None
    if keyword == 'K3':
        try:
            return res['sortedSIFs']['K3']
        except KeyError:
            return None
    if keyword == 'J':
        try:
            return res['sortedSIFs']['J']
        except KeyError:
            return None
    if keyword == 'Cpd':
        try:
            return res['sortedSIFs']['Cpd']
        except KeyError:
            return None
    if keyword == 'JKs':
        try:
            return res['sortedSIFs']['JKs']
        except KeyError:
            return None
    if keyword == 'T':
        try:
            return res['sortedSIFs']['T']
        except KeyError:
            return None
