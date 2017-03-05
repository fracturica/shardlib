import unittest
from mock import Mock, MagicMock, patch, call
import numpy as np
from trees import TreeNode
from test_treeSetUp import TreeSetUp
from plotFuncs import getBranchSimIdsByCriteria, getDiamHeightError, getCeAeError, createCeAeDataStr, createD_H_SimId_Err_ValDataStr, getSimIdsWithLowestErrorPerDH, selectSimsForMinErrors, getContourPlotData, prepContourPlotData


class TestGetBranchSimIdsByCriteria(TreeSetUp):

    def test_getBranchSimIdsByCriteria_criteria_starting_from_root(self):
        exp = (set(['node1FEMsQR_sm_1', 'node1FEMsQR_sm_2']),
               set(['node1FEMsQR_fm_1']))
        inCrit = ['root', '1.0', 'FEM', 'scale', 'QR']
        self.assertEqual(exp, getBranchSimIdsByCriteria(self.root, inCrit))

    def test_getBranchSimIdsByCriteria_criteria_notstarting_from_root(self):
        exp = (set(['node2FEMsQF_sm_1', 'node2FEMsQF_sm_2']), set([]))
        inCrit = ['2.0', 'FEM', 'scale', 'QF']
        self.assertEqual(exp, getBranchSimIdsByCriteria(self.root, inCrit))

    def test_getBranchSimIdsByCriteria_criteria_not_ending_at_leaf_node(self):
        exp = (set(['node1FEMsQR_sm_1', 'node1FEMsQR_sm_2', 'node1FEMsLR_sm_1']),
               set(['node1FEMsQR_fm_1', 'node1FEMsLR_fm_1']))
        inCrit = ['root', '1.0', 'FEM', 'scale']
        self.assertEqual(exp, getBranchSimIdsByCriteria(self.root, inCrit))

    def test_getBranchSimIdsByCriteria_with_criteria_not_corresponding_to_the_tree_1(
            self):
        inCrit = ['root', 'nonexisting', 'FEM', 'scale', 'LR']
        self.assertRaises(
            KeyError,
            getBranchSimIdsByCriteria,
            self.root,
            inCrit)

    def test_getBranchSimIdsByCriteria_with_criteria_not_corresponding_to_the_tree_2(
            self):
        inCrit = ['1.0', 'FEM', 'scale', 'QF']
        self.assertRaises(
            KeyError,
            getBranchSimIdsByCriteria,
            self.root,
            inCrit)

    def test_getBranchSimIdsByCriteria_with_criteria_not_corresponding_to_the_tree_3(
            self):
        inCrit = ['QF', 'scale', 'FEM', '2.0']
        self.assertRaises(
            KeyError,
            getBranchSimIdsByCriteria,
            self.root,
            inCrit)


class TestGetDHErrType(unittest.TestCase):

    def setUp(self):
        self.adMock = MagicMock()
        self.adMock().getContainerDiam.return_value = 'd100'
        self.adMock().getContainerHeight.return_value = 'h50'
        self.adMock().getErrorReports.return_value = {
            'difference': {'K1': 'diffK1', 'K2': 'diffK2'},
            'areas': {'K1': 'areasK1', 'K2': 'areasK2'}}
        self.adPatch = patch(
            'dataProcessing.AnalysisData',
            self.adMock)
        self.adPatch.start()

    def tearDown(self):
        self.adPatch.stop()

    def test_getDiamHeightError_difference_K1(self):
        exp = ('d100', 'h50'), 'diffK1'
        self.assertEqual(
            exp, getDiamHeightError(
                'simid_1', 'difference', 'K1'))

    def test_getDiamHeightError_areas_K2(self):
        exp = ('d100', 'h50'), 'areasK2'
        self.assertEqual(exp, getDiamHeightError('simid_2', 'areas', 'K2'))


class TestGetCeAeError(unittest.TestCase):

    def setUp(self):
        self.adMock = MagicMock()
        self.adMock().getMeshParams.return_value = {
            'crackEdges': 0.5, 'allEdges': 5, 'cz': 2}
        self.adMock().getErrorReports.return_value = {
            'rmsd': {'K1': 11, 'K2': 12},
            'diff': {'K1': 21, 'K2': 22}}
        self.adPatch = patch(
            'dataProcessing.AnalysisData', self.adMock)
        self.adPatch.start()

    def tearDown(self):
        self.adPatch.stop()

    def test_getCeAeError_with_successful_True_K1(self):
        key, err = getCeAeError('simid', 'rmsd', 'K1', successful=True)
        self.assertEqual((0.5, 5), key)
        self.assertEqual(11, err)

    def test_getCeAeError_with_successful_True_K2(self):
        key, err = getCeAeError('simid1', 'diff', 'K2', successful=True)
        self.assertEqual((0.5, 5), key)
        self.assertEqual(22, err)

    def test_getCeAeError_with_successful_False(self):
        key, err = getCeAeError('simid', 'rmsd', 'K2', successful=False)
        self.assertEqual((0.5, 5), key)
        self.assertIsNone(err)


class TestCreateCeAeDataStr(unittest.TestCase):

    def setUp(self):
        def mockSF(simId, errType, sif, successful=True):
            data = {
                'simid1': {
                    'rmsd': {
                        'K1': 111, 'K2': 112}, 'diff': {
                        'K1': 121, 'K2': 122}}, 'simid2': {
                    'rmsd': {
                        'K1': 211, 'K2': 212}, 'diff': {
                            'K1': 221, 'K2': 222}}, 'simid3': {
                                'rmsd': {
                                    'K1': 311, 'K2': 312}, 'diff': {
                                        'K1': 321, 'K2': 322}}, 'simid4': {
                                            'rmsd': {
                                                'K1': 411, 'K2': 412}, 'diff': {
                                                    'K1': 421, 'K2': 422}}}
            keys = {
                'simid1': (0.1, 1), 'simid2': (0.2, 2),
                'simid3': (0.3, 3), 'simid4': (0.4, 4)}
            if successful:
                return keys[simId], data[simId][errType][sif]
            else:
                return keys[simId], None

        self.simids = ['simid1', 'simid2', 'simid3', 'simid4']
        self.caeMock = MagicMock(side_effect=mockSF)
        self.caePatch = patch(
            'plotFuncs.getCeAeError', self.caeMock)
        self.caePatch.start()

    def tearDown(self):
        self.caePatch.stop()

    def test_createCeAeDataStr_with_rmsd_K1_successful_True(self):
        res = createCeAeDataStr(self.simids, 'rmsd', 'K1', successful=True)
        exp = {(0.1, 1): ('simid1', 111), (0.2, 2): ('simid2', 211),
               (0.3, 3): ('simid3', 311), (0.4, 4): ('simid4', 411)}
        self.assertEqual(exp, res)

    def test_createCeAeDataStr_with_diff_K2_successful_True(self):
        res = createCeAeDataStr(self.simids, 'diff', 'K2', successful=True)
        exp = {(0.1, 1): ('simid1', 122), (0.2, 2): ('simid2', 222),
               (0.3, 3): ('simid3', 322), (0.4, 4): ('simid4', 422)}
        self.assertEqual(exp, res)

    def test_createCeAeError_wint_successful_False(self):
        res = createCeAeDataStr(self.simids, 'diff', 'K2', successful=False)
        exp = {(0.1, 1): ('simid1', None), (0.2, 2): ('simid2', None),
               (0.3, 3): ('simid3', None), (0.4, 4): ('simid4', None)}
        self.assertEqual(exp, res)


class TestCreateD_H_SimId_Err_ValDataStr(unittest.TestCase):

    def setUp(self):
        def mockSF(simId, errType, sif):
            data = {
                'simid_1': ((100, 10), 1), 'simid_2': ((200, 20), 2),
                'simid_3': ((100, 10), 3), 'simid_4': ((200, 20), 4),
                'simid_5': ((300, 30), 5), 'simid_6': ((500, 50), 6)}
            return data[simId]
        dheMock = MagicMock(side_effect=mockSF)
        self.dheP = patch(
            'plotFuncs.getDiamHeightError', dheMock)
        self.dheP.start()

    def tearDown(self):
        self.dheP.stop()

    def test_createD_H_SimId_Err_ValDataStr(self):
        exp = {(100, 10): [('simid_1', 1), ('simid_3', 3)],
               (200, 20): [('simid_2', 2), ('simid_4', 4)],
               (300, 30): [('simid_5', 5)],
               (500, 50): [('simid_6', 6)]}
        simIds = [
            'simid_6',
            'simid_5',
            'simid_4',
            'simid_3',
            'simid_2',
            'simid_1']
        res = createD_H_SimId_Err_ValDataStr(simIds, 'err', 'K1')
        for k in res.keys():
            self.assertEqual(set(exp[k]), set(res[k]))


class TestGetSimIdsWithLowestErrorPerDH(unittest.TestCase):

    def setUp(self):
        returnVal = {
            (100, 10): [('s1', 1), ('s2', 2), ('s3', -1), ('s4', 0)],
            (200, 20): [('s5', 10.0), ('s6', 5), ('s7', -3)],
            (300, 30): [('s8', 9)]}
        dheMock = MagicMock(return_value=returnVal)
        self.dheP = patch(
            'plotFuncs.createD_H_SimId_Err_ValDataStr',
            dheMock)
        self.dheP.start()

    def tearDown(self):
        self.dheP.stop()

    def test_getSimIdsWithLowestErrorPerDH(self):
        exp = {(100, 10): ('s4', 0), (200, 20)               : ('s7', -3), (300, 30): ('s8', 9)}
        self.assertEqual(
            exp, getSimIdsWithLowestErrorPerDH(
                'simids', 'err', 'K1'))


class TestSelectSimsForMinErrors(unittest.TestCase):

    def setUp(self):
        self.data = {
            'dotProd': {
                'K1': {
                    (100, 10): ('s1dp', 11), (200, 20): ('s2dp', 12),
                    (300, 30): ('s3dp', 13)},
                'K2': {
                    (100, 10): ('s4dp', 21), (200, 20): ('s5dp', 22),
                    (300, 30): ('s6dp', 23)}},
            'areas': {
                'K1': {
                    (100, 10): ('s7a', 11), (200, 20): ('s8a', 12),
                    (300, 30): ('s9a', 13)},
                'K2': {
                    (100, 10): ('s10a', 21), (200, 20): ('s11a', 22),
                    (300, 30): ('s12a', 23)}}}

        def mockSF(simIds, errType, sif):
            return self.data[errType][sif]
        dhMock = MagicMock(side_effect=mockSF)
        self.dhp = patch(
            'plotFuncs.getSimIdsWithLowestErrorPerDH',
            dhMock)
        self.dhp.start()

    def tearDown(self):
        self.dhp.stop()

    def test_selectSimsForMinErrors_with_single_errorType_and_sif(self):
        exp = {'dotProd': {'K1': self.data['dotProd']['K1']}}
        self.assertEqual(exp,
                         selectSimsForMinErrors('sims', ['dotProd'], ['K1']))

    def test_selectSimsForMinErrors_with_two_errorTypes_and_sifs(self):
        self.assertEqual(
            self.data, selectSimsForMinErrors(
                'sims', [
                    'dotProd', 'areas'], [
                    'K1', 'K2']))


class TestGetContourPlotData(unittest.TestCase):

    def setUp(self):
        self.data = {
            (100, 10): ('s1', 1), (200, 20): ('s2', 2), (300, 30): ('s3', 3),
            (400, 40): ('s4', 4), (500, 50): ('s5', 5), (600, 60): ('s6', 6)}

    def test_getContourPlotData(self):
        exp = (
            [100, 200, 300, 400, 500, 600],
            [10, 20, 30, 40, 50, 60], [1, 2, 3, 4, 5, 6])
        res = getContourPlotData(self.data)
        self.assertEqual(len(exp), len(res))
        for i in range(len(exp)):
            self.assertEqual(set(exp[i]), set(res[i]))
            self.assertEqual(len(exp[0]), len(res[i]))
        for i in range(len(res[0])):
            self.assertEqual(res[0][i] / 10., res[1][i])
            self.assertEqual(res[1][i] / 10., res[2][i])


class TestPrepContourPlotData(unittest.TestCase):

    def setUp(self):
        self.sMRDict = {
            1: [[100, 200, 101, 201], [10, 20, 11, 21], [1, 2, -1, -2]],
            2: [[300, 400, 301, 401], [30, 40, 31, 41], [3, 4, -3, -4]],
            3: [[500, 600, 501, 601], [50, 60, 51, 61], [5, 6, -5, -6]]}

        def cMockSF(data):
            return self.sMRDict[data]
        cMock = MagicMock(side_effect=cMockSF)
        self.gPatch = patch(
            'plotFuncs.getContourPlotData', cMock)
        self.gPatch.start()

    def tearDown(self):
        self.gPatch.stop()

    def test_prepContourPlotData_with_3_sifs_and_areas_errType(self):
        dataDict = {'K1': 1, 'K2': 2, 'K3': 3}
        expSifs = ['K1', 'K2', 'K3']
        expD = [[100, 200, 101, 201], [
            300, 400, 301, 401], [500, 600, 501, 601]]
        expH = [[10, 20, 11, 21], [30, 40, 31, 41], [50, 60, 51, 61]]
        expErrs = [[1, 2, -1, -2], [3, 4, -3, -4], [5, 6, -5, -6]]
        expMinErr = -6
        expMaxErr = 6
        res = prepContourPlotData(dataDict, 'areas')
        self.assertEqual(expSifs, res[0])
        for i in range(len(expSifs)):
            self.assertEqual(expD[i], list(res[1][i]))
            self.assertEqual(expH[i], list(res[2][i]))
            self.assertEqual(expErrs[i], list(res[3][i]))
        self.assertEqual(expMinErr, res[4])
        self.assertEqual(expMaxErr, res[5])

    def test_prepContourPlotData_with_2_sifs_and_dotProd_errType(self):
        dataDict = {'K1': 1, 'K2': 2}
        expSifs = ['K1', 'K2']
        expD = [[100, 200, 101, 201], [300, 400, 301, 401]]
        expH = [[10, 20, 11, 21], [30, 40, 31, 41]]
        expErrs = [[1, 2, 1, 2], [3, 4, 3, 4]]
        expMinErr = 1
        expMaxErr = 4
        res = prepContourPlotData(dataDict, 'dotProd')
        self.assertEqual(expSifs, res[0])
        for i in range(len(expSifs)):
            self.assertEqual(expD[i], list(res[1][i]))
            self.assertEqual(expH[i], list(res[2][i]))
            self.assertEqual(expErrs[i], list(res[3][i]))
        self.assertEqual(expMinErr, res[4])
        self.assertEqual(expMaxErr, res[5])
