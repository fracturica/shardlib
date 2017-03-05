import unittest
from mock import Mock, MagicMock, call, patch
from comp_analysis.FEMCompAnalysis import FEMCompAnalysis
from test_treeSetUp import TreeSetUp


class TestFEMCompAnalysis(TreeSetUp):

    def setUp(self):
        TreeSetUp.setUp(self)
        self.fca = FEMCompAnalysis(
            pNode=self.node1FEM,
            analysisBranches=[
                ['1.0', 'FEM', 'scale', 'QR'],
                ['1.0', 'FEM', 'elliptic', 'QF']],
            criteria=['rmsd', 'K1'], sifs=['K1', 'K2', 'K3'])
        self.dataStr = [[{1: ['node1FEMsQR_sm_1'],
                          2:['node1FEMsQR_sm_2']},
                         2,
                         'Selection ID Number',
                         'FEM scale QR'],
                        [{3: ['node1FEMeQF_sm_1']},
                         3,
                         'Selection ID Number',
                         'FEM elliptic QF']]

    def test_createDataStrEntry(self):
        def oskMockSF(dd, ss):
            ss1 = set(['node1FEMsQR_sm_1', 'node1FEMsQR_sm_2'])
            ss2 = set(['node1FEMeQF_sm_1'])
            if set(ss) == ss1:
                return 2
            elif set(ss) == ss2:
                return 3
            else:
                print ss
                raise KeyError
        oskMock = MagicMock(side_effect=oskMockSF)
        with patch(
                'comp_analysis.compAnalysisBase.CompAnalysisBase.getOptSimKey',
                oskMock):
            self.fca.dataStr = []
            self.fca.count = 0
            self.fca.createDataStrEntry(self.node1FEMsQR)
            self.assertEqual([self.dataStr[0]], self.fca.dataStr)
            self.fca.createDataStrEntry(self.node1FEMeQF)
            self.assertEqual(self.dataStr, self.fca.dataStr)

    def test_createSelectionDict(self):
        self.fca.dataStr = self.dataStr
        self.fca.createSelectionDict()
        exp = {
            1: 'node1FEMsQR_sm_1',
            2: 'node1FEMsQR_sm_2',
            3: 'node1FEMeQF_sm_1'}
        self.assertEqual(exp, self.fca.sData)
