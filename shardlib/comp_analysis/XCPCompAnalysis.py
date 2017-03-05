import matplotlib as mpl
import dbaccess as dba
import dataProcessing as dp
import plotFuncs as pf
from compAnalysisBase import CompAnalysisBase


class XCPCompAnalysis(CompAnalysisBase):

    def __init__(self, node, crackEdge, criteria, sifs, errType='difference'):
        self.aNodes = [node]
        self.ce = crackEdge
        self.crit = criteria
        self.sifs = sifs
        self.errType = errType
        self.dataStr = [
            [{}, None, 'crackEdges', 'Optimal Simulations per crackEdge'],
            [{}, None, 'allEdges',
             'Simulations with crackEdge = {0}'.format(self.ce)]]

    def runMethods(self):
        self.createDataStr()

        self.createSelectionDict()
        self.createDataDict()
        self.createSelectionAxisLabels()

    def createDataStr(self):
        ss = self.aNodes[0].getSuccessfulMembers()
        sf = self.aNodes[0].getFailedMembers()
        sd = pf.createCeAeDataStr(
            ss, self.crit[0], self.crit[1], successful=True)
        fd = pf.createCeAeDataStr(
            sf, self.crit[0], self.crit[1], successful=False)
        self.extractCrackEdges(sd.items())
        self.setOptCeValue(sd.items())
        self.setOptAeValuePerGivenCe(sd.items())
        self.setOptSimIdForEachCe(sd.items())
        self.setSimIdsForTheSelectedCe(list(sd.items()) + list(fd.items()))

    def extractCrackEdges(self, data):
        self.crackEdges = set([])
        for item in data:
            self.crackEdges.add(item[0][0])
        self.crackEdges = sorted(self.crackEdges)
        assert self.ce in self.crackEdges, 'The selected crack edge value {0} must be in the available range of crack edge values {1}'.format(
            self.ce, self.crackEdges)

    def setOptCeValue(self, data):
        val = sorted(data, key=lambda x: abs(x[1][1]))[0][0][0]
        self.dataStr[0][1] = val

    def setOptAeValuePerGivenCe(self, data):
        d = self.filterSimIdsWithCe(data, self.ce)
        val = sorted(d, key=lambda x: abs(x[1][1]))[0][0][1]
        self.dataStr[1][1] = val

    def setOptSimIdForEachCe(self, data):
        for ce in self.crackEdges:
            d = self.filterSimIdsWithCe(data, ce)
            if len(d) > 0:
                d.sort(key=lambda x: abs(x[1][1]))
                key = d[0][0][0]
                val = d[0][1][0]
                self.dataStr[0][0][key] = [val]

    def setSimIdsForTheSelectedCe(self, data):
        d = self.filterSimIdsWithCe(data, self.ce)
        for keyval in d:
            ae = keyval[0][1]
            if keyval[1][1] is not None:
                simId = [keyval[1][0]]
            else:
                simId = []
            self.dataStr[1][0][ae] = simId

    def filterSimIdsWithCe(self, data, ce):
        return [d for d in data if d[0][0] == ce]

    def createSelectionDict(self):
        self.sData = {}
        i = 1
        for key in sorted(self.dataStr[1][0].keys()):
            if self.dataStr[1][0][key]:
                self.sData[i] = self.dataStr[1][0][key][0]
                i += 1

    def createSelectionAxisLabels(self):
        self.selLabels = []
        nonSel = ''
        i = 1
        for k in sorted(self.dataStr[1][0].keys()):
            if self.dataStr[1][0][k]:
                self.selLabels.append(i)
                i += 1
            else:
                self.selLabels.append(nonSel)

# figure
    def createFigure(self, fig):
        CompAnalysisBase.createFigure(self, fig)
        self.addSubplotConnections()
        self.adjustXlabels()
        self.addSelectionAxisToAxes(self.axes[-1], self.selLabels, color='g')

    def getXOptBoxCoord(self, axes, offset):
        i = self.axes.index(axes) % 2
        sif = self.sifs[0]
        bpdata, pos, altpos = self.createBoxPlotData(self.dataDicts[i][sif])
        xs = sorted(pos + altpos)
        if i == 1:
            ind = sorted(self.dataStr[i][0].keys()).index(self.dataStr[i][1])
        else:
            ind = sorted(self.dataStr[0][0].keys()).index(self.ce)
        x = xs[ind] + offset
        xf = self.convDataPointToFigCoord(axes, (x, 0))[0]
        return xf

    def getAxesCoords(self, axes):
        ymin, ymax = axes.get_ylim()
        xmin, xmax = axes.get_xlim()
        llp = self.convDataPointToFigCoord(axes, (xmin, ymin))
        urp = self.convDataPointToFigCoord(axes, (xmax, ymax))
        return llp, urp

    def createSubplotConnectionsCoords(self):
        coords = []
        # grey rectangle coords
        yoffset = self.yoffset
        x0 = self.getXOptBoxCoord(self.axes[-2], -self.xoffset)
        y0 = self.getAxesCoords(self.axes[-2])[0][1] - yoffset
        x1 = self.getAxesCoords(self.axes[-1])[1][0]
        y1 = self.getAxesCoords(self.axes[1])[1][1] + yoffset
        w = x1 - x0
        h = y1 - y0
        r = yoffset
        coords.append([[x0, y0], w, h, r])
        # white rectangle coords
        yoffset = 0.5 * self.yoffset
        x0 = self.getXOptBoxCoord(self.axes[-2], self.xoffset)
        y0 = self.getAxesCoords(self.axes[-2])[0][1] - yoffset
        x1 = self.getAxesCoords(self.axes[-1])[0][0]
        y1 = self.getAxesCoords(self.axes[1])[1][1] + yoffset
        w = x1 - x0
        h = y1 - y0
        r = yoffset
        coords.append(((x0, y0), w, h, r))
        # green rect coords
        yoffset = 0.75 * self.yoffset
        x0 = self.getXOptBoxCoord(self.axes[-2], 0)
        y0 = self.getAxesCoords(self.axes[-2])[0][1] - yoffset
        x1 = self.getXOptBoxCoord(self.axes[-1], 0)
        y1 = self.getAxesCoords(self.axes[1])[1][1] + yoffset
        w = x1 - x0
        h = y1 - y0
        r = yoffset
        coords.append(((x0, y0), w, h, r))
        return coords

    def addSubplotConnections(self):
        patches = []
        self.xoffset = 0.5
        self.yoffset = 0.02
        edgecolor = [0.6 for i in range(3)]
        facecolor = [0.85 for i in range(3)]
        coords = self.createSubplotConnectionsCoords()
        c = coords[0]
        patches.append(
            mpl.patches.FancyBboxPatch(
                xy=c[0],
                width=c[1],
                height=c[2],
                boxstyle='round,pad=0, rounding_size={0}'.format(
                    c[3]),
                facecolor=facecolor,
                edgecolor=edgecolor,
                transform=self.fig.transFigure,
                figure=self.fig,
                zorder=0))
        c = coords[1]
        patches.append(
            mpl.patches.FancyBboxPatch(
                xy=c[0],
                width=c[1],
                height=c[2],
                boxstyle='round,pad=0, rounding_size={0}'.format(
                    c[3]),
                facecolor='w',
                edgecolor=edgecolor,
                transform=self.fig.transFigure,
                figure=self.fig,
                zorder=0))
        c = coords[2]
        patches.append(
            mpl.patches.FancyBboxPatch(
                xy=c[0],
                width=c[1],
                height=c[2],
                boxstyle='round,pad=0, rounding_size={0}'.format(
                    c[3]),
                fill=False,
                edgecolor='lime',
                transform=self.fig.transFigure,
                figure=self.fig,
                zorder=0))
        self.fig.patches.extend(patches)

    def adjustXlabels(self):
        pad = 16
        self.syc = -0.4
        self.axes[-1].tick_params(axis='x', pad=pad)
        self.axes[-2].tick_params(axis='x', pad=pad)
