import matplotlib as mpl
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import dataProcessing as dp
import plotFuncs as pf
import sessionFuncs as sf
from types import *
import copy


class CompAnalysisBase(object):

    def __init__(
            self,
            pNode,
            analysisBranches,
            criteria,
            sifs,
            errType='difference'):
        self.pNode = pNode
        self.crit = criteria
        self.sifs = sifs
        self.analysisBranches = analysisBranches
        self.errType = errType

    def runMethods(self):
        self.setAnalysisNodes()
        self.createDataStr()
        self.createSelectionDict()
        self.createDataDict()

    def setAnalysisNodes(self):
        self.aNodes = []
        for a in self.analysisBranches:
            if isinstance(a, (list, tuple)):
                self.aNodes.append(self.pNode.getTreeBranch(a))
            elif isinstance(a, (NoneType,)):
                pass
            else:
                raise KeyError(
                    'Invalid value for the analysisBranches argument')

    def getSubplotTitle(self, node, depth=3):
        title = []
        n = copy.copy(node)
        if node.getNodeLevelInTree() < depth:
            raise IndexError(
                'Node level in tree is lower than the depth value.\
                            Try lower depth value.')
        else:
            for i in range(depth):
                title.append(n.getName())
                n = n.getParent()
            return ' '.join(title[::-1])

    def createDataStr(self):
        self.dataStr = []
        self.count = 0
        for node in self.aNodes:
            self.createDataStrEntry(node)

    def getOptSimKey(self, dataDict, simIds):
        optSim = [pf.getSimIdsWithLowestErrorPerDH(
            simIds, self.crit[0], self.crit[1]).values()[0][0]]
        optSimKey = [key for key in dataDict.keys() if dataDict[
            key] == optSim][0]
        return optSimKey

    def createSelectionDict(self):
        self.sData = []
        for dd in self.dataStr:
            self.sData = self.sData + dd[0].items()
        self.sData = dict(self.sData)

    def createDataDict(self):
        self.dataDicts = []
        for entry in self.dataStr:
            data = self.createDataDictEntry(entry[0])
            self.dataDicts.append(data)

    def createDataDictEntry(self, dataStrEntry):
        data = {s: {} for s in self.sifs}
        for key in dataStrEntry.keys():
            errs = self.getSimIdErrors(dataStrEntry[key])
            for sif in self.sifs:
                data[sif][key] = errs[sif]
        return data

    def getSimIdErrors(self, simKey):
        if simKey == []:
            return {s: [] for s in self.sifs}
        elif isinstance(simKey, list) and len(simKey) == 1:
            ad = dp.AnalysisData(simKey[0])
            ad.calcAnSol()
            ad.calculateStats()
            errs = ad. getErrorReports()[self.errType]
            return {sif: errs[sif] for sif in self.sifs}

# figure
    def createFigure(self, fig):
        self.syc = -0.33
        self.fig = fig
        self.axes = []
        self.createFigureAxes()
        i = 0
        for sif in self.sifs:
            for dDict, dStr in zip(self.dataDicts, self.dataStr):
                self.createSubplotBoxplot(
                    self.axes[i], dDict, sif)
                optBox = self.markOptSim(self.axes[i], dStr, dDict, sif)
                errBox = self.markFailedSim(self.axes[i], dDict, sif)
                i += 1
        self.markBoxes = [optBox, errBox]
        self.createLegend()
        self.setYlimits()
        self.setSubplotTitles()
        self.setXlabels()

    def createFigureAxes(self):
        lboxcols = len(self.dataStr[0][0].keys())
        rboxcols = (len(self.dataStr[1][0].keys())
                    if len(self.dataStr) == 2 else 0)
        ncols = len(self.dataStr)
        nrows = len(self.sifs)
        if lboxcols == 0 or rboxcols == 0:
            width_ratios = None
        else:
            width_ratios = [lboxcols, rboxcols]
        gs = mpl.gridspec.GridSpec(
            nrows=nrows, ncols=ncols,
            width_ratios=width_ratios)
        gs.update(wspace=0.04, hspace=0.08)
        for i in range(nrows * ncols):
            self.axes.append(self.fig.add_subplot(gs[i]))
            self.axes[i].grid(True)
            if i % 2 == 1 and ncols == 2:
                self.axes[i].set_yticklabels([])

    def createSubplotBoxplot(self, axis, dataDict, sif):
        bpdata, pos, altpos = self.createBoxPlotData(dataDict[sif])
        axis.boxplot(bpdata, widths=0.8, positions=pos)
        axis.set_xlim(-0.5, len(pos + altpos) - 0.5)
        axis.set_xticks(range(len(pos + altpos)))
        axis.set_xticklabels(sorted(dataDict[sif].keys()))

    def createBoxPlotData(self, dataDict):
        data, pos, altpos = [], [], []
        count = 0
        for k in sorted(dataDict.keys()):
            if dataDict[k] != []:
                pos.append(count)
                data.append(dataDict[k])
            else:
                altpos.append(count)
            count += 1
        return data, pos, altpos

    def markOptSim(self, axes, dStr, dDict, sif):
        optSimKey = dStr[1]
        ob = None
        bpdata, pos, altpos = self.createBoxPlotData(dDict[sif])
        pos = sorted(pos + altpos)
        i = sorted(dDict[sif].keys()).index(optSimKey)
        ob = axes.axvspan(pos[i] - 0.45, pos[i] + 0.45, color='DarkGreen',
                          ec='lime', alpha=0.2)
        return ob

    def markFailedSim(self, axes, dDict, sif):
        eb = None
        bpdata, pos, altpos = self.createBoxPlotData(dDict[sif])
        for p in altpos:
            eb = axes.axvspan(p - 0.45, p + 0.45, color='DarkRed',
                              ec='red', alpha=0.2)
        return eb

    def createLegend(self):
        i = len(self.dataStr) - 1
        text = [
            'optimal simulation',
            'failed simulation',
            'optSim for rightplot']
        labels, handles = [], []
        for i in range(len(self.markBoxes)):
            if self.markBoxes[i] is not None:
                labels.append(text[i])
                handles.append(self.markBoxes[i])
        if handles:
            self.axes[i].legend(handles, labels, bbox_to_anchor=(1.02, 1),
                                loc=2, borderaxespad=0)

    def setXlabels(self):
        for i in range(len(self.dataStr)):
            self.axes[-1 - i].set_xlabel(self.dataStr[::-1][i][2])

    def setYlimits(self):
        if len(self.dataStr) == 2:
            for i in range(0, len(self.axes), 2):
                ylims = list(self.axes[i].get_ylim()) + \
                    list(self.axes[i + 1].get_ylim())
                self.axes[i].set_ylim(min(ylims), max(ylims))
                self.axes[i + 1].set_ylim(min(ylims), max(ylims))

    def setSubplotTitles(self):
        for i in range(len(self.dataStr)):
            title = self.dataStr[i][3]
            self.axes[i].text(0.5, 1.1, title,
                              horizontalalignment='center',
                              fontsize=12,
                              transform=self.axes[i].transAxes)

    def addSelectionAxisToAxes(self, axes, labels, color='g'):
        labels = [0] + labels
        tax = axes.twiny()
        tax.set_xlim(axes.get_xlim())
        tax.spines['top'].set_position(('axes', self.syc))
        tax.set_xlabel('Selection ID Number')
        tax.xaxis.set_major_locator(MultipleLocator(1))
        tax.xaxis.set_tick_params(direction='out')
        tax.xaxis.label.set_color(color)
        tax.tick_params(axis='x', colors=color)
        tax.set_xticklabels(labels)
        x1 = axes.get_xlim()[0] + 0.5
        x2 = axes.get_xlim()[1] - 0.5
        x1 = self.convDataPointToAxesCoord(tax, (x1, 0))[0]
        x2 = self.convDataPointToAxesCoord(tax, (x2, 0))[0]
        l = mpl.lines.Line2D([x1, x2], [self.syc, self.syc],
                             transform=tax.transAxes, axes=tax, color=color,
                             visible=True, zorder=3, clip_on=False)
        tax.add_line(l)

    def convDataPointToAxesCoord(self, axis, point):
        """
        Converts data point coordinates to axes coordinates
        """
        x_d, y_d = axis.transData.transform(point)
        xy = axis.transAxes.inverted().transform((x_d, y_d))
        return xy

    def convDataPointToFigCoord(self, axis, point):
        x_d, y_d = axis.transData.transform(point)
        xy = self.fig.transFigure.inverted().transform((x_d, y_d))
        return xy

    def addToQueue(self, cq, selIdNum):
        if isinstance(selIdNum, (NoneType,)):
            pass
        elif selIdNum in self.sData.keys():
            simId = self.sData[selIdNum]
            cq.addSimId(simId)
        else:
            print 'Verify the selIdNum argument value'


# assignment
    def assignSimIdAsFailed(self, trees, cq, selIdNum):
        if isinstance(selIdNum, (NoneType,)):
            pass
        elif selIdNum in self.sData.keys():
            simId = self.sData[selIdNum]
            cq.removeSimIdFromQueue(simId)
            sf.writeToShelve(simId, 'failed')
            sf.setSimIdAsFailed(trees, [simId])
            del self.sData[selIdNum]
            print simId, 'simId'
        else:
            print 'Verify the selIdNum argument value and try again'
