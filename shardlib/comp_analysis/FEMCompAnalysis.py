from compAnalysisBase import CompAnalysisBase


class FEMCompAnalysis(CompAnalysisBase):

    def createDataStrEntry(self, node):
        ss = sorted(node.getSuccessfulMembers())
        dd = dict([(i + self.count + 1, [ss[i]]) for i in range(len(ss))])
        self.count += len(ss)
        optSimKey = self.getOptSimKey(dd, ss)
        data = [
            dd,
            optSimKey,
            'Selection ID Number',
            self.getSubplotTitle(node)]
        self.dataStr.append(data)

    def createFigure(self, fig):
        CompAnalysisBase.createFigure(self, fig)
        self.setXAxisColor()

    def createSelectionDict(self):
        self.sData = {}
        for dd in self.dataStr:
            for k in sorted(dd[0].keys()):
                self.sData[k] = dd[0][k][0]

    def setXAxisColor(self, color='g'):
        for i in range(len(self.dataStr)):
            self.axes[-1 - i].xaxis.label.set_color(color)
            self.axes[-1 - i].spines['bottom'].set_color(color)
            self.axes[-1 - i].tick_params(axis='x', colors=color)
