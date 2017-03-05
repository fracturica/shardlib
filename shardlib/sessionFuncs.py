import shelve
import os
import dbaccess as dba
import trees as tr
import time

sessionDirName = 'sessiondata'
sShelveName = 'successfulSimIds'
fShelveName = 'failedSimIds'
dataKey = 'data'


def getSessionDir():
    currentDir = os.path.dirname(os.path.abspath(__file__))
    pdir, td = os.path.split(currentDir)
    shelveDir = os.path.join(pdir, sessionDirName)
    return shelveDir


def getShelvePath(simIdType):
    if simIdType == 'successful':
        shName = sShelveName
    elif simIdType == 'failed':
        shName = fShelveName
    else:
        raise KeyError('Valid argument values: "successful" of "failed"')
    sessionDir = getSessionDir()
    return os.path.join(sessionDir, shName)


def createNewSessionFiles(createFlag):
    if createFlag:
        sessDir = getSessionDir()
        files = set([f for f in os.listdir(sessDir)
                     if os.path.isfile(os.path.join(sessDir, f))])
        shelveNames = set([sShelveName, fShelveName])
        timeStamp = time.localtime()
        for f in shelveNames & files:
            backupFile(sessDir, f, timeStamp)
        createShelves()
        print 'New session files created.'


def backupFile(fileDir, fileName, timeStamp):
    path1 = os.path.join(fileDir, fileName)
    assert os.path.isfile(path1)
    pref = time.strftime('%d.%b.%Y %H:%M:%S', timeStamp)
    newName = '{0}_backup_{1}'.format(pref, fileName)
    path2 = os.path.join(fileDir, newName)
    os.rename(path1, path2)
    print 'backed up {0} as {1}'.format(fileName, newName)


def createShelves():
    simTypes = ['successful', 'failed']
    for st in simTypes:
        shPath = getShelvePath(st)
        db = shelve.open(shPath)
        db[dataKey] = set()
        db.close()
        print 'Created new session file for {0} simIds'.format(st)


def writeToShelve(simIds, simIdType):
    if simIds is None:
        return
    assert isinstance(simIds, (str, set, list, tuple))
    assert len(simIds) >= 1
    if isinstance(simIds, (set, list, tuple)):
        assert '' not in simIds
    if isinstance(simIds, str):
        simIds = set([simIds])
    elif isinstance(simIds, (list, tuple)):
        simIds = set(simIds)

    try:
        shPath = getShelvePath(simIdType)
        db = shelve.open(shPath)
        sims = db[dataKey]
        before = len(simIds)
        sims = sims | simIds
        db[dataKey] = sims
        after = len(sims)
        simLen = after - before
        print 'Saved successfully {0} simIds'.format(simLen)
    except:
        print 'Error occurred.'
    finally:
        db.close()


def getSimIdsFromShelve(simIdType):
    sims = None
    shPath = getShelvePath(simIdType)
    try:
        db = shelve.open(shPath, 'r')
        sims = db[dataKey]
        db.close()
    finally:
        pass
    return sims


def assignNodeSimsAsFailed(trees, simIds):
    assert isinstance(simIds, (set, list, tuple, frozenset))
    assert isinstance(trees, (set, list, tuple, frozenset))
    numChanges = 0
    numChangedTrees = 0
    for t in trees:
        rootNode = t.getRootNode()
        for s in simIds:
            numChanges += rootNode.assignMemberAsFailed(s, False)
        numChangedTrees += 1
    return numChanges, numChangedTrees


def setSimIdAsFailed(trees, simIds, rowlen=80, node=None):
    if node is not None:
        changes, treeChanges = [], []
        node.printStats2()
        ch, trCh = assignNodeSimsAsFailed(trees, simIds)
        changes.append(ch)
        treeChanges.append(trCh)
        info = ' {0} changes in {1} trees '.format(
            sum(changes), sum(treeChanges))
        f = int((rowlen - len(info)) * 0.5)
        b = rowlen - f - len(info)
        print '-' * f, info, '-' * b
        node.printNode(node, rowlen)
    else:
        assignNodeSimsAsFailed(trees, simIds)
