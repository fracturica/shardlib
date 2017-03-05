import unittest
from mock import Mock, MagicMock, patch, call
import numpy as np
from dataProcessing import AnalysisData, AnalysisNodeData
from trees import TreeNode


class TestAnalysisData(unittest.TestCase):

    def setUp(self):
        self.ukey = 'unique_key'
        self.eSignFactor = 'eSignFactor'
        keys = set(['a',
                    'b',
                    'omega',
                    'gamma',
                    'sigma',
                    'h',
                    'd',
                    'E',
                    'v',
                    'material',
                    'crackType',
                    'crackRatio',
                    'analysisType',
                    'elements',
                    'modelType',
                    'transform',
                    'analysisSuccess',
                    'czrSeeds',
                    'crSeeds',
                    'czmSeeds',
                    'arcSeeds',
                    'allEdges',
                    'crackEdges'])
        self.data = {k: None for k in keys}
        keys = ['areaDiff', 'dotProd', 'difference', 'avgNormError',
                'maxNormError', 'rmsd']
        self.errors = {k: {} for k in keys}

    def test_contructor_with_arguments(self):
        with patch('dataProcessing.AnalysisData.extractDataFromDb') as mock:
            ad = AnalysisData(self.ukey, loadFromDb=False,
                              sifs=['K1', 'K2'], eSignFactor=self.eSignFactor)
            self.assertEqual(self.ukey, ad.uek)
            self.assertEqual(self.eSignFactor, ad.eSignFactor)
            self.assertEqual(self.data, ad.data)
            self.assertEqual(['K1', 'K2'], ad.sifs)
            self.assertEqual(self.errors, ad.errors)
            self.assertFalse(ad.calculatedErrors)
            self.assertEqual({}, ad.anSol)
            self.assertEqual({}, ad.results)
            self.assertEqual({}, ad.rawres)
            self.assertEqual([], ad.angles)
            self.assertFalse(mock.called)

    def test_constructor_with_default_arg_vals(self):
        with patch('dataProcessing.AnalysisData.extractDataFromDb') as extMock:
            ad = AnalysisData(self.ukey)
            self.assertEqual(['K1', 'K2', 'K3'], ad.sifs)
            self.assertEqual('areas', ad.eSignFactor)
            self.assertEqual(self.errors, ad.errors)
            self.assertFalse(ad.calculatedErrors)
            self.assertEqual({}, ad.anSol)
            self.assertEqual({}, ad.results)
            self.assertEqual({}, ad.rawres)
            self.assertEqual([], ad.angles)
            self.assertTrue(extMock.called)

    def test_calcAnSol_with_all_Kfactors(self):
        mock = MagicMock(side_effect=[1, 2, 3])
        with patch('anSol.calcAnSolWrapper', mock):
            ad = AnalysisData(
                self.ukey,
                sifs=[
                    'K1',
                    'K2',
                    'K3'],
                loadFromDb=False)
            ad.angles = [1, 2, 3]
            ad.data['a'] = 'a'
            ad.data['b'] = 'b'
            ad.data['v'] = 'v'
            ad.data['omega'] = 'omega'
            ad.data['gamma'] = 'gamma'
            ad.data['sigma'] = 'tenstress'
            ad.calcAnSol()
            self.assertEqual(1, ad.anSol['K1'])
            self.assertEqual(2, ad.anSol['K2'])
            self.assertEqual(3, ad.anSol['K3'])
            expectedCalls = [
                call(sifKey=sif, majorAxis='a', minorAxis='b',
                     v='v', betas=[1, 2, 3], gamma='gamma', omega='omega',
                     tensileStress='tenstress')
                for sif in ['K1', 'K2', 'K3']]
            self.assertEqual(expectedCalls, mock.call_args_list)

    def test_calcAnSol_with_one_Kfactor(self):
        mock = MagicMock(side_effect=[1, 2, 3])
        with patch('anSol.calcAnSolWrapper', mock):
            ad = AnalysisData(self.ukey, sifs=['K2'], loadFromDb=False)
            ad.angles = [1, 2, 3]
            ad.data['a'] = 'a'
            ad.data['b'] = 'b'
            ad.data['v'] = 'v'
            ad.data['omega'] = 'omega'
            ad.data['gamma'] = 'gamma'
            ad.data['sigma'] = 'tenstress'
            ad.calcAnSol()
            self.assertEqual(1, ad.anSol['K2'])
            self.assertEqual(['K2'], ad.anSol.keys())
            mock.assert_called_once_with(
                sifKey='K2', majorAxis='a', minorAxis='b',
                v='v', betas=[1, 2, 3], gamma='gamma', omega='omega',
                tensileStress='tenstress')

    def test_extractDataFromDb(self):
        entryMock = MagicMock(return_value=0)
        extractMock = MagicMock(return_value=1)
        patchEntry = patch('dbaccess.getEntryData',
                           entryMock)
        patchExtract = patch('dbaccess.extractDataFromEntry',
                             extractMock)
        patchEntry.start()
        patchExtract.start()
        sifs = ['K1', 'K2', 'K3']
        ad = AnalysisData(self.ukey, sifs=sifs, loadFromDb=True)
        self.assertFalse(ad.calculatedErrors)
        entryMock.assert_called_once_with(self.ukey)
        expectedExtractCalls = sifs + self.data.keys() + ['angles']
        for e in expectedExtractCalls:
            extractMock.assert_any_call(0, e)
        expectedExtractCalls = len(self.data.keys()) + len(sifs) + 1
        self.assertEqual(expectedExtractCalls, len(extractMock.mock_calls))
        expected = {k: 1 for k in self.data.keys()}
        self.assertEqual(expected, ad.data)
        expectedRawres = {sif: 1 for sif in sifs}
        self.assertEqual(expectedRawres, ad.rawres)
        self.assertEqual(1, ad.angles)
        patchEntry.stop()
        patchExtract.stop()

    def setup_calculateStats(self, sifs):
        self.contAvgMock = MagicMock(return_value='contAvgMock')
        self.statsMock = MagicMock(return_value='statsMock')
        self.patchContAvg = patch(
            'miscFuncs.contourAveraging', self.contAvgMock)
        self.patchStats = patch(
            'miscFuncs.calcStatsWrapper', self.statsMock)
        self.patchContAvg.start()
        self.patchStats.start()

    def teardown_calculateStats(self):
        self.patchContAvg.stop()
        self.patchStats.stop()

    def calculateStats_successfulAnalysis(self, sifs):
        self.setup_calculateStats(sifs)
        rawres = {s: {c: [] for c in ['c1', 'c2', 'c3']} for s in sifs}
        anSol = {s: [] for s in sifs}
        ad = AnalysisData(self.ukey, sifs=sifs, loadFromDb=False,
                          eSignFactor=self.eSignFactor)
        ad.data['analysisSuccess'] = True
        self.assertFalse(ad.calculatedErrors)
        ad.rawres = rawres
        ad.anSol = anSol
        ad.calculateStats()
        self.assertTrue(ad.calculatedErrors)
        expectedErrs = {e: {s: 'statsMock' for s in sifs} for e in self.errors}
        self.assertEqual(expectedErrs, ad.errors)
        expectedRes = {s: 'contAvgMock' for s in sifs}
        self.assertEqual(expectedRes, ad.results)
        self.assertEqual(len(sifs) * len(self.errors),
                         self.statsMock.call_count)
        self.assertEqual(len(sifs), self.contAvgMock.call_count)
        for s in sifs:
            self.contAvgMock.assert_any_call(rawres[s], len(rawres[s]) - 2)
            for e in self.errors:
                self.statsMock.assert_any_call(
                    statKey=e,
                    angles=[],
                    analytical=anSol[s],
                    analysis='contAvgMock',
                    eSign=self.eSignFactor)

        self.teardown_calculateStats()

    def test_calculateStats_with_all_Kfactors_successfulAnalysis(self):
        self.calculateStats_successfulAnalysis(['K1', 'K2', 'K3'])

    def test_calculateStats_with_K2_Kfactor_successfulAnalysis(self):
        self.calculateStats_successfulAnalysis(['K2'])

    def test_calculateStats_with_failedAnalysis(self):
        sifs = ['K1', 'K2', 'K3']
        self.setup_calculateStats(sifs)
        ad = AnalysisData(self.ukey, sifs=sifs, loadFromDb=False)
        ad.data['analysisSuccess'] = False
        ad.calculateStats()
        self.assertTrue(ad.calculatedErrors)
        self.assertFalse(self.contAvgMock.called)
        self.assertFalse(self.statsMock.called)
        self.teardown_calculateStats()

    def test_calculateStats_with_ZeroDevError(self):
        sifs = ['K2']
        csMock = MagicMock(side_effect=ZeroDivisionError)
        with patch('miscFuncs.contourAveraging') as cavgMock:
            with patch('miscFuncs.calcStatsWrapper', csMock):
                ad = AnalysisData(self.ukey, sifs=sifs, loadFromDb=False)
                ad.rawres = {'K2': {'cont1': [], 'cont2': []}}
                ad.anSol = {'K2': {'cont1': [], 'cont2': []}}
                ad.results = {'K2': {'cont1': [], 'cont2': []}}
                ad.data['analysisSuccess'] = True
                ad.calculateStats()
        self.assertEqual(self.errors.keys(), ad.errors.keys())
        for k in self.errors.keys():
            self.assertTrue(np.isnan(ad.errors[k]['K2']))
        expectedNumberCSMockCalls = len(sifs) * len(self.errors.keys())
        self.assertEqual(expectedNumberCSMockCalls, csMock.call_count)


class TestAnalysisNodeData(unittest.TestCase):

    def test_contructor_with_valid_input(self):
        an = AnalysisNodeData(
            node='node', sifs=[
                'K1', 'K3'], eSignFactor='areas')
        self.assertEqual('areas', an.eSignFactor)
        self.assertEqual(['K1', 'K3'], an.sifs)
        self.assertEqual('node', an.node)
        self.assertEqual([], list(an.angles))
        for s in ['K1', 'K3']:
            self.assertEqual(0, len(an.results[s]))
            self.assertEqual(0, len(an.anSol[s]))
        self.assertEqual(
            {
                'a': set(
                    []), 'b': set(
                    []), 'omega': set(
                    []), 'gamma': set(
                        []), 'sigma': set(
                            []), 'v': set(
                                [])}, an.anSolParams)
        self.assertEqual({}, an.errors)
        expEst = {'areaDiff': {}, 'dotProd': {}, 'avgNormError': {},
                  'maxNormError': {}, 'rmsd': {}}
        self.assertEqual(expEst, an.estimates)

    def test_constructor_with_invalid_eSignFactor(self):
        self.assertRaises(
            AssertionError,
            AnalysisNodeData,
            'node',
            ['K1'],
            'eSign')

    def test_sortDataByAnglesData(self):
        an = AnalysisNodeData(node='node', sifs=['K1'], eSignFactor='areas')
        an.angles = [2, 3, 1, 0]
        an.results['K1'] = [6, 7, 5, 4]
        an.anSol['K1'] = [9, 10, 8, 7]
        an.sortDataByAnglesData()
        self.assertEqual([0, 1, 2, 3], list(an.angles))
        self.assertEqual([4, 5, 6, 7], list(an.results['K1']))
        self.assertEqual([7, 8, 9, 10], list(an.anSol['K1']))

    def test_extractDataFromSims_with_nonempty_node(self):
        with patch('dataProcessing.AnalysisNodeData.extractDataFromSimId') as extrMock:
            with patch('trees.TreeNode.getSuccessfulMembers') as successMock:
                successMock.return_value = [1, 2, 3]
                an = AnalysisNodeData(TreeNode(''), ['K1'], 'areas')
                an.extractDataFromSims()
                successMock.assert_called_once_with()
                calls = [call(1), call(2), call(3)]
                self.assertEqual(calls, extrMock.mock_calls)

    def test_extractDataFromSimId(self):
        with patch('dataProcessing.AnalysisNodeData.extractAnSolParams') as ansolMock:
            with patch('dataProcessing.AnalysisData') as aMock:
                aMock().getAngles.return_value = [4, 5, 6]
                aMock().getResults.return_value = {
                    'K1': ['1r4', '1r5', '1r6'],
                    'K3': ['3r4', '3r5', '3r6']}
                aMock().getAnSol.return_value = {
                    'K1': ['1a4', '1a5', '1a6'],
                    'K3': ['3a4', '3a5', '3a6']}
                an = AnalysisNodeData('node', ['K1', 'K3'], 'areas')
                an.angles = [1, 2, 3]
                an.results = {'K1': ['1r1'], 'K2': ['2r1'], 'K3': ['3r1']}
                an.anSol = {'K1': ['1a1'], 'K2': ['2a1'], 'K3': ['3a1']}
                an.extractDataFromSimId('simId')
                expAngles = [1, 2, 3, 4, 5, 6]
                expResults = {
                    'K1': [
                        '1r1', '1r4', '1r5', '1r6'], 'K2': ['2r1'], 'K3': [
                        '3r1', '3r4', '3r5', '3r6']}
                expAnSol = {'K1': ['1a1', '1a4', '1a5', '1a6'], 'K2': ['2a1'],
                            'K3': ['3a1', '3a4', '3a5', '3a6']}
                self.assertEqual(expAngles, list(an.angles))
                for k in expResults.keys():
                    self.assertEqual(expResults[k], list(an.results[k]))
                    self.assertEqual(expAnSol[k], list(an.anSol[k]))

    def test_extractAnSolParams(self):
        adMock = MagicMock()
        params = {'a': 20, 'b': 10,
                  'omega': 60, 'gamma': 45, 'sigma': 100, 'v': 0.3}
        adMock.getAnSolParams.return_value = params
        an = AnalysisNodeData('node', ['K1', 'K3'], 'areas')
        an.extractAnSolParams(adMock)
        expParams = {
            'a': set(
                [20]), 'b': set(
                [10]), 'v': set(
                [0.3]), 'omega': set(
                    [60]), 'gamma': set(
                        [45]), 'sigma': set(
                            [100])}
        self.assertEqual(expParams, an.anSolParams)
        an.extractAnSolParams(adMock)
        self.assertEqual(expParams, an.anSolParams)
        params['a'] = 30
        expParams['a'] = set([20, 30])
        adMock = MagicMock()
        adMock.getAnSolParams.return_value = params
        an.extractAnSolParams(adMock)
        self.assertEqual(expParams, an.anSolParams)

    def test_verifyAnSolParams_with_sets_of_unit_length(self):
        an = AnalysisNodeData('node', ['K1', 'K2'], 'areas')
        an.anSolParams = {
            'a': set(
                ['2']), 'b': set(
                ['1']), 'v': set(
                ['0.3']), 'omega': set(
                    ['60']), 'gamma': set(
                        ['45']), 'sigma': set(
                            ['100'])}
        an.verifyAnSolParams()
        expected = {'a': 2, 'b': 1, 'v': 0.3,
                    'omega': 60, 'gamma': 45, 'sigma': 100}
        self.assertEqual(expected, an.anSolParams)

    def test_verifyAnSolParams_with_sets_of_multiple_length(self):
        an = AnalysisNodeData('node', ['K1', 'K2'], 'areas')
        an.anSolParams = {
            'a': set(['2', '3']), 'b': set(['1', '2', '3']), 'v': set(['0.3']),
            'omega': set(['60']), 'gamma': set(['45']), 'sigma': set(['100'])}
        self.assertRaises(AssertionError, an.verifyAnSolParams)

    def test_calcErrors(self):
        diffMock = MagicMock(return_value=1)
        with patch('miscFuncs.calcDiffErrors', diffMock):
            an = AnalysisNodeData('node', ['K1', 'K2'], 'areas')
            an.results = {'K1': ['1r1', '1r2'], 'K2': ['2r1', '2r2']}
            an.anSol = {'K1': ['1a1', '1a2'], 'K2': ['2a1', '2a2']}
            an.calcErrors()
        diffMock.assert_any_call(['1a1', '1a2'], ['1r1', '1r2'])
        diffMock.assert_any_call(['2a1', '2a2'], ['2r1', '2r2'])
        self.assertEqual(2, diffMock.call_count)
        expected = {'difference': {'K1': 1, 'K2': 1}, 'normedDiff': {}}

    def test_calcEstimates_with_nonzero_analytical_solutions(self):
        wrMock = MagicMock(return_value=1)
        with patch('miscFuncs.calcStatsWrapper', wrMock):
            an = AnalysisNodeData('node', ['K1', 'K3'], 'areas')
            an.angles = [1, 2]
            an.anSol = {'K1': [1, 2], 'K3': [1, 2]}
            an.results = {'K1': [1, 2], 'K3': [1, 2]}
            an.calcEstimates()
        expected = {e: {'K1': 1, 'K3': 1} for e in [
            'areaDiff', 'dotProd', 'avgNormError', 'maxNormError', 'rmsd']}
        self.assertEqual(expected, an.estimates)

    def test_calcEstimates_with_ZeroDivisionError(self):
        wrMock = MagicMock(side_effect=ZeroDivisionError)
        with patch('miscFuncs.calcStatsWrapper', wrMock):
            an = AnalysisNodeData('node', ['K1'], 'areas')
            an.angles = [1, 2]
            an.anSol = {'K1': [1, 2]}
            an.results = {'K1': [1, 2]}
            an.calcEstimates()
        errs = ['areaDiff', 'dotProd', 'avgNormError', 'maxNormError', 'rmsd']
        for e in errs:
            self.assertTrue(np.isnan(an.estimates[e]['K1']))

    def test_fixAngleValues(self):
        an = AnalysisNodeData('node', ['K1'], 'areas')
        an.angles = np.array([1, 4, 90, 120, 90, 340, 380, 720])
        an.fixAngleValues()
        exp = [1, 4, 90, 120, 90, 340, 20, 0]
        self.assertEqual(exp, list(an.angles))

    def test_calcSIFsForSigmaAndSIF(self):
        an = AnalysisNodeData('node', ['K1'], 'areas')
        an.anSolParams = {'a': 20, 'b': 10, 'v': 0.3, 'gamma': 45, 'omega': 60}
        an.angles = [30, 45]
        aMock = MagicMock(return_value=123)
        with patch('anSol.calcAnSolWrapper', aMock):
            res = an.calcSIFsForSigmaAndSIF(100, 'K2')
        self.assertEqual(123, res)
        aMock.assert_called_once_with(
            sifKey='K2', majorAxis=20, minorAxis=10, v=0.3,
            betas=[30, 45], gamma=45, omega=60, tensileStress=100)
