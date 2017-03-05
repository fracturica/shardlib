import unittest
from mock import Mock, MagicMock, patch, call
from comp_analysis.XSCompAnalysis import XSCompAnalysis
from test_treeSetUp import TreeSetUp


class TestXSCompAnalysis(TreeSetUp):

    def setUp(self):
        TreeSetUp.setUp(self)
        self.xsc = XSCompAnalysis(self.node1FEM,
                                  [['1.0', 'XFEM', 'cp', 'LT'], ['1.0', 'XFEM', 'mp', 'LR']],
                                  ['rmsd', 'K1'], ['K1', 'K2', 'K3'])
        self.dataStr = [[{111: ['node1XFEMcpLT_sm_1'],
                          211:['node1XFEMcpLT_sm_2'],
                          311:['node1XFEMcpLT_sm_3'],
                          121:[]},
                         111,
                         'allEdges',
                         'XFEM cp LT'],
                        [{131: ['node1XFEMmpLR_sm_1'],
                          231:['node1XFEMmpLR_sm_2'],
                            141:[]},
                         131,
                         'allEdges',
                         'XFEM mp LR']]

    def test_createDataStrEntry(self):
        def mMockSF(simId):
            data = {'node1XFEMcpLT_sm_1': {'allEdges': 111, 'other': 112},
                    'node1XFEMcpLT_sm_2': {'allEdges': 211, 'other': 212},
                    'node1XFEMcpLT_sm_3': {'allEdges': 311, 'other': 312},
                    'node1XFEMcpLT_fm_1': {'allEdges': 121, 'other': 122},
                    'node1XFEMmpLR_sm_1': {'allEdges': 131, 'other': 132},
                    'node1XFEMmpLR_sm_2': {'allEdges': 231, 'other': 232},
                    'node1XFEMmpLR_fm_1': {'allEdges': 141, 'other': 142}}
            return data[simId]

        def oskMockSF(dd, ss):
            ss1 = set(['node1XFEMcpLT_sm_1',
                       'node1XFEMcpLT_sm_2',
                       'node1XFEMcpLT_sm_3'])
            ss2 = set(['node1XFEMmpLR_sm_1', 'node1XFEMmpLR_sm_2'])
            if ss == ss1:
                return 111
            elif ss == ss2:
                return 131
            else:
                raise KeyError
        mMock = MagicMock(side_effect=mMockSF)
        oskMock = MagicMock(side_effect=oskMockSF)
        with patch('dataProcessing.getMeshParams', mMock):
            with patch('comp_analysis.compAnalysisBase.CompAnalysisBase.getOptSimKey', oskMock):
                self.xsc.dataStr = []
                self.xsc.createDataStrEntry(self.node1XFEMcpLT)
                self.assertEqual([self.dataStr[0]], self.xsc.dataStr)
                self.xsc.createDataStrEntry(self.node1XFEMmpLR)
                self.assertEqual(self.dataStr, self.xsc.dataStr)

    def test_createSelectionDict(self):
        self.xsc.dataStr = self.dataStr
        self.xsc.createSelectionDict()
        exp = {
            1: 'node1XFEMcpLT_sm_1', 2: 'node1XFEMcpLT_sm_2',
            3: 'node1XFEMcpLT_sm_3', 4: 'node1XFEMmpLR_sm_1',
            5: 'node1XFEMmpLR_sm_2'}
        self.assertEqual(exp, self.xsc.sData)

    def test_createSelectionAxisLabels(self):
        self.xsc.dataStr = self.dataStr
        self.xsc.createSelectionAxisLabels()
        exp = [[1, '', 2, 3], [4, '', 5]]
        self.assertEqual(exp, self.xsc.selLabels)
