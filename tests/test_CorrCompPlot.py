import unittest
from mock import Mock, MagicMock, patch, call
from comp_analysis.SIMCompAnalysis import CorrCompPlot
from test_SIMCompAnalysis import SIMCompAnalysisSetUp

modulePath = 'comp_analysis.SIMCompAnalysis'


class TestCorrCompPlot(SIMCompAnalysisSetUp):

    def setUp(self):
        SIMCompAnalysisSetUp.setUp(self)
        self.ccp = CorrCompPlot(self.lq, ['rmsd', 'K1'], ['K1', 'K2', 'K3'])
        self.dataX = {
            'K1': {1: [1, 2, 0, -3, 4], 2: [0, 5, -7], 3: [0, 4, -3], 4: [-9, 0, 7]},
            'K2': {1: [4, 9, -2, 2.5, 1], 2: [6, 8, -2], 3: [-1, 1, 2], 4: [1, 2, 0]},
            'K3': {1: [1, 2, -1, 0, 1], 2: [1, -2, 3], 3: [1, -2, 1], 4: [-3, 2, 1]}}
        self.dataY = {
            'K1': {1: [2, 3, 1, 8, 4], 2: [4, 5, 3], 3: [1, 2, 5], 4: [9, 5, 3]},
            'K2': {1: [7, 6, 4, 3, 5], 2: [8, 5, 9], 3: [0, 0, 2], 4: [8, 6, 2]},
            'K3': {1: [4, 5, 6, 7, 8], 2: [3, 4, 3], 3: [0, -1, 4], 4: [-1, 5, 1]}}
        self.dataDicts = [[self.dataX, self.dataY]]

    def test_createDataDict(self):
        def mockSF(node):
            data = {
                1: [{'K1': 111, 'K2': 112, 'K3': 113}, {'K1': 121, 'K2': 122, 'K3': 123}],
                2: [{'K1': 211, 'K2': 212, 'K3': 213}, {'K1': 221, 'K2': 222, 'K3': 223}],
                3: [{'K1': 311, 'K2': 312, 'K3': 313}, {'K1': 321, 'K2': 322, 'K3': 323}],
                4: [{'K1': 411, 'K2': 412, 'K3': 413}, {'K1': 421, 'K2': 422, 'K3': 423}]}
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
        npMock = MagicMock(side_effect=mockSF)
        self.ccp.items = [1, 3, 4]
        self.ccp.dataStr = [[{
            1: self.node1FEMeQF, 3: self.node1FEMsQR,
            4: self.node1XFEMcpLT}]]
        with patch(modulePath + '.CorrCompPlot.getNodeParams', npMock):
            self.ccp.createDataDict()
        exp = [[{
            'K1': {1: 111, 3: 311, 4: 411}, 'K2': {1: 112, 3: 312, 4: 412},
            'K3': {1: 113, 3: 313, 4: 413}}, {
            'K1': {1: 121, 3: 321, 4: 421}, 'K2': {1: 122, 3: 322, 4: 422},
            'K3': {1: 123, 3: 323, 4: 423}}]]
        self.assertEqual(exp, self.ccp.dataDicts)

    def test_getReferenceXYVals_with_quantity_results(self):
        self.ccp.qt = 'results'
        self.ccp.items = [1, 3, 4]
        self.ccp.dataDicts = self.dataDicts
        x, y = self.ccp.getReferenceXYVals()
        self.assertEqual(x, y)
        exp = {'K1': [-9, 7], 'K2': [-2, 9], 'K3': [-3, 2]}
        self.assertEqual(exp, x)

    def test_getReferenceXYVals_with_quantity_difference(self):
        self.ccp.qt = 'difference'
        self.ccp.items = [1, 3, 4]
        self.ccp.dataDicts = self.dataDicts
        x, y = self.ccp.getReferenceXYVals()
        expY = {'K1': [0, 0], 'K2': [0, 0], 'K3': [0, 0]}
        self.assertEqual(expY, y)
        expX = {'K1': [0, 7], 'K2': [0, 9], 'K3': [0, 2]}
        self.assertEqual(expX, x)

    def test_getXYVals_with_quantity_results(self):
        self.ccp.dataDicts = self.dataDicts
        self.ccp.qt = 'results'
        x, y = self.ccp.getXYVals('K1', 2)
        expX = self.dataX['K1'][2]
        self.assertEqual(expX, x)
        expY = self.dataY['K1'][2]
        self.assertEqual(expY, y)

    def test_getXYVals_with_quantity_difference(self):
        self.ccp.dataDicts = self.dataDicts
        self.ccp.qt = 'difference'
        x, y = self.ccp.getXYVals('K2', 2)
        expX = [6, 8, 2]
        self.assertEqual(expX, list(x))
        expY = [8, 5, 9]
        self.assertEqual(expY, y)
