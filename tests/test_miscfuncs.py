import unittest
from mock import Mock, MagicMock, patch
from miscFuncs import *
import numpy as np

modulePath = 'miscFuncs.'


class TestDotProd(unittest.TestCase):

    def test_dotProd_with_vectors_of_equal_length(self):
        A = [[1, 1, 1], [1, 1, 1], [45, 45, 45], [
            45, 45, 45], [45, 45, 45], [3, 3, 3]]
        B = [[1, 2, 3], [4, 5, 6], [-1, 0, 0],
             [0, -1, 0], [0, 0, -1], [0, 0, 0]]
        expected = [6, 15, -45, -45, -45, 0]
        for i in range(len(expected)):
            self.assertAlmostEqual(expected[i], dotProd(A[i], B[i]))

    def test_dotProd_with_different_length_vectors(self):
        a = [1, 2, 3]
        b = [1, 1]
        self.assertRaises(AssertionError, dotProd, a, b)

    def test_dotProd_with_multidimensional_arrays(self):
        a = [[1, 1], [2, 2]]
        b = [[1, 3], [5, 5]]
        self.assertRaises(AssertionError, dotProd, a, b)


class TestCalcAbsoluteArea(unittest.TestCase):

    def test_calcAbsoluteArea_with_two_negative_y_values(self):
        y = [-2, -3]
        x = [0, 1]
        expected = 2.5
        self.assertAlmostEqual(expected, calcAbsoluteArea(x, y))

    def test_calcAbsoluteArea_with_two_positive_y_values(self):
        y = [2, 3]
        x = [0, 1]
        expected = 2.5
        self.assertAlmostEqual(expected, calcAbsoluteArea(x, y))

    def test_calcAbsoluteArea_with_one_positive_and_one_negative_y_value(self):
        y = [2, -3]
        x = [0, 1]
        expected = 2.5
        self.assertAlmostEqual(expected, calcAbsoluteArea(x, y))

    def test_calcAbsoluteArea_with_larger_sequence_of_y_values(self):
        y = [2, 3, -1]
        x = [0, 1, 2]
        expected = 4.5
        self.assertAlmostEqual(expected, calcAbsoluteArea(x, y))

    def test_calcAbsoluteArea_with_unordered_x_values(self):
        y = [2, 3]
        x = [1, 0]
        self.assertRaises(AssertionError, calcAbsoluteArea, x, y)

    def test_calcAbsoluteArea_with_different_length_x_and_y(self):
        y = [2, 3, 4]
        x = [0, 1]
        self.assertRaises(AssertionError, calcAbsoluteArea, x, y)

    def test_calcAbsoluteArea_with_multidimensional_arrays(self):
        y = [[1, 1], [2, 3]]
        x = [[0, 1], [2, 3]]
        self.assertRaises(AssertionError, calcAbsoluteArea, x, y)

    def test_calcAbsoluteArea_with_negative_x_element(self):
        y = [1, 2]
        x = [-2, 2]
        self.assertRaises(AssertionError, calcAbsoluteArea, x, y)


class TestCalcDotProdDiff(unittest.TestCase):

    def test_calcDotProdDiff_with_nonzero_inputs_higher_analytical(self):
        analytical = [3, 4]
        analysis = [2, 3]
        expected = -12.0 / 25.0
        self.assertAlmostEqual(expected, calcDotProdDiff(analysis, analytical))

    def test_calcDotProdDiff_with_nonzero_inputs_higher_analysis(self):
        analytical = [2, 3]
        analysis = [3, 4]
        expected = 12.0 / 13.0
        self.assertAlmostEqual(expected, calcDotProdDiff(analysis, analytical))

    def test_calcDotProdDiff_with_zero_analysis_and_nonzero_analytical(self):
        analytical = [3, 4]
        analysis = [0, 0]
        expected = -1
        self.assertAlmostEqual(expected, calcDotProdDiff(analysis, analytical))

    def test_calcDotProdDiff_with_zero_analytical_and_nonzero_analysis(self):
        analytical = [0., 0.]
        analysis = [3, 4]
        self.assertRaises(
            ZeroDivisionError,
            calcDotProdDiff,
            analysis,
            analytical)


class TestCalcAreaDiff(unittest.TestCase):

    def test_calcAreaDiff_with_nonzero_inputs_higher_analytical(self):
        angles = [0, 1]
        analysisData = [2, 3]
        analyticalData = [3, 4]
        expected = -1.0 / 3.5
        self.assertAlmostEqual(
            expected,
            calcAreaDiff(
                angles,
                analysisData,
                analyticalData))

    def test_calAreaDiff_with_nonzero_inputs_higher_analysis(self):
        angles = [0, 1]
        analysisData = [3, 4]
        analyticalData = [2, 3]
        expected = 1.0 / 2.5
        self.assertAlmostEqual(
            expected,
            calcAreaDiff(
                angles,
                analysisData,
                analyticalData))

    def test_calcAreaDiff_with_zero_analysis_and_nonzero_analytical(self):
        angles = [0, 1]
        analysisData = [0, 0]
        analyticalData = [1, 2]
        expected = -1
        self.assertAlmostEqual(
            expected,
            calcAreaDiff(
                angles,
                analysisData,
                analyticalData))

    def test_calcAreaDiff_with_zero_analytical_and_nonzero_analysis(self):
        angles = [0, 1]
        analysisData = [1, 2]
        analyticalData = [0, 0]
        self.assertRaises(ZeroDivisionError,
                          calcAreaDiff, angles, analysisData, analyticalData)


class TestContourAveraging(unittest.TestCase):

    def setUp(self):
        self.contEvenDict = {
            'cont_1': [5, 0, -5], 'cont_2': [1, 0, -1], 'cont_3': [9, 0, -9],
            'cont_4': [4, 0, -4], 'cont_5': [3, 0, -3], 'cont_6': [7, 0, -7]}
        self.contOddDict = {
            'cont_1': [5, 0, -5], 'cont_2': [1, 0, -1], 'cont_3': [9, 0, -9],
            'cont_4': [4, 0, -4], 'cont_5': [3, 0, -3]}

    def test_contourAveraging_with_even_number_contours_and_even_numCont(self):
        numCont = 4
        expected = [17.0 / 4., 0, -17.0 / 4.]
        for i in range(len(expected)):
            self.assertAlmostEqual(
                expected[i], contourAveraging(
                    self.contEvenDict, numCont)[i])

    def test_contourAveraging_with_even_number_contours_and_odd_numCont(self):
        numCont = 3
        expected = [14.0 / 3., 0, -14.0 / 3.]
        for i in range(len(expected)):
            self.assertAlmostEqual(
                expected[i], contourAveraging(
                    self.contEvenDict, numCont)[i])

    def test_contourAveraging_with_odd_number_contours_and_even_numCont(self):
        numCont = 4
        expected = [19.0 / 4., 0, -19.0 / 4.]
        for i in range(len(expected)):
            self.assertAlmostEqual(
                expected[i], contourAveraging(
                    self.contOddDict, numCont)[i])

    def test_contourAveraging_with_odd_number_contours_and_odd_numCont(self):
        numCont = 3
        expected = [14.0 / 3., 0, -14.0 / 3.]
        for i in range(len(expected)):
            self.assertAlmostEqual(
                expected[i], contourAveraging(
                    self.contOddDict, numCont)[i])

    def test_contourAveraging_with_even_number_contours_and_one_numCont(self):
        numCont = 1
        expected = [9., 0, -9.]
        for i in range(len(expected)):
            self.assertAlmostEqual(
                expected[i], contourAveraging(
                    self.contEvenDict, numCont)[i])

    def test_contourAveraging_with_odd_number_contours_and_one_numCont(self):
        numCont = 1
        expected = [9.0, 0, -9.0]
        for i in range(len(expected)):
            self.assertAlmostEqual(
                expected[i], contourAveraging(
                    self.contEvenDict, numCont)[i])

    def test_contourAveraging_with_even_number_contours_over_all_contours(
            self):
        numCont = len(self.contEvenDict.keys())
        expected = [29. / 6., 0, -29. / 6]
        for i in range(len(expected)):
            self.assertAlmostEqual(
                expected[i], contourAveraging(
                    self.contEvenDict, numCont)[i])

    def test_contourAveraging_with_odd_number_contours_over_all_contours(self):
        numCont = len(self.contOddDict.keys())
        expected = [22. / 5, 0, -22. / 5]
        for i in range(len(expected)):
            self.assertAlmostEqual(
                expected[i], contourAveraging(
                    self.contOddDict, numCont)[i])

    def test_contourAveraging_with_larger_numCont_than_contours(self):
        numCont = len(self.contEvenDict.keys()) + 1
        self.assertRaises(
            AssertionError, contourAveraging, self.contEvenDict, numCont)

    def test_contourAveraging_over_zero_contours(self):
        numCont = 0
        self.assertRaises(
            AssertionError, contourAveraging, self.contEvenDict, numCont)


class TestCalcErrors(unittest.TestCase):

    def test_calcErrors_with_vectors_of_equal_lengths(self):
        analysis = [
            -20, -5, 0, 5, 20,
            -20, -5, 0, 5, 20,
            -20, -5, 0, 5, 20]
        analytical = [
            -10, -10, -10, -10, -10,
            0, 0, 0, 0, 0,
            10, 10, 10, 10, 10]
        expected = [
            10, -5, -10, -5, 10,
            20, 5, 0, 5, 20,
            10, -5, -10, -5, 10]
        for i in range(len(expected)):
            self.assertAlmostEqual(expected[i],
                                   calcErrors(analytical, analysis)[i])

    def test_calcErrors_with_vectors_of_different_lengths(self):
        analysis = [1, 2, 3, 4, 5]
        analytical = [1, 2, 3]
        self.assertRaises(AssertionError, calcErrors, analytical, analysis)

    def test_calcErrors_with_multidimensional_arrays_with_equal_size(self):
        analysis = [[1, 2, 3], [1, 2, 3]]
        analytical = [[2, 3, 4], [4, 5, 6]]
        self.assertRaises(AssertionError, calcErrors, analytical, analysis)


class TestCalcDiffErrors(unittest.TestCase):
    pass


class TestCalcRMSD(unittest.TestCase):

    def test_calcRMSD_with_vectors_of_equal_length(self):
        analytical = [-5, -1, 1, 2, 3, 4, 5, 6]
        analysis = [-4, 2, -1, 0, 1, 2, 5, 9]
        expected = (35.0 / 8.0)**0.5
        self.assertAlmostEqual(expected, calcRMSD(analytical, analysis))

    def test_calcRMSD_with_vectors_of_different_length(self):
        analytical = [1, 2, 3, 4]
        analysis = [1, 2, 3]
        self.assertRaises(AssertionError, calcRMSD, analytical, analysis)

    def test_calcRMSD_with_arrays_of_different_size(self):
        analytical = [[1, 2], [4, 5]]
        analysis = [[1, 2, 3], [1, 2, 3]]
        self.assertRaises(AssertionError, calcRMSD, analytical, analysis)


class TestCalcNormErrors(unittest.TestCase):

    def setUp(self):
        self.domain = [0, 1, 2, 3, 4, 5]

    def test_calcNormErrors_with_analysis_dotProd_larger(self):
        analytical = [1, 2, 3, -4, -5, -6]
        analysis = [2, 1, -7, -1, -9, 3]
        #expected =   [1, -1, -10, 3, -4, 9]
        expected = [
            0.16666666, -0.166666666, -1.666666666, 0.5, -0.666666666, 1.5]
        result = calcNormErrors(analytical, analysis, self.domain, 'dotProd')
        self.assertEqual(1, result[1])
        for i in range(len(expected)):
            self.assertAlmostEqual(expected[i], result[0][i])

    def test_calcNormErrors_with_analytical_dotProd_larger(self):
        analysis = [1, 2, 3, -4, -5, -6]
        analytical = [2, 1, -7, -1, -9, 3]
        #expected =  [-1, 1, 10, -3,  4, -9]
        expected = [-0.111111111, 0.111111111,
                    1.11111111111, -0.333333333, 0.44444444, -1]
        result = calcNormErrors(analytical, analysis, self.domain, 'dotProd')
        self.assertEqual(-1, result[1])
        for i in range(len(expected)):
            self.assertAlmostEqual(expected[i], result[0][i])

    def test_calcNormErrors_with_analytical_areas_larger(self):
        analysis = [1, 2, 3, -4, -5, -6]
        analytical = [2, 1, -7, -1, -9, 3]
        #expected =  [-1, 1, 10, -3,  4, -9]
        expected = [-0.111111111, 0.111111111,
                    1.11111111111, -0.333333333, 0.44444444, -1]
        result = calcNormErrors(analytical, analysis, self.domain, 'areas')
        self.assertEqual(-1, result[1])
        for i in range(len(expected)):
            self.assertAlmostEqual(expected[i], result[0][i])

    def test_calcNormErrors_with_analysis_areas_larger(self):
        analytical = [1, 2, 3, -4, -5, -6]
        analysis = [2, 1, -7, -1, -9, 3]
        #expected =   [1, -1, -10, 3, -4, 9]
        expected = [
            0.16666666, -0.166666666, -1.666666666, 0.5, -0.666666666, 1.5]
        result = calcNormErrors(analytical, analysis, self.domain, 'areas')
        self.assertEqual(1, result[1])
        for i in range(len(expected)):
            self.assertAlmostEqual(expected[i], result[0][i])

    def test_calcNormErrors_with_unrecognized_eSignFactor(self):
        analytical = [1, 2, 3, -4, -5, -6]
        analysis = [2, 1, -7, -1, -9, 3]
        self.assertRaises(
            KeyError,
            calcNormErrors,
            analytical,
            analysis,
            self.domain,
            'unrecognized key')


class TestCalcAvgNormError(unittest.TestCase):

    def test_calcAvgNormError(self):
        domain = [0, 1, 2, 3, 4, 5]
        analysis = [1, 2, 3, -4, -5, -6]
        analytical = [2, 1, -7, -1, -9, 3]
        #expected =  [-1, 1, 10, -3,  4, -9]
        errors = [-0.111111111, 0.111111111,
                  1.11111111111, -0.333333333, 0.44444444, -1]
        expected = -3.1111111111 / float(len(domain))
        mock = MagicMock(return_value=(np.array(errors), -1))
        with patch(modulePath + 'calcNormErrors', mock):
            result = calcAvgNormError(analytical, analysis, domain, 'areas')
        self.assertAlmostEqual(expected, result)


class TestCalcMaxNormError(unittest.TestCase):

    def test_calcMaxNormError(self):
        domain = [0, 1, 2, 3, 4, 5]
        analysis = [1, 2, 3, -4, -5, -6]
        analytical = [2, 1, -7, -1, -9, 3]
        #expected =  [-1, 1, 10, -3,  4, -9]
        errors = [-0.111111111, 0.111111111,
                  1.11111111111, -0.333333333, 0.44444444, -1]
        mock = MagicMock(return_value=(errors, -1))
        with patch(modulePath + 'calcNormErrors', mock):
            result = calcMaxNormError(analytical, analysis, domain, 'areas')
        self.assertAlmostEqual(errors[2], result)


class TestCalcStatsWrapper(unittest.TestCase):

    def setUp(self):
        self.areaDiffMock = MagicMock(return_value='areaDiffMock')
        self.dpMock = MagicMock(return_value='dpMock')
        self.avgNErrMock = MagicMock(return_value='avgNErrMock')
        self.maxNErrMock = MagicMock(return_value='maxNErrMock')
        self.diffErrMock = MagicMock(return_value='diffErrMock')
        self.rmsdMock = MagicMock(return_value='rmsdMock')
        self.patches = [
            patch(modulePath + 'calcAreaDiff', self.areaDiffMock),
            patch(modulePath + 'calcDotProdDiff', self.dpMock),
            patch(modulePath + 'calcAvgNormError', self.avgNErrMock),
            patch(modulePath + 'calcMaxNormError', self.maxNErrMock),
            patch(modulePath + 'calcDiffErrors', self.diffErrMock),
            patch(modulePath + 'calcRMSD', self.rmsdMock)]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def test_calcStatsWrapper_with_nonexisting_statKey(self):
        self.assertRaises(KeyError, calcStatsWrapper, 'statkey',
                          'angles', 'analytical', 'analysis', 'areas')

    def test_calcStatsWrapper_with_areaDiff_statKey(self):
        self.assertEqual(
            'areaDiffMock',
            calcStatsWrapper(
                'areaDiff',
                'angles',
                'analytical',
                'analysis',
                'areas'))
        self.areaDiffMock.assert_called_once_with(
            angles='angles',
            analysisData='analysis',
            analyticalData='analytical')

    def test_calcStatsWrapper_with_dotProd_statKey(self):
        self.assertEqual(
            'dpMock',
            calcStatsWrapper(
                'dotProd',
                'angles',
                'analytical',
                'analysis',
                'areas'))
        self.dpMock.assert_called_once_with(analysisData='analysis',
                                            analyticalData='analytical')

    def test_calcStatsWrapper_with_avgNormError(self):
        self.assertEqual(
            'avgNErrMock',
            calcStatsWrapper(
                'avgNormError',
                'angles',
                'analytical',
                'analysis',
                'areas'))
        self.avgNErrMock.assert_called_once_with(
            analytical='analytical',
            analysis='analysis',
            domain='angles',
            eSignFactor='areas')

    def test_calcStatsWrapper_with_maxNormError_statKey(self):
        self.assertEqual(
            'maxNErrMock',
            calcStatsWrapper(
                'maxNormError',
                'angles',
                'analytical',
                'analysis',
                'areas'))
        self.maxNErrMock.assert_called_once_with(
            analytical='analytical',
            analysis='analysis',
            domain='angles',
            eSignFactor='areas')

    def test_calcStatsWrapper_with_difference_statKey(self):
        self.assertEqual(
            'diffErrMock',
            calcStatsWrapper(
                'difference',
                'angles',
                'analytical',
                'analysis',
                'areas'))
        self.diffErrMock.assert_called_once_with(analytical='analytical',
                                                 analysis='analysis')

    def test_calcStatsWrapper_with_rmsd_statKey(self):
        self.assertEqual(
            'rmsdMock',
            calcStatsWrapper(
                'rmsd',
                'angles',
                'analytical',
                'analysis',
                'areas'))
        self.rmsdMock.assert_called_once_with(analytical='analytical',
                                              analysis='analysis')
