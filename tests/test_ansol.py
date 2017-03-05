from math import pi
import unittest
from mock import Mock, MagicMock, patch
from anSol import calcK, calcR, calcQ, calcStresses, calcK1, calcK2, calcK3, calcAnSolWrapper

modulePrefix = 'anSol.'


class TestCalcK(unittest.TestCase):

    def test_calcK_with_invalid_axes_values(self):
        axes = [(-10, -5), (-1, -2), (-1, 2), (0, -2), (0, 2), (0, 0), (2, 3)]
        for a, b in axes:
            self.assertRaises(AssertionError, calcK, a, b)

    def test_calcK_with_valid_axes_values(self):
        axes = [(2, 1), (1, 1), (2, 2), (10, 1)]
        kVals = [0.866025403, 0, 0, 0.994987437]
        for (a, b), k in zip(axes, kVals):
            self.assertAlmostEqual(k, calcK(a, b))


class TestCalcR(unittest.TestCase):

    def test_calcR_with_invalid_v_and_valid_k(self):
        k = 0.5
        for v in [-2, -1, -0.5, 0, 0.51, 1]:
            self.assertRaises(AssertionError, calcR, k, v)

    def test_calcR_with_valid_v_and_invalid_k(self):
        v = 0.3
        for k in [-1, -0.1, 1, 2]:
            self.assertRaises(AssertionError, calcR, k, v)

    def test_calcR_with_valid_v_and_nonzero_k(self):
        kv = [(0.1, 0.5), (0.5, 0.5), (0.9, 0.5),
              (0.1, 0.3), (0.5, 0.3), (0.9, 0.3)]
        res = [0.20795543698, 0.6990718462014841, 1.3789606608181639,
               0.28591552229, 0.71503219085390219, 1.1402245888836]
        for (k, v), r in zip(kv, res):
            self.assertAlmostEqual(r, calcR(k, v))

    def test_calcR_with_valid_v_and_zero_k(self):
        v = 0.3
        k = 0.0
        exp = 2.0 / (pi * (1 - v))
        self.assertAlmostEqual(exp, calcR(k, v))


class TestCalcQ(unittest.TestCase):

    def test_calcQ_with_invalid_v_and_valid_k(self):
        k = 0.5
        for v in [-2, -1, -0.5, 0, 0.51, 1]:
            self.assertRaises(AssertionError, calcQ, k, v)

    def test_calcQ_with_valid_v_and_invalid_k(self):
        v = 0.3
        for k in [-1, -0.1, 1, 2]:
            self.assertRaises(AssertionError, calcQ, k, v)

    def test_calcQ_with_valid_v_and_nonzero_k(self):
        kv = [(0.1, 0.5), (0.5, 0.5), (0.9, 0.5),
              (0.1, 0.3), (0.5, 0.3), (0.9, 0.3)]
        res = [-0.3979963117, 1.67926764853912, 1.07298641382068,
               -1.1170081642, 1.11413640688092, 0.998904358791297]
        for (k, v), r in zip(kv, res):
            self.assertAlmostEqual(r, calcQ(k, v))

    def test_calcQ_with_valid_v_and_zero_k(self):
        v = 0.3
        k = 0.0
        exp = 2.0 / pi
        self.assertAlmostEqual(exp, calcQ(k, v))


class TestCalcStresses(unittest.TestCase):

    def test_calcStresses_with_gamma_less_or_equal_to_90_degrees(self):
        s_a = [(100, 0), (100, 30), (100, 60), (100, 90)]
        res = [(100, 0), (75, 43.301270189), (25, 43.301270189), (0, 0)]
        for (stress, gamma), (exp_sigma, exp_tao) in zip(s_a, res):
            sigma, tao = calcStresses(stress, gamma)
            self.assertAlmostEqual(exp_sigma, sigma)
            self.assertAlmostEqual(exp_tao, tao)

    def test_calcStresses_with_gamma_larger_than_or_equal_to_360_degrees(self):
        s_a = [(100, 360), (100, 390), (100, 420), (100, 450)]
        res = [(100, 0), (75, 43.301270189), (25, 43.301270189), (0, 0)]
        for (stress, gamma), (exp_sigma, exp_tao) in zip(s_a, res):
            sigma, tao = calcStresses(stress, gamma)
            self.assertAlmostEqual(exp_sigma, sigma)
            self.assertAlmostEqual(exp_tao, tao)

    def test_calcStress_with_gamma_larger_than_90_or_less_than_0(self):
        s_a = [(100, -10), (100, 130), (100, 200), (100, 350)]
        for sigma, gamma in s_a:
            self.assertRaises(AssertionError, calcStresses, sigma, gamma)


class TestCalcK1(unittest.TestCase):

    def test_calcK1_with_a20_b10_sigma100(self):
        a, b = 20, 10
        betas = [0, 60, 90,
                 120, 180, 240,
                 270, 300, 360]
        sigma = 100
        expected = [247.6864593064, 345.116280255875, 350.28154996732,
                    345.116280255875, 247.6864593064, 345.11628025587532,
                    350.28154996732, 345.116280255875, 247.6864593064754]
        for beta, k1 in zip(betas, expected):
            self.assertAlmostEqual(k1, calcK1(a, b, beta, sigma))

    def test_calcK1_with_a20_b20_sigma100(self):
        a, b = 20, 20
        sigma = 100
        betas = [0, 60, 90, 180, 240, 300, 360, 400]
        expected = 356.82482323055
        for beta in betas:
            self.assertAlmostEqual(expected, calcK1(a, b, beta, sigma))

    def test_calcK1_with_a10_b20_sigma100(self):
        a, b = 10, 20
        betas = [0, 60, 90, 180, 240, 300, 360, 400]
        sigma = 100
        for beta in betas:
            self.assertRaises(AssertionError, calcK1, a, b, beta, sigma)

    def test_calcK1_with_a20_b10_sigma0(self):
        a, b = 20, 20
        betas = [0, 60, 90, 180, 240, 300, 360, 400]
        sigma = 0
        for beta in betas:
            self.assertAlmostEqual(0, calcK1(a, b, beta, sigma))


class TestCalcK2(unittest.TestCase):

    def setUp(self):
        self.v = 0.3
        self.tao = 100
        self.beta = 45
        self.omega = 60

    def test_calcK2_with_a20_b10_tao100(self):
        a, b = 20, 10
        betas = [0, 60, 90,
                 180, 240, 300,
                 360, 400]
        expected = [-151.81193289, -364.761525373456, -343.0689272125,
                    151.81193289, 364.761525373456, 304.324782974556,
                    -151.81193289388983, -369.32377154114926]
        for beta, k2 in zip(betas, expected):
            self.assertAlmostEqual(
                k2,
                calcK2(
                    a,
                    b,
                    self.v,
                    beta,
                    self.omega,
                    self.tao))

    def test_calcK2_with_a20_b20_tao100(self):
        a, b = 20, 20
        expected = -398.73343769
        self.assertAlmostEqual(
            expected,
            calcK2(
                a,
                b,
                self.v,
                self.beta,
                self.omega,
                self.tao))

    def test_calcK2_with_a20_b10_tao0(self):
        a, b = 20, 10
        tao = 0
        expected = 0
        self.assertAlmostEqual(
            expected,
            calcK2(
                a,
                b,
                self.v,
                self.beta,
                self.omega,
                tao))

    def test_calcK2_with_a10_b20_tao100(self):
        a, b = 10, 20
        self.assertRaises(AssertionError, calcK2,
                          a, b, self.v, self.beta, self.omega, self.tao)


class TestCalcK3(unittest.TestCase):

    def setUp(self):
        self.v = 0.3
        self.tao = 100
        self.beta = 45
        self.omega = 60

    def test_calcK3_with_a20_b10_tao100(self):
        a, b = 20, 10
        betas = [0, 60, 90,
                 180, 240, 300,
                 360, 400]
        expected = [-169.8104553924517, 112.75031034975231, 150.28614610002944,
                    169.81045539245176, -112.7503103497523, -180.35231339102046,
                    -169.81045539245181, 71.441969172512316]
        for beta, k2 in zip(betas, expected):
            self.assertAlmostEqual(
                k2,
                calcK3(
                    a,
                    b,
                    self.v,
                    beta,
                    self.omega,
                    self.tao))

    def test_calcK3_with_a20_b20_tao100(self):
        a, b = 20, 20
        expected = -26.80015418
        self.assertAlmostEqual(
            expected,
            calcK3(
                a,
                b,
                self.v,
                self.beta,
                self.omega,
                self.tao))

    def test_calcK3_with_a20_b10_tao0(self):
        a, b = 20, 10
        tao = 0
        expected = 0
        self.assertAlmostEqual(
            expected,
            calcK3(
                a,
                b,
                self.v,
                self.beta,
                self.omega,
                tao))

    def test_calcK3_with_a10_b20_tao100(self):
        a, b = 10, 20
        self.assertRaises(AssertionError, calcK3,
                          a, b, self.v, self.beta, self.omega, self.tao)


class TestCalcAnSolWrapper(unittest.TestCase):

    def setUp(self):
        self.betas = ['a', 'b', 'c']
        self.mockK1 = MagicMock(return_value=1)
        self.mockK2 = MagicMock(return_value=2)
        self.mockK3 = MagicMock(return_value=3)
        self.mockStr = MagicMock(return_value=('sigma', 'tao'))
        self.patches = [
            patch(modulePrefix + 'calcK1', self.mockK1),
            patch(modulePrefix + 'calcK2', self.mockK2),
            patch(modulePrefix + 'calcK3', self.mockK3),
            patch(modulePrefix + 'calcStresses', self.mockStr)]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def test_calcAnSolWrapper_with_K1_sifKey(self):
        res = calcAnSolWrapper('K1', 'a', 'b', 'v', self.betas,
                               'gamma', 'omega', 'stress')
        self.mockStr.assert_called_once_with(
            tensileStress='stress', gamma='gamma')
        self.assertEqual(len(self.betas), self.mockK1.call_count)
        self.assertEqual(len(self.betas) * [1], res)
        for beta in self.betas:
            self.mockK1.assert_any_call(axisA='a', axisB='b',
                                        beta=beta, sigma='sigma')

    def test_calcAnSolWrapper_with_K2_sifKey(self):
        res = calcAnSolWrapper('K2', 'a', 'b', 'v', self.betas,
                               'gamma', 'omega', 'stress')
        self.mockStr.assert_called_once_with(
            tensileStress='stress', gamma='gamma')
        self.assertEqual(len(self.betas), self.mockK2.call_count)
        self.assertEqual(len(self.betas) * [2], res)
        for beta in self.betas:
            self.mockK2.assert_any_call(axisA='a', axisB='b', v='v',
                                        beta=beta, omega='omega', tao='tao')

    def test_calcAnSolWrapper_with_K3_sifKey(self):
        res = calcAnSolWrapper('K3', 'a', 'b', 'v', self.betas,
                               'gamma', 'omega', 'stress')
        self.mockStr.assert_called_once_with(
            tensileStress='stress', gamma='gamma')
        self.assertEqual(len(self.betas), self.mockK3.call_count)
        self.assertEqual(len(self.betas) * [3], res)
        for beta in self.betas:
            self.mockK3.assert_any_call(axisA='a', axisB='b', v='v',
                                        beta=beta, omega='omega', tao='tao')

    def test_calcAnSolWrapper_with_undefined_sifKey(self):
        self.assertRaises(
            KeyError,
            calcAnSolWrapper,
            'unknown_sifKey',
            'a',
            'b',
            'v',
            self.betas,
            'gamma',
            'omega',
            'stress')
