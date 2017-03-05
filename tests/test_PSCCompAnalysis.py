import unittest
from mock import Mock, MagicMock, patch, call
from comp_analysis.PSCCompAnalysis import PSCCompAnalysis


class TestPSCCompAnalysis(unittest.TestCase):

    def setUp(self):
        self.simIds = [
            's80_50', 's80_80', 's80_100',
            's100_50', 's100_80', 's100_100',
            's120_50', 's120_80', 's120_100']
        self.psc = PSCCompAnalysis(self.simIds)

    def test_divideSimIds_with_all_dimension_combinations(self):
        adMock = MagicMock()
        adMock().getContainerDiam.side_effect = [
            80, 80, 80, 100, 100, 100, 120, 120, 120]
        adMock().getContainerHeight.side_effect = [
            50, 80, 100, 50, 80, 100, 50, 80, 100]
        adMock().getErrorReports.side_effect = [
            {'difference': {'K1': [111]}}, {'difference': {'K1': [122]}},
            {'difference': {'K1': [133]}}, {'difference': {'K1': [144]}},
            {'difference': {'K1': [155]}}, {'difference': {'K1': [166]}},
            {'difference': {'K1': [177]}}, {'difference': {'K1': [188]}},
            {'difference': {'K1': [199]}}]
        with patch('dataProcessing.AnalysisData', adMock):
            self.psc.divideSimIds(limD=100, limH=80)
        expSims = {
            'smaller': set([
                's80_50', 's80_80', 's80_100', 's100_50', 's120_50']),
            'equal': set([
                's100_80']),
            'larger': set([
                's100_100', 's120_80', 's120_100'])}
        self.assertEqual(expSims['smaller'], self.psc.simIds['smaller'])
        self.assertEqual(expSims['equal'], self.psc.simIds['equal'])
        self.assertEqual(expSims['larger'], self.psc.simIds['larger'])
        expErrs = {
            'smaller': [111, 122, 133, 144, 177],
            'equal': [155],
            'larger': [166, 188, 199]}
        self.assertEqual(expErrs['smaller'], list(self.psc.errs['smaller']))
        self.assertEqual(expErrs['equal'], list(self.psc.errs['equal']))
        self.assertEqual(expErrs['larger'], list(self.psc.errs['larger']))

    def test_delEmptySimIdClassificationSets(self):
        self.psc.simIds = {
            'smaller': set(['s80_50', 's80_80', 's100_50']),
            'equal': set(['s100_100']),
            'larger': set([])}
        self.psc.errs = {
            'smaller': [111, 122, 133, 144],
            'equal': [155], 'larger': []}
        self.psc.delEmptySimIdClassificationSets()
        expKeys = set(['smaller', 'equal'])
        self.assertEqual(expKeys, set(self.psc.simIds.keys()))
        self.assertEqual(expKeys, set(self.psc.errs.keys()))
        self.assertEqual([111, 122, 133, 144], self.psc.errs['smaller'])
        self.assertEqual([155], self.psc.errs['equal'])
        self.assertEqual(
            set(['s80_50', 's80_80', 's100_50']), self.psc.simIds['smaller'])
        self.assertEqual(set(['s100_100']), self.psc.simIds['equal'])

    def test_manipulateErrors(self):
        self.psc.errs = {
            'smaller': [50, 100, 150, 200, 300, 2000, -2000],
            'equal': [0, 50, -50, 30, -30, -1000, 1000]}
        self.psc.lim = 500
        self.psc.manipulateErrors()
        expErrs = {
            'smaller': [
                50, 100, 150, 200, 300], 'equal': [
                0, 50, -50, 30, -30]}
        self.assertEqual(expErrs, self.psc.errs)
