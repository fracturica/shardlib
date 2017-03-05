import unittest
from mock import Mock, MagicMock, patch, call
from comp_analysis.SIMCompAnalysis import BoundsCompPlot
from test_SIMCompAnalysis import SIMCompAnalysisSetUp
import numpy as np


modulePath = 'comp_analysis.SIMCompAnalysis'


class TestBoundsCompPlot(SIMCompAnalysisSetUp):

    def setUp(self):
        SIMCompAnalysisSetUp.setUp(self)
        self.bcp = BoundsCompPlot(self.lq, ['rmsd', 'K1'], ['K1', 'K2', 'K3'])

    def test_createDataStr(self):
        self.bcp.items = [2, 4]
        self.bcp.createDataStr()
        exp = [
            [{2: self.node1FEMsLR}, None, 'angles', 'FEM scale LR'],
            [{4: self.node1XFEMcpLT}, None, 'angles', 'XFEM cp LT']]
        self.assertEqual(exp, self.bcp.dataStr)

    def test_getPercentPointsInPoly_with_values_that_add_up(self):
        cMock = MagicMock(return_value=(200, 41, 159))
        with patch(modulePath + '.BoundsCompPlot.countPointInOutOfContour', cMock):
            res = self.bcp.getPercentPointsInPoly('adn', 100, 'K1')
        self.assertAlmostEqual(20.5, res)

    def test_getPercentPointsInPoly_with_values_not_adding_up(self):
        cMock = MagicMock(return_value=(200, 10, 100))
        with patch(modulePath + '.BoundsCompPlot.countPointInOutOfContour', cMock):
            self.assertRaises(
                AssertionError,
                self.bcp.getPercentPointsInPoly,
                'adn',
                100,
                'K1')

    def test_countPointInOutOfContour_with_inside_and_outside_points(self):
        pMock = MagicMock(return_value=np.array(
            [True, False, True, False, False, False, True, True, True]))
        with patch(modulePath + '.BoundsCompPlot.getInOutOfContour', pMock):
            a, i, o = self.bcp.countPointInOutOfContour('adn', 100, 'K1')
        self.assertEqual((9, 5, 4), (a, i, o))

    def test_createVertsForPolyPath(self):
        x = [1, 2, 3, 4]
        y = [10, 20, 30, 40]
        verts = self.bcp.createVertsForPolyPath(x, y)
        exp = [[1, -10e16], [1, 10], [2, 20], [3, 30], [4, 40], [4, -10e16]]
        self.assertEqual(exp, verts)

    def test_getInOutOfContour(self):
        def ioMockSF(angles, yVals, points):
            return angles, yVals, points
        adn = MagicMock()
        adn.getAngles.return_value = [1, 2, 3, 4]
        adn.getResults.return_value = {'K3': np.array([5, -6, -7, 8])}
        adn.calcSIFsForSigmaAndSIF.return_value = [-9, -10, 11, 12]
        ioMock = MagicMock(side_effect=ioMockSF)
        with patch(modulePath + '.BoundsCompPlot.getInOutPointsArray', ioMock):
            res = self.bcp.getInOutOfContour(adn, 100, 'K3')
        self.assertEqual([1, 2, 3, 4], res[0])
        self.assertTrue((np.array([9, 10, 11, 12]) == res[1]).all())
        self.assertEqual([[1, 5], [2, 6], [3, 7], [4, 8]], res[2])

    def test_getInOutPoints_with_possible_point_positions(self):
        def iocMockSF(adn, sigma, sif):
            if sigma == 110:
                return [True, True, False]
            elif sigma == 100:
                return [True, False, False]
            else:
                raise ValueError('iocMock called with unexpected sigma value')
        exp = [[[2], [20]], [[1, 3], [10, 30]]]
        iocMock = MagicMock(side_effect=iocMockSF)
        adnMock = MagicMock()
        adnMock.getAngles.return_value = [1, 2, 3]
        adnMock.getResults.return_value = {'K1': [10, 20, 30]}
        with patch(modulePath + '.BoundsCompPlot.getInOutOfContour', iocMock):
            res = self.bcp.getInOutPoints(adnMock, 100, 110, 'K1')
        self.assertEqual(exp, res)

    def test_getInOutPoints_with_impossible_point_positions(self):
        def iocMockSF(adn, sigma, sif):
            if sigma == 110:
                return [False]
            elif sigma == 100:
                return [True]
            else:
                raise ValueError('iocMock called with unexpected sigma value')
        iocMock = MagicMock(side_effect=iocMockSF)
        adnMock = MagicMock()
        adnMock.getAngles.return_value = [1]
        adnMock.getResults.return_value = {'K1': [10]}
        with patch(modulePath + '.BoundsCompPlot.getInOutOfContour', iocMock):
            res = self.bcp.getInOutPoints(adnMock, 100, 110, 'K1')
        exp = [[[], []], [[1], [10]]]

    def test_findSigmaBound(self):
        log = {'sigma': [], 'pip': []}

        def pipMockSF(adn, sigma, sif):
            self.assertEqual('K1', sif)
            self.assertEqual('adn', adn)
            return sigma / 10.
        self.bcp.tol = 0.1
        self.bcp.iterLim = 100
        pipMock = MagicMock(side_effect=pipMockSF)
        with patch(modulePath + '.BoundsCompPlot.getPercentPointsInPoly', pipMock):
            res = self.bcp.findSigmaBound('adn', 1000, 0, 'K1', 41.3, log)
        self.assertAlmostEqual(41.3, res['pip'][-1], delta=0.1)
        self.assertAlmostEqual(413, res['sigma'][-1], delta=1)

    def test_createDataDicts(self):
        def sbMockSF(adn, sigmaUp, sigmaLow, sif, target, log):
            if sif == 'K1':
                return {
                    'sigma': [
                        100 +
                        target +
                        sigmaUp],
                    'pip': [
                        0.1 +
                        target]}
            elif sif == 'K2':
                return {
                    'sigma': [
                        200 +
                        target +
                        sigmaUp],
                    'pip': [
                        0.2 +
                        target]}
            elif sif == 'K3':
                return {
                    'sigma': [
                        300 +
                        target +
                        sigmaUp],
                    'pip': [
                        0.3 +
                        target]}
            else:
                raise KeyError('unknown sif value: {0}'.format(sif))
        adnMock = MagicMock()
        adnMock().getAnSolParams.side_effect = [
            {'sigma': 1000}, {'sigma': 3000}]
        sbMock = MagicMock(side_effect=sbMockSF)
        self.bcp.items = [1, 3]
        self.bcp.targets = {'lower': 5, 'upper': 95}
        self.bcp.dataStr = [
            [{1: self.node1FEMeQF}, None, 'angles', 'FEM elliptic QF'],
            [{3: self.node1FEMsQR}, None, 'angles', 'FEM scale QR']]
        with patch(modulePath + '.BoundsCompPlot.findSigmaBound', sbMock):
            with patch(
                    'dataProcessing.AnalysisNodeData', adnMock):
                self.bcp.createDataDicts()
        expLog1 = {
            'K1': {
                'upper': {'sigma': [2195], 'pip': [95.1]},
                'lower': {'sigma': [2105], 'pip': [5.1]}},
            'K2': {
                'upper': {'sigma': [2295], 'pip': [95.2]},
                'lower': {'sigma': [2205], 'pip': [5.2]}},
            'K3': {
                'upper': {'sigma': [2395], 'pip': [95.3]},
                'lower': {'sigma': [2305], 'pip': [5.3]}}}
        expLog2 = {
            'K1': {
                'upper': {'sigma': [6195], 'pip': [95.1]},
                'lower': {'sigma': [6105], 'pip': [5.1]}},
            'K2': {
                'upper': {'sigma': [6295], 'pip': [95.2]},
                'lower': {'sigma': [6205], 'pip': [5.2]}},
            'K3': {
                'upper': {'sigma': [6395], 'pip': [95.3]},
                'lower': {'sigma': [6305], 'pip': [5.3]}}}
        print self.bcp.dataDicts[0][1]['K1']
        print expLog1['K1']
        for sif in self.bcp.sifs:
            self.assertEqual(expLog1[sif], self.bcp.dataDicts[0][1][sif])
            self.assertEqual(expLog2[sif], self.bcp.dataDicts[1][1][sif])
