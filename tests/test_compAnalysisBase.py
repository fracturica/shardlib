import unittest
from mock import Mock, MagicMock, patch, call
from comp_analysis.compAnalysisBase import CompAnalysisBase
from test_treeSetUp import TreeSetUp

classPath = 'comp_analysis.compAnalysisBase.CompAnalysisBase'


class TestCompAnalysisBase(TreeSetUp):

    def setUp(self):
        TreeSetUp.setUp(self)
        self.cab = CompAnalysisBase(
            pNode=self.node1FEM,
            analysisBranches=[['elliptic', 'QF']],
            criteria=['areas', 'K3'],
            sifs=['K1', 'K2'], errType='rmsd')

    def test_CompAnalysisBase_constructor(self):
        rMock = MagicMock()
        with patch(classPath + '.runMethods', rMock):
            cab = CompAnalysisBase(pNode=self.node1FEM,
                                   analysisBranches=[
                                       ['scale', 'QR'], ['elliptic', 'QF']],
                                   criteria=['areas', 'K3'],
                                   sifs=['K1', 'K2'], errType='rmsd')
        # rMock.assert_called_once_with_with()
        self.assertIs(self.node1FEM, cab.pNode)
        self.assertEqual(['areas', 'K3'], cab.crit)
        self.assertEqual(
            [['scale', 'QR'], ['elliptic', 'QF']],
            cab.analysisBranches)
        self.assertEqual('rmsd', cab.errType)

    def test_setAnalysisNodes_with_two_lists_defining_unique_paths(self):
        cab = CompAnalysisBase(pNode=self.node1FEM,
                               analysisBranches=[
                                   ['1.0', 'FEM', 'scale', 'QR'],
                                   ['1.0', 'FEM', 'elliptic', 'QF']],
                               criteria=['areas', 'K3'],
                               sifs=['K1', 'K2'], errType='rmsd')
        cab.setAnalysisNodes()
        self.assertEqual(
            set([self.node1FEMsQR, self.node1FEMeQF]),
            set(cab.aNodes))

    def test_setAnalysisNodes_with_single_list_defining_unique_path(self):
        cab = CompAnalysisBase(pNode=self.node10FEM,
                               analysisBranches=[['10.0', 'FEM', 'elliptic', 'LF']],
                               criteria=['areas', 'K3'], sifs=['K1', 'K2'],
                               errType='rmsd')
        cab.setAnalysisNodes()
        self.assertEqual(set([self.node10FEMeLF]), set(cab.aNodes))

    def test_setAnalysisNodes_with_None(self):
        cab = CompAnalysisBase(pNode=self.node10FEM,
                               analysisBranches=[None],
                               criteria=['areas', 'K3'], sifs=['K1', 'K2'],
                               errType='rmsd')
        cab.setAnalysisNodes()
        self.assertEqual(set([]), set(cab.aNodes))

    def test_setAnalysisNodes_with_single_list_defining_ambiguious_path(self):
        self.assertRaises(KeyError, self.cab.setAnalysisNodes)

    def test_getSubplotTitle_with_depth_value_lower_than_node_level(self):
        exp = 'FEM elliptic QF'
        self.assertEqual(exp,
                         self.cab.getSubplotTitle(self.node1FEMeQF, depth=3))
        exp = 'elliptic QF'
        self.assertEqual(exp,
                         self.cab.getSubplotTitle(self.node1FEMeQF, depth=2))
        exp = '10.0 XFEM cp LR'
        self.assertEqual(
            exp, self.cab.getSubplotTitle(
                self.node10XFEMcpLR, depth=4))
        exp = 'FEM elliptic'
        self.assertEqual(exp,
                         self.cab.getSubplotTitle(self.node3FEMe, depth=2))

    def test_getSubplotTitle_with_depth_value_higher_than_node_level(self):
        self.assertRaises(
            IndexError, self.cab.getSubplotTitle, self.root, 2)
        self.assertRaises(
            IndexError, self.cab.getSubplotTitle, self.node1FEMeQF, 5)

    def test_createDataDict(self):
        cdeMock = MagicMock(side_effect=[1, 2])
        self.cab.dataStr = [[{1: 1}, 10], [{2: 2}, 20]]
        with patch(classPath + '.createDataDictEntry', cdeMock):
            self.cab.createDataDict()
        self.assertEqual([1, 2], self.cab.dataDicts)
        expCalls = [call({1: 1}), call({2: 2})]
        self.assertEqual(expCalls, cdeMock.mock_calls)

    def test_createDataDictEntry(self):
        def mockSF(simKey):
            if simKey == [1]:
                return {'K1': 11, 'K2': 12, 'K3': 13}
            elif simKey == [2]:
                return {'K1': 21, 'K2': 22, 'K3': 23}
        gseMock = MagicMock(side_effect=mockSF)
        with patch(classPath + '.getSimIdErrors', gseMock):
            res = self.cab.createDataDictEntry({0.1: [1], 0.2: [2]})
        exp = {'K1': {0.1: 11, 0.2: 21}, 'K2': {0.1: 12, 0.2: 22}}
        self.assertEqual(exp, res)

    def test_getSimIdErrors_with_empty_failed_simId(self):
        exp = {'K1': [], 'K2': []}
        self.assertEqual(exp, self.cab.getSimIdErrors([]))

    def test_getSimIdErrors_with_nonempty_successful_simId(self):
        adMock = MagicMock()
        adMock().getErrorReports.return_value = {
            'rmsd': {'K1': 11, 'K2': 22, 'K3': 33}}
        with patch('dataProcessing.AnalysisData', adMock):
            res = self.cab.getSimIdErrors([1])
        self.assertEqual({'K1': 11, 'K2': 22}, res)

    def test_createSelectionDict(self):
        self.cab.dataStr = [
            [{0.1: [11], 0.2:[22]}, 1, 'a'],
            [{3: [33], 4:[44]}, 2, 'b']]
        self.cab.createSelectionDict()
        exp = {0.1: [11], 0.2: [22], 3: [33], 4: [44]}
        self.assertEqual(exp, self.cab.sData)

    def test_getOptSimKey(self):
        leMock = MagicMock(return_value={(100, 10): ('simid1', 2)})
        dataDict = {0.1: ['simid1'], 0.2: ['simid2'], 0: ['simid3']}
        with patch(
                'plotFuncs.getSimIdsWithLowestErrorPerDH',
                leMock):
            res = self.cab.getOptSimKey(dataDict, set(['simid1', 'simid2']))
        self.assertEqual(0.1, res)
        leMock.assert_called_once_with(
            set(['simid1', 'simid2']), 'areas', 'K3')

    def test_assignSimIdAsFailed_with_None(self):
        self.cab.sData = {1: 11, 2: 22}
        self.cab.assignSimIdAsFailed('tree', 'queue', None)
        self.assertEqual({1: 11, 2: 22}, self.cab.sData)

    def test_assignSimIdAsFailed_with_valid_selection(self):
        self.cab.sData = {1: 11, 2: 22}
        queueMock = MagicMock()
        shelveMock = MagicMock()
        sfMock = MagicMock()
        sfPath = 'sessionFuncs'
        with patch(sfPath + '.writeToShelve', shelveMock):
            with patch(sfPath + '.setSimIdAsFailed', sfMock):
                self.cab.assignSimIdAsFailed('tree', queueMock, 1)
        self.assertEqual({2: 22}, self.cab.sData)

        queueMock.removeSimIdFromQueue.assert_called_once_with(11)
        shelveMock.assert_called_once_with(11, 'failed')
        sfMock.assert_called_once_with('tree', [11])
