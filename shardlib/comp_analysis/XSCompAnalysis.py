import dataProcessing as dp
import plotFuncs as pf
from compAnalysisBase import CompAnalysisBase


class XSCompAnalysis(CompAnalysisBase):

    def runMethods(self):
        CompAnalysisBase.runMethods(self)
        self.createSelectionAxisLabels()

    def createDataStrEntry(self, node):
        ss = node.getSuccessfulMembers()
        sf = node.getFailedMembers()
        dd = dict([(dp.getMeshParams(sim)['allEdges'], [sim]) for sim in ss] +
                  [(dp.getMeshParams(sim)['allEdges'], []) for sim in sf])
        optSimKey = self.getOptSimKey(dd, ss)
        data = [dd, optSimKey, 'allEdges', self.getSubplotTitle(node)]
        self.dataStr.append(data)

    def createSelectionDict(self):
        self.sData = {}
        i = 1
        for dd in self.dataStr:
            for k in sorted(dd[0].keys()):
                if dd[0][k]:
                    self.sData[i] = dd[0][k][0]
                    i += 1

    def createSelectionAxisLabels(self):
        nonSel = ''
        self.selLabels = []
        i = 1
        for n in range(len(self.dataStr)):
            self.selLabels.append([])
            dd = self.dataStr[n][0]
            for k in sorted(dd.keys()):
                if dd[k]:
                    self.selLabels[n].append(i)
                    i += 1
                else:
                    self.selLabels[n].append(nonSel)

    def createFigure(self, fig):
        CompAnalysisBase.createFigure(self, fig)
        for i in range(len(self.dataStr)):
            self.addSelectionAxisToAxes(
                self.axes[-1 - i], self.selLabels[::-1][i], color='g')
