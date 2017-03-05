import unittest
from mock import Mock, MagicMock, patch, call
from comp_analysis.SIMCompAnalysis import HistCompPlot
from test_SIMCompAnalysis import SIMCompAnalysisSetUp

modulePath = 'comp_analysis.SIMCompAnalysis'


class TestHistCompPlot(SIMCompAnalysisSetUp):

    def setUp(self):
        SIMCompAnalysisSetUp.setUp(self)
        self.hcp = HistCompPlot(self.lq, ['rmsd', 'K1'], ['K1', 'K2', 'K3'])

    def test_createDataStr(self):
        inMock = MagicMock(return_value={'itemNo': 'node'})
        self.hcp.errType = 'diff'
        self.hcp.items = {1: 10, 2: 20, 3: 30}
        with patch(modulePath + '.SIMCompAnalysis.getItemNodeDict', inMock):
            self.hcp.createDataStr()
        exp = [[{'itemNo': 'node'}, None, 'errors "diff"', 'hist']]
        self.assertEqual(exp, self.hcp.dataStr)
        inMock.assert_called_once_with([1, 2, 3], self.lq)

    def test_createDataDict(self):
        def eMockSF(node):
            data = {
                1: {'K1': 11, 'K2': 12, 'K3': 13},
                2: {'K1': 21, 'K2': 22, 'K3': 23},
                3: {'K1': 31, 'K2': 32, 'K3': 33},
                4: {'K1': 41, 'K2': 42, 'K3': 43}}
            if node is self.node1FEMeQF:
                return data[1]
            elif node is self.node1FEMsLR:
                return data[2]
            elif node is self.node1FEMsQR:
                return data[3]
            elif node is self.node1XFEMcpLT:
                return data[4]
            else:
                raise KeyError
        eMock = MagicMock(side_effect=eMockSF)
        self.hcp.items = {1: 11, 2: 22, 4: 44}
        self.hcp.dataStr = [[{
            1: self.node1FEMeQF, 2: self.node1FEMsLR,
            4: self.node1XFEMcpLT}]]
        with patch(modulePath + '.HistCompPlot.getNodeErrors', eMock):
            self.hcp.createDataDict()
        exp = [{
            'K1': {1: 11, 2: 21, 4: 41}, 'K2': {1: 12, 2: 22, 4: 42},
            'K3': {1: 13, 2: 23, 4: 43}}]
        self.assertEqual(exp, self.hcp.dataDicts)
