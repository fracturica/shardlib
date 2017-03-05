import dbaccess as dba
import unittest
from mock import Mock, MagicMock, patch
import tempfile
import os


@patch('os.path.abspath', MagicMock(
    return_value=r'parentdir/dataanalysis/shardlib/dbaccess.py'))
class TestGetDbRepoDir(unittest.TestCase):

    def test_with_no_db_dir(self):
        mock = MagicMock(side_effect=[False, False])
        with patch('os.path.exists', mock):
            self.assertRaises(IOError, dba.getDbRepoDir)

    def test_with_db_in_first_parent_dir(self):
        expected = r'parentdir/dataanalysis/db'
        mock = MagicMock(side_effect=[True, False])
        with patch('os.path.exists', mock):
            result = dba.getDbRepoDir()
        self.assertEqual(expected, result)

    def test_with_db_in_second_parent_dir(self):
        expected = r'parentdir/db'
        mock = MagicMock(side_effect=[False, True])
        with patch('os.path.exists', mock):
            result = dba.getDbRepoDir()
        self.assertEqual(expected, result)


class TestCheckIfValidShelvePath(unittest.TestCase):

    def setUp(self):
        self.dbRepoPath = tempfile.mkdtemp()
        self.dbname = 'dbname'
        self.patcher = patch(
            'dbaccess.getDbRepoDir',
            MagicMock(return_value=self.dbRepoPath))
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        os.rmdir(self.dbRepoPath)

    def test_with_dbname_without_matching_directory(self):
        self.assertFalse(dba.checkIfValidShelvePath(self.dbname))

    def test_with_dbname_without_results_directory(self):
        dbpath = os.path.join(self.dbRepoPath, self.dbname)
        os.mkdir(dbpath)
        self.assertFalse(dba.checkIfValidShelvePath(self.dbname))
        os.rmdir(dbpath)

    def test_with_dbname_without_shelve_file(self):
        dbpath = os.path.join(self.dbRepoPath, self.dbname)
        os.mkdir(dbpath)
        respath = os.path.join(dbpath, dba.resultsDb)
        os.mkdir(respath)
        self.assertFalse(dba.checkIfValidShelvePath(self.dbname))
        os.rmdir(respath)
        os.rmdir(dbpath)

    def test_with_valid_db_directory_structure(self):
        dbpath = os.path.join(self.dbRepoPath, self.dbname)
        os.mkdir(dbpath)
        respath = os.path.join(dbpath, dba.resultsDb)
        os.mkdir(respath)
        filepath = os.path.join(respath, self.dbname)
        with open(filepath, 'w') as f:
            f.write(self.dbRepoPath)
        self.assertTrue(dba.checkIfValidShelvePath(self.dbname))
        os.remove(filepath)
        os.rmdir(respath)
        os.rmdir(dbpath)


class TestFilterDbKeys(unittest.TestCase):

    def test_filterDbKeys_on_passing_and_nonpassing_keys(self):
        keys = ['abc$12345', 'dcf$metadata', 'efg$sample', 'hij$dummy']
        self.assertEqual(
            set(['abc$12345', 'efg$sample', 'hij$dummy']),
            dba.filterDbKeys(keys))


class TestGetDbKeysFromSubset(unittest.TestCase):

    def test_getDbKeysFromSubset(self):
        subset = {
            '1$1', '1$2', '1$3',
            '2$a', '2$b', '2$c', '2$d',
            '3$a', '3$b'}
        expected = {
            '1': {'1', '2', '3'},
            '2': {'a', 'b', 'c', 'd'},
            '3': {'a', 'b'}}
        result = dba.getDbKeysFromSubset(subset)
        self.assertEqual(expected, dba.getDbKeysFromSubset(subset))


class TestGetSubsetByCriterion(unittest.TestCase):

    def setUp(self):
        self.patchedFunc = 'dbaccess.extractSimIdParamValuesFromSubset'
        self.crit = 2
        self.param = 'parameter'

    def test_getSubsetByCriterion_empty_dict(self):
        mock = MagicMock(return_value={})
        with patch(self.patchedFunc, mock):
            expected = set([])
            result = dba.getSubsetByCriterion(set([]), self.param, self.crit)
        self.assertEqual(expected, result)

    def test_getSubsetByCriterion_nonempty_dict(self):
        mock = MagicMock(return_value={'1$a': 1, '1$b': 2, '1$c': 3, '2$a': 2})
        with patch(self.patchedFunc, mock):
            expected = set(['1$b', '2$a'])
            result = dba.getSubsetByCriterion(set([]), self.param, self.crit)
        self.assertEqual(expected, result)


class TestGetParameterRange(unittest.TestCase):

    def setUp(self):
        self.patchedFunc = 'dbaccess.extractSimIdParamValuesFromSubset'
        self.param = 'parameter'

    def test_getParameterRange_with_empty_dict(self):
        mock = MagicMock(return_value={})
        with patch(self.patchedFunc, mock):
            expected = set([])
            result = dba.getParameterRange(set([]), self.param)
        self.assertEqual(expected, result)

    def test_getParameterRange_with_nonempty_dict(self):
        mock = MagicMock(
            return_value={
                '1$a': 1,
                '1$b': 2,
                '1$c': 3,
                '2$c': 9,
                '2$d': 2})
        with patch(self.patchedFunc, mock):
            expected = set([1, 2, 3, 9])
            result = dba.getParameterRange(set([]), self.param)
        self.assertEqual(expected, result)
