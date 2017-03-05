import unittest
from mock import Mock, MagicMock, patch, call
from comp_analysis.SIMCompAnalysis import BoxCompPlot
from test_SIMCompAnalysis import SIMCompAnalysisSetUp


class TestBoxCompPlot(SIMCompAnalysisSetUp):

    def setUp(self):
        SIMCompAnalysisSetUp.setUp(self)
        self.bcp = BoxCompPlot(self.lq, ['rmsd', 'K1'], ['K1', 'K2', 'K3'])

    def test_createDataDictAndEstBoxPlot(self):
        self.bcp.items = [1, 3, 4]
        self.bcp.errType = 'diff'

        def eMockSF(node):
            data = {
                1: [{'K1': 121, 'K2': 122, 'K3': 123}, {'K1': 111, 'K2': 112}],
                2: [{'K1': 221, 'K2': 222, 'K3': 223}, {'K1': 211, 'K2': 212}],
                3: [{'K1': 321, 'K2': 322, 'K3': 323}, {'K1': 311, 'K2': 312}],
                4: [{'K1': 421, 'K2': 422, 'K3': 423}, {'K1': 411, 'K2': 412}]}
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
        with patch('comp_analysis.SIMCompAnalysis.BoxCompPlot.getNodeErrsEst', eMock):
            self.bcp.createDataDictAndEstBoxPlot()
        expDataDicts = [{
            'K1': {1: 121, 3: 321, 4: 421},
            'K2': {1: 122, 3: 322, 4: 422},
            'K3': {1: 123, 3: 323, 4: 423}}]
        expEst = {1: 111, 3: 311, 4: 411}
        self.assertEqual(expDataDicts, self.bcp.dataDicts)
        self.assertEqual(expEst, self.bcp.est)

    def test_getLeavesOptKey_with_nonzero_estimates(self):
        self.bcp.est = {1: -10, 2: 1, 3: -2, 4: -0.5}
        self.assertEqual(4, self.bcp.getLeavesOptKey())

    def test_getLeavesOptKey_with_zero_estimate_value(self):
        self.bcp.est = {1: -2, 3: 0, 4: 2}
        self.assertEqual(3, self.bcp.getLeavesOptKey())

    def test_createDataStrBoxPlot(self):
        self.bcp.est = {1: -2, 3: 1, 4: 0.5}
        self.bcp.items = [1, 3, 4]
        exp = [[
            {1: self.node1FEMeQF, 3: self.node1FEMsQR, 4: self.node1XFEMcpLT},
            4, 'Number in Queue', '']]
        self.bcp.createDataStrBoxPlot()
        self.assertEqual(exp, self.bcp.dataStr)
