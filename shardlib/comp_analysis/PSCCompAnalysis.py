import sessionFuncs as sf
import dataProcessing as dp

import numpy as np
import scipy.stats as stats

import matplotlib as mpl
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA

from types import *


class PSCCompAnalysis(object):

    def __init__(self, simIds):
        self.sims = simIds
        self.sif = 'K1'
        self.dists = ['norm', 't']
        self.errType = 'difference'
        self.dKeys = ['smaller', 'equal', 'larger']
        self.errs = {key: np.array([]) for key in self.dKeys}
        self.simIds = {key: set() for key in self.dKeys}

    def divideSimIds(self, limD, limH):
        self.d = limD
        self.h = limH
        for s in self.sims:
            ad = dp.AnalysisData(s)
            ad.calcAnSol()
            ad.calculateStats()
            simD = ad.getContainerDiam()
            simH = ad.getContainerHeight()
            errs = ad.getErrorReports()[self.errType][self.sif]
            if simD == limD and simH == limH:
                key = self.dKeys[1]
            elif simD >= limD and simH >= limH:
                key = self.dKeys[2]
            else:
                key = self.dKeys[0]
            self.simIds[key].add(s)
            self.errs[key] = np.concatenate((self.errs[key], errs))

    def delEmptySimIdClassificationSets(self):
        for k in self.dKeys:
            if len(self.simIds[k]) == 0:
                del self.simIds[k]
                del self.errs[k]

    def manipulateErrors(self):
        for k in self.errs.keys():
            avg = np.average(self.errs[k])
            self.errs[k] = [e for e in self.errs[k] if (
                (e <= avg + self.lim) and (e >= avg - self.lim))]

    def createFigureAxes(self):
        self.axes = []
        ncols = 1
        nrows = len(self.simIds)
        gs = mpl.gridspec.GridSpec(nrows=nrows, ncols=ncols)
        gs.update(wspace=0.04, hspace=0.08)
        for i in range(ncols * nrows):
            self.axes.append(self.fig.add_subplot(gs[i]))
            self.axes[i].grid(True)

    def createPSCStatPlots(self, limD, limH, bins, lim, fig):
        self.limD = limD
        self.limH = limH
        self.axes = []
        self.fig = fig
        self.lim = lim
        self.bins = bins
        self.divideSimIds(limD, limH)
        self.delEmptySimIdClassificationSets()
        self.manipulateErrors()
        self.createFigureAxes()
        i = 0
        for k in self.dKeys:
            if k in self.simIds:
                self.createPSCHistProbPlots(i, k)
                i += 1
        self.axes[-1].set_xlabel('errors difference')

    def createPSCHistProbPlots(self, i, key):
        errs = self.errs[key]
        x = np.arange(min(errs), max(errs), 0.1)

        mu, sigma = stats.norm.fit(errs)
        normpdf = stats.norm.pdf(x, mu, sigma)
        shape, loc, scale = stats.t.fit(errs)
        rv = stats.t(shape, loc=loc, scale=scale)

        self.axes[i].hist(errs, self.bins, normed=True,
                          color='MidnightBlue', alpha=0.7,
                          label='Errors {0}'.format(self.sif))
        self.axes[i].plot(x, normpdf,
                          'r', label='Normal fit')
        self.axes[i].plot(x, rv.pdf(x),
                          'g', label='T fit')

        text = self.getContainerDescription(key)
        self.axes[i].text(0.01, 0.9, text,
                          transform=self.axes[i].transAxes,
                          fontsize=14)
        self.axes[i].text(0.01, 0.7,
                          '$\mu=${0:.3}\n$\sigma=${1:.3}'.format(mu, sigma),
                          transform=self.axes[i].transAxes,
                          fontsize=14)

        h, l = self.axes[i].get_legend_handles_labels()
        self.axes[i].legend(h, l)

        self.axes[i].set_ylabel('Probability')
        self.axes[i].set_xlim((-self.lim, self.lim))

    def createPSCProbPlots(self, i, fig):
        i = i - 1
        keys = []
        for k in self.dKeys:
            if k in self.simIds:
                keys.append(k)
        errs = self.errs[keys[i]]

        text = self.getContainerDescription(keys[i])
        fig.suptitle(text, fontsize=14)
        mu, sigma = stats.norm.fit(errs)
        shape, loc, scale = stats.t.fit(errs)
        for i in range(len(self.dists)):
            dist = self.dists[i]
            ax = PLTAxes(fig.add_subplot(len(self.dists), 1, i + 1))
            if dist == 'norm':
                stats.probplot(errs, dist='norm', fit=True, plot=ax)
                ax.title('Normal probability plot')
            elif dist == 't':
                stats.probplot(errs, dist='t', fit=True,
                               sparams=(loc, scale),
                               plot=ax)
                ax.title('T probability plot')

    def getContainerDescription(self, key):
        if key == 'smaller':
            d = '<{0}'.format(self.limD)
            h = '<{0}'.format(self.limH)
        elif key == 'equal':
            d = '={0}'.format(self.limD)
            h = '={0}'.format(self.limH)
        else:
            d = '>{0}'.format(self.limD)
            h = '>{0}'.format(self.limH)
        text = 'Container d{0}, h{1}'.format(d, h)
        return text


class PLTAxes(object):

    def __init__(self, axes):
        self.axes = axes
        self.axes.grid(True)

    def plot(self, *args, **kargs):
        createPlot = True
        for arg in args:
            if isinstance(arg, (np.ndarray,)):
                if np.isnan(np.min(arg)):
                    createPlot = False
        if createPlot:
            self.axes.plot(*args, **kargs)

    def title(self, *args):
        self.axes.set_title(args[0])

    def xlabel(self, *args):
        self.axes.set_xlabel(args[0])

    def ylabel(self, *args):
        self.axes.set_ylabel(args[0])

    def text(self, *args):
        self.axes.text(args[0], args[1], args[2])


def assignSimIdAsFailed(trees, cq, selIdNum):
    if isinstance(selIdNum, NoneType):
        pass
    elif selIdNum in cq.getQueueDict().keys():
        simId = cq.getQueueDict()[selIdNum]
        cq.removeSimIdFromQueue(simId)
        sf.writeToShelve(simId, 'failed')
        sf.setSimIdAsFailed(trees, [simId])
        print simId
    else:
        print 'Verify the selIdNum argument value'
