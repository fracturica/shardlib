import unittest
from mock import Mock, MagicMock, patch, call
from comp_analysis.XCPCompAnalysis import XCPCompAnalysis
from test_treeSetUp import TreeSetUp

classPath = 'comp_analysis.compAnalysisBase.CompAnalysisBase'


class TestXCPCompAnalysis(TreeSetUp):

    def setUp(self):
        TreeSetUp.setUp(self)
        self.sinp = [
            ((0.1, 1), ('simid1', 1.1)), ((0.1, 2), ('simid2', 2.1)),
            ((0.1, 3), ('simid3', -1.1)), ((0.1, 4), ('simid4', 0.11)),
            ((0.2, 5), ('simid5', 4.2)), ((0.2, 6), ('simid6', -6.4)),
            ((0.2, 7), ('simid7', -4.2)), ((0.2, 8), ('simid8', -0.5)),
            ((0.3, 9), ('simid9', 1.5)), ((0.301, 10), ('simid10', -0.1)),
            ((0.3, 11), ('simid11', 2.2)), ((0.3, 12), ('simid12', 20.3))]
        self.finp = [
            ((0.1, 5), ('simid13', None)), ((0.1, 6), ('simid14', None)),
            ((0.3, 1), ('simid15', None)), ((0.4, 1), ('simid16', None)),
            ((0.4, 2), ('simid17', None)), ((0.4, 3), ('simid18', None))]
        self.xca = XCPCompAnalysis(
            node=self.node1XFEMcpLT, crackEdge=0.5,
            criteria=['rmsd', 'K2'], sifs=['K1', 'K2', 'K3'],
            errType='errType')

    def test_XCPCompAnalysis_constructor(self):
        self.assertEqual([self.node1XFEMcpLT], self.xca.aNodes)
        self.assertEqual(0.5, self.xca.ce)
        self.assertEqual(['rmsd', 'K2'], self.xca.crit)
        self.assertEqual(['K1', 'K2', 'K3'], self.xca.sifs)
        self.assertEqual('errType', self.xca.errType)
        expDS = [
                [{}, None, 'crackEdges', 'Optimal Simulations per crackEdge'],
                [{}, None, 'allEdges',
                    'Simulations with crackEdge = 0.5']]
        self.assertEqual(expDS, self.xca.dataStr)

    def test_extractCrackEdges_with_ce_in_crackEdges(self):
        exp = [0.1, 0.2, 0.3, 0.301]
        self.xca.ce = 0.2
        self.xca.extractCrackEdges(self.sinp)
        self.assertEqual(exp, self.xca.crackEdges)

    def test_extractCrackEdges_with_ce_not_in_crackEdges(self):
        self.xca.ce = 0.9
        self.assertRaises(
            AssertionError,
            self.xca.extractCrackEdges,
            self.sinp)

    def test_setOptCeValue(self):
        self.xca.setOptCeValue(self.sinp)
        exp = 0.301
        self.assertEqual(exp, self.xca.dataStr[0][1])
        self.assertEqual({}, self.xca.dataStr[0][0])
        self.assertEqual({}, self.xca.dataStr[1][0])
        self.assertIsNone(self.xca.dataStr[1][1])

    def test_setOptAeValuePerGivenCe_with_crackEdge_01(self):
        self.xca.ce = 0.1
        self.xca.setOptAeValuePerGivenCe(self.sinp)
        exp = 4
        self.assertEqual(exp, self.xca.dataStr[1][1])
        self.assertEqual({}, self.xca.dataStr[0][0])
        self.assertEqual({}, self.xca.dataStr[1][0])
        self.assertIsNone(self.xca.dataStr[0][1])

    def test_setOptAeValuePerGivenCe_with_crackEdge_02(self):
        self.xca.ce = 0.2
        self.xca.setOptAeValuePerGivenCe(self.sinp)
        exp = 8
        self.assertEqual(exp, self.xca.dataStr[1][1])

    def test_filterSimIdsWithCe_with_01_ce_successful_simIds(self):
        exp = self.sinp[0:4]
        self.assertEqual(exp, self.xca.filterSimIdsWithCe(self.sinp, 0.1))

    def test_filterSimIdsWithCe_with_01_ce_successful_and_failed_simIds(self):
        exp = self.sinp[0:4] + self.finp[0:2]
        self.assertEqual(
            exp, self.xca.filterSimIdsWithCe(
                self.sinp + self.finp, 0.1))

    def test_filterSimIdsWithCe_with_nonexisting_ce(self):
        self.assertEqual([], self.xca.filterSimIdsWithCe(self.sinp, 0.9))

    def test_setOptSimIdForEachCe(self):
        self.xca.crackEdges = [0.1, 0.2, 0.3, 0.301, 0.4]
        exp = {
            0.1: ['simid4'],
            0.2: ['simid8'],
            0.3: ['simid9'],
            0.301: ['simid10']}
        self.xca.setOptSimIdForEachCe(self.sinp)
        self.assertEqual(exp, self.xca.dataStr[0][0])
        self.assertEqual({}, self.xca.dataStr[1][0])
        self.assertIsNone(self.xca.dataStr[0][1])
        self.assertIsNone(self.xca.dataStr[1][1])

    def test_setSimIdsForTheSelectedCe_with_01_ce(self):
        self.xca.ce = 0.1
        exp = {1: ['simid1'], 2: ['simid2'], 3: ['simid3'],
               4: ['simid4'], 5: [], 6: []}
        self.xca.setSimIdsForTheSelectedCe(self.sinp + self.finp)
        self.assertEqual(exp, self.xca.dataStr[1][0])
        self.assertEqual({}, self.xca.dataStr[0][0])
        self.assertIsNone(self.xca.dataStr[0][1])
        self.assertIsNone(self.xca.dataStr[1][1])

    def test_setSimIdsForTheSelectedCe_with_03_ce(self):
        self.xca.ce = 0.3
        exp = {9: ['simid9'], 11: ['simid11'], 12: ['simid12'], 1: []}
        self.xca.setSimIdsForTheSelectedCe(self.sinp + self.finp)
        self.assertEqual(exp, self.xca.dataStr[1][0])
        self.assertEqual({}, self.xca.dataStr[0][0])
        self.assertIsNone(self.xca.dataStr[0][1])
        self.assertIsNone(self.xca.dataStr[1][1])

    def test_createSelectionDict(self):
        self.xca.dataStr[1][0] = {1.1: ['simid1'], 2.1: ['simid2'],
                                  3.1: ['simid3'], 4.1: ['simid4'], 5.1: []}
        exp = {1: 'simid1', 2: 'simid2', 3: 'simid3', 4: 'simid4'}
        self.xca.createSelectionDict()
        self.assertEqual(exp, self.xca.sData)

    def test_createSelectionAxisLabels(self):
        self.xca.dataStr[1][0] = {
            1.1: ['simid1'],
            2.1: [],
            3.1: ['simid3'],
            4.1: ['simid4'],
            5.1: [],
            6.1: ['simid6'],
            7.1: []}
        exp = [1, '', 2, 3, '', 4, '']
        self.xca.createSelectionAxisLabels()
        self.assertEqual(exp, self.xca.selLabels)
