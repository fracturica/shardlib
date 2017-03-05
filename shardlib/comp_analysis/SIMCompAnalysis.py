import dataProcessing as dp
import plotFuncs as pf

import numpy as np
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA

from matplotlib.path import Path
from mpl_toolkits.mplot3d import Axes3D
import matplotlib as mpl

from compAnalysisBase import CompAnalysisBase


class SIMCompAnalysis(CompAnalysisBase):

    def __init__(self, leavesQueue, criteria, sifs):
        self.queue = leavesQueue
        self.sifs = sifs
        self.crit = criteria

    def printQueueItems(self, items):
        self.queue.printTitle()
        for i in sorted(items):
            self.queue.printQueueItem(i)

    def getItemNodeDict(self, items, queue):
        qdict = queue.getQueueDict()
        return dict([(i, qdict[i]) for i in items])

    def calcAlphaVal(self, sif, item):
        vals = len(self.dataDicts[0][0][sif][item])
        if vals > 1000:
            return 0.1
        else:
            return 1


class BoxCompPlot(SIMCompAnalysis):

    def createCompBoxPlot(self, items, errType, fig):
        self.items = items
        self.errType = errType
        self.createDataDictAndEstBoxPlot()
        self.createDataStrBoxPlot()
        self.createFigure(fig)

    def createDataStrBoxPlot(self):
        dd = self.getItemNodeDict(self.items, self.queue)
        optKey = self.getLeavesOptKey()
        data = [dd, optKey, 'Number in Queue', '']
        self.dataStr = [data]

    def getLeavesOptKey(self):
        return sorted(self.est.items(), key=lambda x: abs(x[1]))[0][0]

    def createDataDictAndEstBoxPlot(self):
        dataDict = {s: {} for s in self.sifs}
        est = {i: {} for i in self.items}
        dd = self.getItemNodeDict(self.items, self.queue)
        for i in self.items:
            node = dd[i]
            errs, est[i] = self.getNodeErrsEst(node)
            for s in self.sifs:
                dataDict[s][i] = errs[s]
        self.est = {i: est[i][self.crit[1]] for i in self.items}
        self.dataDicts = [dataDict]

    def getNodeErrsEst(self, node):
        adn = dp.AnalysisNodeData(node, self.sifs)
        adn.performOperations()
        est = adn.getEstimates()[self.crit[0]]
        errs = adn.getErrors()[self.errType]
        return errs, est


class HistCompPlot(SIMCompAnalysis):

    def createCompHistPlot(self, items, errType, xlim, fig):
        self.fig = fig
        self.items = items
        self.errType = errType
        self.xlim = xlim
        self.createDataStr()
        self.createDataDict()
        self.createFigure()

    def createDataStr(self):
        dd = self.getItemNodeDict(self.items.keys(), self.queue)
        xlabel = 'errors "{0}"'.format(self.errType)
        data = [dd, None, xlabel, 'hist']
        self.dataStr = [data]

    def createDataDict(self):
        data = {s: {} for s in self.sifs}
        for i in self.items.keys():
            node = self.dataStr[0][0][i]
            errs = self.getNodeErrors(node)
            for s in self.sifs:
                data[s][i] = errs[s]
        self.dataDicts = [data]

    def getNodeErrors(self, node):
        adn = dp.AnalysisNodeData(node, self.sifs)
        adn.performOperations()
        errs = adn.getErrors()[self.errType]
        return errs

    def setAxesXlim(self):
        for ax in self.axes:
            ax.set_xlim(self.xlim)

    def setAxesYlim(self):
        ymin, ymax = 10e16, 10e-16
        for ax in self.axes:
            y1, y2 = ax.get_ylim()
            ymin = y1 if y1 < ymin else ymin
            ymax = y2 if y2 > ymax else ymax
        for ax in self.axes:
            ax.set_ylim((ymin, ymax))

    def setLegend(self, handles):
        text = 'Node: '
        labels = [text + str(i) for i in sorted(handles.keys())]
        handles = [handles[i] for i in sorted(handles.keys())]
        self.axes[0].legend(handles, labels, bbox_to_anchor=(1.02, 1),
                            loc=2, borderaxespad=0)

    def createFigure(self):
        self.axes = []
        self.createFigureAxes()
        handles = {}
        for k in range(len(self.axes)):
            s = self.sifs[k]
            for i in self.items.keys():
                n, b, p = self.axes[k].hist(
                    self.dataDicts[0][s][i],
                    self.items[i],
                    normed=True,
                    alpha=0.5)
                handles[i] = p[0]
        self.setAxesXlim()
        self.setAxesYlim()
        self.setLegend(handles)
        self.setXlabels()
        self.printQueueItems(self.items.keys())


class CorrCompPlot(SIMCompAnalysis):

    def createCompCorrPlot(self, items, quantityType, ylim, fig):
        self.fig = fig
        self.items = items
        self.qt = quantityType
        self.ylim = ylim
        self.createDataStr()
        self.createDataDict()
        self.createFigure()

    def createDataStr(self):
        dd = self.getItemNodeDict(self.items, self.queue)
        data = [dd, None, 'analytical values', 'analysis vs analytical']
        self.dataStr = [data]

    def createDataDict(self):
        dataX = {s: {} for s in self.sifs}
        dataY = {s: {} for s in self.sifs}
        for i in self.items:
            node = self.dataStr[0][0][i]
            anSol, res = self.getNodeParams(node)
            for s in self.sifs:
                dataX[s][i] = anSol[s]
                dataY[s][i] = res[s]
        self.dataDicts = [[dataX, dataY]]

    def getNodeParams(self, node):
        adn = dp.AnalysisNodeData(node, self.sifs)
        adn.performOperations()
        anSol = adn.getAnSol()
        res = adn.getDataByType(self.qt)
        return anSol, res

    def getReferenceXYVals(self):
        minV = {s: 10e16 for s in self.sifs}
        maxV = {s: -10e16 for s in self.sifs}
        for s in self.sifs:
            for i in self.items:
                mn = min(self.dataDicts[0][0][s][i])
                mx = max(self.dataDicts[0][0][s][i])
                minV[s] = mn if mn < minV[s] else minV[s]
                maxV[s] = mx if mx > maxV[s] else maxV[s]
        if self.qt == 'results':
            refX = {s: [minV[s], maxV[s]] for s in self.sifs}
            return refX, refX
        elif self.qt in ['difference', 'normedDiff']:
            refX = {s: [max(0, minV[s]), maxV[s]] for s in self.sifs}
            refY = {s: [0, 0] for s in self.sifs}
            return refX, refY
        else:
            raise NotImplementedError

    def getXYVals(self, sif, item):
        if self.qt == 'results':
            X = self.dataDicts[0][0][sif][item]
            Y = self.dataDicts[0][1][sif][item]
        elif self.qt in ['difference', 'normedDiff']:
            X = np.abs(self.dataDicts[0][0][sif][item])
            Y = self.dataDicts[0][1][sif][item]
        else:
            raise NotImplementedError
        return X, Y

    def createPlot(self):
        self.handles = {}
        refX, refY = self.getReferenceXYVals()
        for k in range(len(self.axes)):
            s = self.sifs[k]
            for i in self.items:
                alpha = self.calcAlphaVal(s, i)
                X, Y = self.getXYVals(s, i)
                p, = self.axes[k].plot(X, Y, '.', alpha=alpha)
                self.handles[i] = p
            r, = self.axes[k].plot(refX[s], refY[s], 'k', lw=1.5)
        self.handles['reference'] = r

    def setXLim(self):
        refX, refY = self.getReferenceXYVals()
        for k in range(len(self.axes)):
            s = self.sifs[k]
            self.axes[k].set_xlim(refX[s])

    def setLegend(self):
        text = 'Node: '
        labels = [text + str(i) for i in self.items]
        handles = [self.handles[i] for i in self.items]
        if 'reference' in self.handles.keys():
            handles.append(self.handles['reference'])
            labels.append('ref line')
        self.axes[0].legend(handles, labels, bbox_to_anchor=(1.02, 1),
                            loc=2, borderaxespad=0)

    def setYLim(self):
        if isinstance(self.ylim, (list, tuple)):
            for ax in self.axes:
                ax.set_ylim(self.ylim)

    def createFigure(self):
        self.axes = []
        self.createFigureAxes()
        self.createPlot()
        self.setXLim()
        self.setLegend()
        self.printQueueItems(self.items)
        self.setYLim()


class RangeCompPlot(SIMCompAnalysis):

    def createCompRangePlot(self, items, opts, fig):
        self.fig = fig
        self.items = items
        self.opts = opts
        self.createDataStr()
        self.createDataDict()
        self.createFigure()

    def createDataStr(self):
        self.dataStr = []
        qdict = self.queue.getQueueDict()
        for k in sorted(self.items.keys()):
            optSim = self.getOptSim(qdict[k])
            data = [{k: qdict[k]}, optSim, 'angles',
                    self.getSubplotTitle(qdict[k])]
            self.dataStr.append(data)

    def getOptSim(self, node):
        if self.opts['optSim']:
            sims = node.getSuccessfulMembers()
            optSim = pf.getSimIdsWithLowestErrorPerDH(
                sims, self.crit[0], self.crit[1]).values()[0][0]
            return optSim
        else:
            return None

    def createDataDict(self):
        self.dataDicts = []
        for item in self.dataStr:
            node = item[0].values()[0]
            self.dataDicts.append(self.getNodeParams(node))

    def getNodeParams(self, node):
        adn = dp.AnalysisNodeData(node, self.sifs)
        adn.performOperations()
        angles = adn.getAngles()
        results = adn.getResults()
        ansol = adn.getAnSol()
        errors = adn.getErrors()[self.opts['errors']]
        return angles, results, ansol, errors

    def createSlices(self):
        self.slices = []
        i = 0
        for k in sorted(self.items.keys()):
            numInt = self.items[k]
            angles = self.dataDicts[i][0]
            sl = self.createSliceIndices(angles, numInt)
            self.slices.append(sl)
            i += 1

    def createSliceIndices(self, vals, numInts):
        intLen = (max(vals) - min(vals)) / float(numInts)
        indices = [[] for i in range(numInts)]
        for x in vals:
            i = int(x / intLen)
            if i < numInts - 1:
                indices[i].append(x)
            else:
                indices[-1].append(x)
        if [] in indices:
            raise ValueError('Try reducing the number of intervals.')
        sliceInd = [[] for i in range(numInts)]
        for i in range(numInts):
            minVal = indices[i][0]
            maxVal = indices[i][-1]
            ind0 = np.where(vals == minVal)[0][0]
            ind1 = np.where(vals == maxVal)[-1][-1] + 1
            sliceInd[i].append(ind0)
            sliceInd[i].append(ind1)
        sliceInd[-1][1] += 1
        return sliceInd

    def createFigure(self):
        self.axes = []
        self.createFigureAxes()
        if self.opts['range']:
            self.createSlices()
            self.plotRangeArea()
        if self.opts['dataPoints']:
            self.createDataPointsPlot()
        if self.opts['analytical']:
            self.createAnSolPlot()
        if self.opts['optSim']:
            self.createOptSimPlot()
        self.setXLim()
        self.createLegend()
        self.setSubplotTitles()
        self.setYlimits()

    def createLegend(self):
        handles = []
        labels = []
        h, l = self.axes[0].get_legend_handles_labels()
        ind = len(self.dataStr) - 1
        self.axes[ind].legend(h, l, bbox_to_anchor=(1, 1.02), loc=2)

    def setXLim(self):
        for n in range(len(self.dataStr)):
            i = self.getItemKey(n)
            for sif in self.sifs:
                ax = self.getAxes(i, sif)
                angles = self.dataDicts[n][0]
                ax.set_xlim((min(angles), max(angles)))

    def createOptSimPlot(self):
        for n in range(len(self.dataDicts)):
            i = self.getItemKey(n)
            ad = dp.AnalysisData(self.dataStr[n][1])
            ad.calcAnSol()
            ad.calculateStats()
            angles = ad.getAngles()
            for sif in self.sifs:
                ax = self.getAxes(i, sif)
                res = ad.getResults()[sif]
                ax.plot(angles, res, 'lime', lw=1,
                        label='optSim')

    def createDataPointsPlot(self):
        for n in range(len(self.dataStr)):
            i = self.getItemKey(n)
            for sif in self.sifs:
                angles = self.dataDicts[n][0]
                ax = self.getAxes(i, sif)
                for dt in self.opts['data']:
                    dInd, color = self.getDataIndAndColor(dt)
                    data = self.dataDicts[n][dInd][sif]
                    alpha = self.calcAlphaValRP(n)
                    ax.plot(angles, data,
                            linestyle='-', marker='.',
                            color=color, alpha=alpha,
                            label=dt)

    def calcAlphaValRP(self, n):
        vals = len(self.dataDicts[n][0])
        if vals > 1000:
            return 0.05
        else:
            return 0.3

    def createAnSolPlot(self):
        for n in range(len(self.items.keys())):
            i = self.getItemKey(n)
            for sif in self.sifs:
                ax = self.getAxes(i, sif)
                angles = self.dataDicts[n][0]
                anSol = self.dataDicts[n][2][sif]
                ax.plot(angles, anSol, 'k', lw=2,
                        label='analytical')

    def getAxes(self, item, sif):
        itemInd = sorted(self.items.keys()).index(item)
        itemLen = len(self.items)
        ax = self.axes[itemLen * self.sifs.index(sif) + itemInd]
        return ax

    def getItemKey(self, n):
        return sorted(self.items.keys())[n]

    def plotRangeArea(self):
        for n in range(len(self.items)):
            i = self.getItemKey(n)
            for sif in self.sifs:
                axes = self.getAxes(i, sif)
                self.plotRangeAreaPerAxes(axes, n, sif)

    def getDataIndAndColor(self, dataType):
        dataInds = {'results': 1, 'errors': 3}
        colors = {'results': 'b', 'errors': 'r'}
        return dataInds[dataType], colors[dataType]

    def createVerts(self, slices, angles, values, func):
        x, y, verts = [], [], []
        valsl = [values[s[0] - 1 if s[0] > 0 else 0:s[1]] for s in slices]
        angsl = [angles[s[0] - 1 if s[0] > 0 else 0:s[1]] for s in slices]
        for a in angsl:
            x.append(a[0])
            x.append(a[-1])
        for v in valsl:
            y.append(func(v))
            y.append(func(v))
        verts = [[xi, yi] for xi, yi in zip(x, y)]
        return verts

    def createVerts2(self, slices, angles, values, func):
        x, y, verts = [], [], []
        valsl = [values[s[0]:s[1]] for s in slices]
        angsl = [angles[s[0]:s[1]] for s in slices]
        for an, va in zip(angsl, valsl):
            y.append(func(va))
            print va, y
            print np.where(va == y[-1])
            ind = np.where(va == y[-1])[0][0]
            x.append(an[ind])
        x.append(angles[-1])
        x.insert(0, angles[0])
        yavg = 0.5 * (y[0] + y[-1])
        y.append(yavg)
        y.insert(0, yavg)
        verts = [[xi, yi] for xi, yi in zip(x, y)]
        return verts

    def plotRangeAreaPerAxes(self, axes, itemInd, sif):
        vertMethods = {1: self.createVerts, 2: self.createVerts2}
        vertFunc = vertMethods[self.opts['rangeType']]
        slices = self.slices[itemInd]
        angles = self.dataDicts[itemInd][0]
        for dt in self.opts['data']:
            dInd, color = self.getDataIndAndColor(dt)
            values = self.dataDicts[itemInd][dInd][sif]
            verts1 = vertFunc(slices, angles, values, min)
            verts2 = vertFunc(slices, angles, values, max)[::-1]
            verts = verts1 + verts2 + [verts2[-1]]
            codes = self.createClosedPathCodes(verts)
            p = Path(verts, codes)
            patch = mpl.patches.PathPatch(
                p,
                facecolor=color,
                edgecolor='none',
                alpha=0.2,
                label=dt +
                ' range')
            axes.add_patch(patch)
            patch = mpl.patches.PathPatch(p, edgecolor=color,
                                          fill=False, lw=0.75, alpha=0.6)
            axes.add_patch(patch)

    def createClosedPathCodes(self, verts):
        codes = [Path.MOVETO]
        for i in range(len(verts) - 2):
            codes.append(Path.LINETO)
        codes.append(Path.CLOSEPOLY)
        return codes


class BoundsCompPlot(SIMCompAnalysis):

    def createBoundsPlot(self, items, targets, fig, tol=0.1, iterLim=100):
        self.items = items
        self.targets = targets
        self.fig = fig
        self.iterLim = iterLim
        self.tol = tol
        self.createDataStr()
        self.createDataDicts()
        self.printStats()
        self.createFigure()

    def createDataStr(self):
        self.dataStr = []
        qdict = self.queue.getQueueDict()
        for i in self.items:
            dd = [{i: qdict[i]}, None, 'angles',
                  self.getSubplotTitle(qdict[i])]
            self.dataStr.append(dd)

    def createDataDicts(self):
        self.dataDicts = []
        for n in range(len(self.items)):
            i = self.items[n]
            log = {s: {t: {'sigma': [], 'pip': []}
                       for t in self.targets.keys()}
                   for s in self.sifs}
            node = self.dataStr[n][0][i]
            adn = dp.AnalysisNodeData(node, self.sifs)
            adn.performOperations()
            sigmaUp = 2 * adn.getAnSolParams()['sigma']
            sigmaLow = 0
            for s in self.sifs:
                for t in self.targets.keys():
                    log[s][t] = self.findSigmaBound(
                        adn, sigmaUp, sigmaLow, s,
                        self.targets[t], log[s][t])
            self.dataDicts.append([adn, log])

    def printStats(self):
        for n in range(len(self.dataStr)):
            i = self.items[n]
            print self.dataStr[n][3]
            log = self.dataDicts[n][1]
            for s in self.sifs:
                sigmas, bounds, its = [], [], []
                for t in log[s].keys():
                    u = log[s][t]
                    sigmas.append(u['sigma'][-1])
                    bounds.append(u['pip'][-1])
                    its.append(len(u['sigma']))
                info = '{0}sigma=[{1:.4}, {2:.4}] | bounds=[{3:.4}%, {4:.4}%] | iterations=[{5}, {6}]'.format(
                    '  {0} '.format(s), sigmas[0], sigmas[1], bounds[0], bounds[1], its[0], its[1])
                print info

    def createFigure(self):
        self.axes = []
        self.createFigureAxes()
        self.createPlot()
        self.setXLimits()
        self.setYlimits()
        self.setSubplotTitles()

    def setXLimits(self):
        for n in range(len(self.dataStr)):
            i = self.items[n]
            adn = self.dataDicts[n][0]
            a = adn.getAngles()
            lims = (min(a), max(a))
            for s in self.sifs:
                ax = self.getAxes(i, s)
                ax.set_xlim(lims)

    def getAxes(self, item, sif):
        itemLen = len(self.items)
        itemInd = self.items.index(item)
        ax = self.axes[itemLen * self.sifs.index(sif) + itemInd]
        return ax

    def getAlphaVal(self, item):
        n = self.items.index(item)
        adn = self.dataDicts[n][0]
        if len(adn.getAngles()) > 1000:
            return 0.1
        else:
            return 1

    def createPlot(self):
        for n in range(len(self.dataStr)):
            i = self.items[n]
            adn = self.dataDicts[n][0]
            logs = self.dataDicts[n][1]
            alpha = self.getAlphaVal(i)
            for s in self.sifs:
                ax = self.getAxes(i, s)
                sigmaUpper = logs[s]['upper']['sigma'][-1]
                sigmaLower = logs[s]['lower']['sigma'][-1]
                ins, outs = self.getInOutPoints(adn,
                                                sigmaLower, sigmaUpper, s)
                ax.plot(ins[0], ins[1], 'b.',
                        label='inside bounds', alpha=alpha)
                ax.plot(outs[0], outs[1], 'r.',
                        label='outside bounds', alpha=alpha)
                angles = adn.getAngles()
                anSol = adn.getAnSol()[s]
                ax.plot(angles, anSol, 'k', lw=1.5,
                        label='analytical')
                lowerBound = adn.calcSIFsForSigmaAndSIF(
                    sigmaLower, s)
                upperBound = adn.calcSIFsForSigmaAndSIF(
                    sigmaUpper, s)
                ax.plot(angles, upperBound, 'lime', lw=1.5,
                        label='bounds')
                ax.plot(angles, lowerBound, 'lime', lw=1.5)

    def findSigmaBound(self, adn, sigmaUp, sigmaLow,
                       sif, target, log):
        sigma = 0.5 * (sigmaUp + sigmaLow)
        pip = self.getPercentPointsInPoly(adn, sigma, sif)
        log['pip'].append(pip)
        log['sigma'].append(sigma)
        if ((pip >= target - self.tol and pip <= target + self.tol) or
                (len(log['sigma']) == self.iterLim)):
            return log
        elif pip < target - self.tol:
            sigmaLow = sigma
            return self.findSigmaBound(adn, sigmaUp, sigmaLow,
                                       sif, target, log)
        elif pip > target + self.tol:
            sigmaUp = sigma
            return self.findSigmaBound(adn, sigmaUp, sigmaLow,
                                       sif, target, log)
        else:
            raise ValueError('unexpected condition reached')

    def getPercentPointsInPoly(self, adn, sigma, sif):
        allnum, numin, numout = self.countPointInOutOfContour(
            adn, sigma, sif)
        assert abs(numin + numout - allnum) < 10e-8
        return float(numin) / float(allnum) * 100

    def countPointInOutOfContour(self, adn, sigma, sif):
        tfl = self.getInOutOfContour(adn, sigma, sif)
        numin = np.sum(tfl)
        allnum = len(tfl)
        numout = allnum - numin
        return allnum, numin, numout

    def getInOutOfContour(self, adn, sigma, sif):
        angles = adn.getAngles()
        results = abs(adn.getResults()[sif])
        points = [[xi, yi] for xi, yi in zip(angles, results)]
        yVals = abs(np.array(adn.calcSIFsForSigmaAndSIF(sigma, sif)))
        return self.getInOutPointsArray(angles, yVals, points)

    def getInOutPointsArray(self, angles, yVals, points):
        path = Path(self.createVertsForPolyPath(angles, yVals))
        return path.contains_points(points, radius=0)

    def getInOutPoints(self, adn, sigmaLow, sigmaUp, sif):
        inoutLow = self.getInOutOfContour(adn, sigmaLow, sif)
        inoutUp = self.getInOutOfContour(adn, sigmaUp, sif)
        angles = adn.getAngles()
        res = adn.getResults()[sif]
        inAngles, inVals = [], []
        outAngles, outVals = [], []
        for i in range(len(inoutUp)):
            if inoutLow[i] or not inoutUp[i]:
                outAngles.append(angles[i])
                outVals.append(res[i])
            else:
                inAngles.append(angles[i])
                inVals.append(res[i])
        return [[inAngles, inVals], [outAngles, outVals]]

    def createVertsForPolyPath(self, x, y):
        verts = [[xi, yi] for xi, yi in zip(x, y)]
        verts.insert(0, [verts[0][0], -10e16])
        verts.append([verts[-1][0], -10e16])
        return verts
