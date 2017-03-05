import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import scipy.stats as stats
import trees
import dbaccess as dba
import dataProcessing as dp
import sessionFuncs as sf
from imp import reload
from types import *


class LeavesQueue(object):

    def __init__(self):
        self.queue = set()
        self.namesLen = []
        self.nd = 2
        self.updated = False
        self.cols = ['Num.', 'Analysis', 'Model', 'Elements']

    def addLeaf(self, leaf):
        self.queue.add(leaf)
        self.updated = False

    def initNamesLen(self):
        names = []
        self.namesLen = [max(len(self.cols[0]), len(str(len(self.queue))))]
        for node in self.queue:
            names.append(self.getNodeNames(node, 0, []))
        names = np.array(names)
        for i in range(len(names[0])):
            self.namesLen.append(len(max(names[::, i], key=lambda x: len(x))))
        for i in range(len(self.cols)):
            if self.namesLen[i] < len(self.cols[i]):
                self.namesLen[i] = len(self.cols[i])

    def getNodeNames(self, node, count, names):
        if count == self.nd:
            names.append(node.getName())
            return names[::-1]
        else:
            names.append(node.getName())
            node = node.getParent()
            return self.getNodeNames(node, count + 1, names)

    def createNodeNamesSL(self, node):
        names = self.getNodeNames(node, 0, [])
        nameSpaces = []
        for i in range(len(names)):
            m = self.namesLen[i + 1] - len(names[i])
            nameSpaces.append(names[i] + m * ' ')
        return nameSpaces

    def getSortedQueue(self):
        return sorted(list(self.queue),
                      key=lambda x: self.createNodeNamesSL(x))

    def getQueueDict(self):
        q = self.getSortedQueue()
        return dict([(i + 1, q[i]) for i in range(len(q))])

    def printTitle(self):
        self.initNamesLen()
        ds, rs = '', ''
        for i in range(len(self.cols)):
            f = int((self.namesLen[i] - len(self.cols[i])) / 2)
            b = self.namesLen[i] - len(self.cols[i]) - f + 1
            rs = rs + '| ' + f * ' ' + self.cols[i] + b * ' '
            ds = ds + '|' + (self.namesLen[i] + 2) * '-'
        print rs
        print ds

    def printQueueItem(self, num):
        self.initNamesLen()
        try:
            q = self.getSortedQueue()
            node = q[num - 1]
            numStr = (self.namesLen[0] - len(str(num))) * ' ' + str(num)
            reprStr = '| {0}'.format(numStr)
            for name in self.createNodeNamesSL(node):
                reprStr = '{0} | {1}'.format(reprStr, name)
            print reprStr
        except IndexError:
            print 'The queue has only {0} entries.'.format(len(self.queue))

    def printQueue(self):
        self.printTitle()
        for i in range(len(self.queue)):
            self.printQueueItem(i + 1)
        self.updated = True

    def getQueueItemByNumber(self, num):
        if self.update:
            try:
                q = self.getSortedQueue()
                return q[num - 1]
            except IndexError:
                print 'The queue has only {0} entries.'.format(len(self.queue))
        else:
            print 'Print the queue to verify your selection.'


class CompQueue(object):

    def __init__(self):
        self.queue = set()
        self.outdatedMsg = 'Call printQueue() to update the queue to verify your selection and then try again.'
        self.oldmsg = 'Entered number may not correspond to the displayed table.\nCall printQueue() first and verify your selection.'

    def addSimId(self, simId):
        if isinstance(simId, (set, frozenset)):
            self.queue = self.queue | simId
        elif isinstance(simId, str):
            self.queue.add(simId)
        elif isinstance(simId, (list, tuple)):
            self.queue = self.queue | set(simId)
        else:
            raise TypeError
        self.updated = False

    def getQueue(self):
        return sorted(list(self.queue))

    def getByNumber(self, number):
        assert isinstance(number, int), 'Valid arguments are integers'
        assert self.updated, self.outdatedMsg
        assert len(self.queue) > 0, 'The queue is empty.'
        assert number > 0 and number < len(
            self.queue) + 1, 'The queue has {0} members. Valid arguments are integers from 1 to {0}'.format(len(self.queue))
        return sorted(list(self.queue))[number - 1]

    def getQueueDict(self):
        return {i: self.getByNumber(i) for i in range(1, len(self.queue) + 1)}

    def removeFromQueue(self, number):
        if isinstance(number, NoneType):
            pass
        elif isinstance(number, int):
            member = self.getByNumber(number)
            self.queue.remove(member)
            print '{0} removed from queue.'.format(number)
            self.updated = False
        else:
            raise AssertionError('Valid arguments are integers.')

    def removeSimIdFromQueue(self, simId):
        if isinstance(simId, NoneType):
            pass
        elif isinstance(simId, str):
            if simId in self.queue:
                self.queue.remove(simId)
                self.updated = False
                print 'Simulation {0} removed from queue.'.format(simId)
            else:
                print 'Warning! Simulation {0} not in queue.'.format(simId)
        else:
            raise AssertionError('Valid arguments are strings')

    def loadSession(self, node):
        nodeSims = node.getSuccessfulMembers()
        sessionSims = sf.getSimIdsFromShelve('successful')
        self.addSimId(nodeSims & sessionSims)
        print 'Loaded {0} simulstions from previous sessions and added to queue.'.format(len(nodeSims & sessionSims))

    def __len__(self):
        return len(self.queue)

    def getGeomParamRepr(self, ad):
        d = ad.getParameter('diameter')
        dStr = self.createValueStr('Diam', d)
        h = ad.getParameter('height')
        hStr = self.createValueStr('Height', h)
        return dStr + hStr

    def getMeshParamRepr(self, ad):
        mesh = ad.getMeshParams()
        rep = ''
        for k in mesh.keys():
            rep = rep + self.createValueStr(k, mesh[k], 4)
        return rep

    def createValueStr(self, valName, val, length=6):
        return ' {0}:{1}{2} |'.format(
            valName, ' ' * (length - len(str(val))), val)

    def printQueue(self):
        count = 1
        print '|Num. |        Container            |   Seed Parameters'
        print '|-----|-----------------------------|----------------------------------'
        for s in sorted(list(self.queue)):
            ad = dp.AnalysisData(s)
            num = '|{0}{1} |'.format(' ' * (4 - len(str(count))), count)
            num = num + self.getGeomParamRepr(ad)
            num = num + self.getMeshParamRepr(ad)
            print num
            count += 1
        self.updated = True

    def plotComp(self, fig):
        q = sorted(list(self.queue))
        axes = []
        sifs = ['K1', 'K2', 'K3']
        ylabels = {'K1': '$K_{I}$', 'K2': '$K_{II}$', 'K3': '$K_{III}$'}
        res = []
        ad = dp.AnalysisData(q[0])
        ad.calcAnSol()
        ad.calculateStats()
        for i in range(len(sifs)):
            axes.append(fig.add_subplot(len(sifs) * 100 + 10 + (i + 1)))
            analytical = axes[i].plot(ad.getAngles(), ad.getAnSol()[sifs[i]])
            for simId in q:
                ad1 = dp.AnalysisData(simId)
                ad1.calcAnSol()
                ad1.calculateStats()
                res = res + axes[i].plot(ad1.getAngles(),
                                         ad1.getResults()[sifs[i]])
            axes[i].set_ylabel(ylabels[sifs[i]])
            axes[i].set_xlabel('angles')
            axes[i].set_xlim(0, 360)
            axes[i].grid(True)
        axes[0].legend(
                       analytical + res[0:len(q)],
                       ['SIF analytical'] +
                       ['Sim Num: {0}'.format(i + 1) for i in range(len(q))],
                       bbox_to_anchor=(1.02, 1),
                       loc=2,
                       borderaxespad=0.)
