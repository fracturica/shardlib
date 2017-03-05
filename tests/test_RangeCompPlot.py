import unittest
from mock import Mock, MagicMock, patch, call
from comp_analysis.SIMCompAnalysis import RangeCompPlot
from test_SIMCompAnalysis import SIMCompAnalysisSetUp
import numpy as np


modulePath = 'comp_analysis.SIMCompAnalysis'


class TestRangeCompPlot(SIMCompAnalysisSetUp):

    def setUp(self):
        SIMCompAnalysisSetUp.setUp(self)
        self.rcp = RangeCompPlot(self.lq, ['rmsd', 'K1'], ['K1', 'K2', 'K3'])

    def test_createDataStr(self):
        optMock = MagicMock(side_effect=[2, 6])
        self.rcp.items = {1: 10, 3: 30}
        with patch(modulePath + '.RangeCompPlot.getOptSim', optMock):
            self.rcp.createDataStr()
        exp = [
            [{1: self.node1FEMeQF}, 2, 'angles', 'FEM elliptic QF'],
            [{3: self.node1FEMsQR}, 6, 'angles', 'FEM scale QR']]
        self.assertEqual(exp, self.rcp.dataStr)

    def test_getOptSim_with_True_optSim_option(self):
        self.rcp.opts = {'optSim': True}
        sMock = MagicMock(return_value={(100, 10): ('simid1', 3)})
        with patch(
                'plotFuncs.getSimIdsWithLowestErrorPerDH',
                sMock):
            optSim = self.rcp.getOptSim(self.node1FEMsQR)
        self.assertEqual('simid1', optSim)
        sMock.assert_called_once_with(
            self.node1FEMsQR.getSuccessfulMembers(), 'rmsd', 'K1')

    def test_getOptSim_with_False_optSim_option(self):
        self.rcp.opts = {'optSim': False}
        self.assertIsNone(self.rcp.getOptSim(self.node1FEMsQR))

    def test_createDataDict(self):
        self.rcp.dataStr = [
            [{1: self.node1FEMeQF}, 2, 'angles', 'FEM elliptic QF'],
            [{3: self.node1FEMsQR}, 6, 'angles', 'FEM scale QR']]
        parMock = MagicMock(side_effect=[(11, 12, 13, 14), (21, 22, 23, 24)])
        with patch(modulePath + '.RangeCompPlot.getNodeParams', parMock):
            self.rcp.createDataDict()
        exp = [(11, 12, 13, 14), (21, 22, 23, 24)]
        self.assertEqual(exp, self.rcp.dataDicts)
        expCalls = [call(self.node1FEMeQF), call(self.node1FEMsQR)]
        self.assertEqual(expCalls, parMock.mock_calls)

    def test_createSlices(self):
        self.rcp.dataStr = [
            [{1: self.node1FEMeQF}, 2, 'angles', 'FEM elliptic QF'],
            [{3: self.node1FEMsQR}, 6, 'angles', 'FEM scale QR']]
        self.rcp.items = {1: 11, 3: 33}
        self.rcp.dataDicts = [(11, 12, 13, 14), (21, 22, 23, 24)]

        def sMockSF(vals, numInts):
            if (vals, numInts) == (11, 11):
                return 111
            elif (vals, numInts) == (21, 33):
                return 333
            else:
                raise KeyError
        sMock = MagicMock(side_effect=sMockSF)
        with patch(modulePath + '.RangeCompPlot.createSliceIndices', sMock):
            self.rcp.createSlices()
        exp = [111, 333]
        self.assertEqual(exp, self.rcp.slices)

    def test_createSliceIndices_with_non_repeating_value_argument_elements(
            self):
        x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        n = 3
        exp = [[0, 3], [3, 6], [6, 12]]
        slices = self.rcp.createSliceIndices(x, n)
        self.assertEqual(exp, slices)

    def test_createSliceIndices_with_repeating_value_argument_elements(self):
        x = np.array([1, 2, 3, 3, 3, 3, 4, 4, 4, 5, 9, 9, 9, 9])
        n = 3
        exp = [[0, 2], [2, 10], [10, 15]]
        slices = self.rcp.createSliceIndices(x, n)
        self.assertEqual(exp, slices)

    def test_createSliceIndices_with_small_in_the_beginning_of_the_value(self):
        x = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1000])
        n = 5
        self.assertRaises(ValueError, self.rcp.createSliceIndices, x, n)

    def test_createSliceIndices_with_sequence(self):
        x = np.arange(1, 100)
        n = 2
        sl = self.rcp.createSliceIndices(x, n)
        exp = list(x[sl[0][0]:sl[0][1]]) + list(x[sl[1][0]:sl[1][1]])
        self.assertEqual(exp, list(x))

    def test_createSliceIndices_with_small_sequence(self):
        x = np.arange(0, 7)
        n = 2
        exp = [[0, 3], [3, 8]]
        sl = self.rcp.createSliceIndices(x, n)
        self.assertEqual(exp, sl)
        resX = list(x[sl[0][0]:sl[0][1]]) + list(x[sl[1][0]:sl[1][1]])
        self.assertEqual(list(x), resX)

    def test_createVerts_with_min_func(self):
        slices = [[0, 4], [4, 8]]
        angles = range(7)
        values = [1, 3, 5, 4, 5, -2, 9]
        exp = [[0, 1], [3, 1], [3, -2], [6, -2]]
        res = self.rcp.createVerts(slices, angles, values, min)
        self.assertEqual(exp, res)

    def test_createVerts_with_max_func(self):
        slices = [[0, 4], [4, 8]]
        angles = range(7)
        values = [1, 3, 5, 6, 5, -2, 9]
        exp = [[0, 6], [3, 6], [3, 9], [6, 9]]
        res = self.rcp.createVerts(slices, angles, values, max)
        self.assertEqual(exp, res)

    def test_createVerts_with_max_consequent_values(self):
        slices = [[0, 3], [3, 8]]
        angles = range(7)
        values = range(7)
        exp = [[0, 2], [2, 2], [2, 6], [6, 6]]
        res = self.rcp.createVerts(slices, angles, values, max)
        self.assertEqual(exp, res)

    def test_createVerts2_with_min_func(self):
        slices = [[0, 4], [4, 8]]
        angles = range(7)
        values = np.array([1, 3, 5, 4, 5, -2, 9])
        exp = [[0, -0.5], [0, 1], [5, -2], [6, -0.5]]
        res = self.rcp.createVerts2(slices, angles, values, min)
        self.assertEqual(exp, res)

    def test_createVerts2_with_max_func(self):
        slices = [[0, 4], [4, 8]]
        angles = range(7)
        values = np.array([1, 3, 5, 4, 5, -2, 9])
        exp = [[0, 7], [2, 5], [6, 9], [6, 7]]
        res = self.rcp.createVerts2(slices, angles, values, max)
        self.assertEqual(exp, res)
