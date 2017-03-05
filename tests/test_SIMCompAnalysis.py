import unittest
from mock import Mock, MagicMock, patch, call
from comp_analysis.SIMCompAnalysis import SIMCompAnalysis
from queues import LeavesQueue
from trees import TreeNode
from test_treeSetUp import TreeSetUp


class SIMCompAnalysisSetUp(TreeSetUp):

    def setUp(self):
        TreeSetUp.setUp(self)
        self.lq = LeavesQueue()
        self.lq.addLeaf(self.node1FEMsQR)
        self.lq.addLeaf(self.node1FEMeQF)
        self.lq.addLeaf(self.node1FEMsLR)
        self.lq.addLeaf(self.node1XFEMcpLT)
        self.lq.initNamesLen()


class TestSIMCompAnalysisSetUp(SIMCompAnalysisSetUp):

    def test_setUp(self):
        self.assertEqual({1: self.node1FEMeQF,
                          2: self.node1FEMsLR,
                          3: self.node1FEMsQR,
                          4: self.node1XFEMcpLT},
                         self.lq.getQueueDict())


class TestSIMCompAnalysis(SIMCompAnalysisSetUp):

    def setUp(self):
        SIMCompAnalysisSetUp.setUp(self)
        self.simca = SIMCompAnalysis(
            self.lq, [
                'rmsd', 'K1'], [
                'K1', 'K2', 'K3'])

    def test_constructor(self):
        self.assertIs(self.lq, self.simca.queue)
        self.assertEqual(['rmsd', 'K1'], self.simca.crit)
        self.assertEqual(['K1', 'K2', 'K3'], self.simca.sifs)

    def test_getItemNodeDict(self):
        items = [1, 3, 4]
        exp = {1: self.node1FEMeQF, 3: self.node1FEMsQR, 4: self.node1XFEMcpLT}
        self.assertEqual(exp, self.simca.getItemNodeDict(items, self.lq))
