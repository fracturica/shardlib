import unittest
from mock import Mock, MagicMock, patch
from sessionFuncs import *
import tempfile
import os
import shelve
import time


class TestGetSessionDir(unittest.TestCase):

    def test_getSessionDir(self):
        mock = MagicMock(return_value=r'dataanalysis/shardlib')
        expected = r'dataanalysis/' + sessionDirName
        with patch('os.path.dirname', mock):
            result = getSessionDir()
        self.assertEqual(expected, result)


@patch('sessionFuncs.getSessionDir', Mock(
    return_value=r'dataanalysis/' + sessionDirName))
class TestGetShelvePath(unittest.TestCase):

    def test_getShelvePath_successful_simids(self):
        expected = r'dataanalysis/{0}/{1}'.format(sessionDirName, sShelveName)
        self.assertEqual(expected, getShelvePath('successful'))

    def test_getShelvePath_failed_simids(self):
        expected = r'dataanalysis/{0}/{1}'.format(sessionDirName, fShelveName)
        self.assertEqual(expected, getShelvePath('failed'))

    def test_getShelvePath_with_unrecognized_input(self):
        self.assertRaises(KeyError, getShelvePath, 'unrecognized arg')


class TestCreateNewSessionFiles(unittest.TestCase):

    def setUp(self):
        self.dbpath = tempfile.mkdtemp()
        self.backupMock = MagicMock()
        self.locTimeMock = MagicMock(return_value='_1')
        self.shelveMock = MagicMock()
        self.patchGetSess = patch(
            'sessionFuncs.getSessionDir',
            Mock(return_value=self.dbpath))
        self.patchBackup = patch('sessionFuncs.backupFile',
                                 self.backupMock)
        self.patchLocTime = patch('time.localtime', self.locTimeMock)
        self.patchShelve = patch(
            'sessionFuncs.createShelves',
            self.shelveMock)
        self.patchGetSess.start()
        self.patchBackup.start()
        self.patchLocTime.start()
        self.patchShelve.start()

    def tearDown(self):
        self.patchGetSess.stop()
        self.patchBackup.stop()
        self.patchLocTime.stop()
        self.patchShelve.stop()
        os.rmdir(self.dbpath)

    def test_createNewSessionFiles_with_True_arg_and_preexisting_files(self):
        sfilePath = os.path.join(self.dbpath, sShelveName)
        ffilePath = os.path.join(self.dbpath, fShelveName)
        ofilePath = os.path.join(self.dbpath, 'otherFile')
        sfile = shelve.open(sfilePath, 'c')
        sfile['path'] = sfilePath
        sfile.close()
        ffile = shelve.open(ffilePath, 'c')
        ffile['path'] = ffilePath
        ffile.close()
        ofile = shelve.open(ofilePath, 'c')
        ofile['path'] = ofilePath
        ofile.close()
        createNewSessionFiles(True)
        self.assertEqual(2, self.backupMock.call_count)
        self.backupMock.assert_any_call(self.dbpath, sShelveName, '_1')
        self.backupMock.assert_any_call(self.dbpath, fShelveName, '_1')
        self.shelveMock.assert_called_once_with()
        self.assertEqual(
            set(os.listdir(self.dbpath)),
            set([sShelveName, fShelveName, 'otherFile']))
        os.remove(sfilePath)
        os.remove(ffilePath)
        os.remove(ofilePath)

    def test_createNewSessionFiles_with_True_and_nonexisting_files(self):
        createNewSessionFiles(True)
        self.assertFalse(self.backupMock.called)
        self.shelveMock.assert_called_once_with()

    def test_createNewSessionFiled_with_False(self):
        createNewSessionFiles(False)
        self.assertFalse(self.backupMock.called)
        self.assertFalse(self.shelveMock.called)
        self.assertEqual([], os.listdir(self.dbpath))


class TestBackupFile(unittest.TestCase):

    def setUp(self):
        self.dbpath = tempfile.mkdtemp()

    def tearDown(self):
        os.rmdir(self.dbpath)

    def test_backupFile_with_dir_containing_multiple_files(self):
        filePath = os.path.join(self.dbpath, 'filename')
        otherFilePath = os.path.join(self.dbpath, 'other')
        with open(filePath, 'w') as f:
            f.write(filePath)
        with open(otherFilePath, 'w') as f:
            f.write(otherFilePath)
        timestamp = time.localtime()
        expectedFileName = '{0}_backup_{1}'.format(
            time.strftime('%d.%b.%Y %H:%M:%S', timestamp), 'filename')
        backupFile(self.dbpath, 'filename', timestamp)
        self.assertEqual(
            set([expectedFileName, 'other']), set(os.listdir(self.dbpath)))
        os.remove(os.path.join(self.dbpath, expectedFileName))
        os.remove(otherFilePath)

    def test_backupFile_with_dir_as_argument(self):
        os.mkdir(os.path.join(self.dbpath, 'empty_dir'))
        timestamp = time.localtime()
        self.assertRaises(AssertionError, backupFile,
                          self.dbpath, 'empty_dir', timestamp)
        os.rmdir(os.path.join(self.dbpath, 'empty_dir'))


class TestWriteToShelve(unittest.TestCase):

    def setUp(self):
        self.dbdir = tempfile.mkdtemp()
        self.dbpath = os.path.join(self.dbdir, 'tempshelve')
        db = shelve.open(self.dbpath)
        db[dataKey] = set([])
        db.close()
        self.shelveMock = MagicMock(return_value=self.dbpath)
        self.shelvePatch = patch(
            'sessionFuncs.getShelvePath',
            self.shelveMock)
        self.shelvePatch.start()

    def tearDown(self):
        self.shelvePatch.stop()
        os.remove(self.dbpath)
        os.rmdir(self.dbdir)

    def test_writeToShelve_with_empty_shelve_and_single_simid(self):
        simid = 'simid123'
        writeToShelve(simid, 'successful')
        db = shelve.open(self.dbpath)
        data = db[dataKey]
        db.close()
        self.assertEqual(data, set([simid]))
        self.shelveMock.assert_called_once_with('successful')

    def test_writeToShelve_with_nonempty_shelve_and_tuple_of_overlaping_simids(
            self):
        simids = ('simid123', 'simid234', 'simid345')
        dbset = set(['simid123', 'simid1'])
        db = shelve.open(self.dbpath)
        db[dataKey] = dbset
        db.close()
        writeToShelve(simids, 'failed')
        db = shelve.open(self.dbpath)
        keys = db[dataKey]
        db.close()
        expected = set(['simid123', 'simid234', 'simid345', 'simid1'])
        self.shelveMock.assert_called_once_with('failed')
        self.assertEqual(expected, keys)

    def test_writeToShelve_with_empty_set_argument(self):
        self.assertRaises(AssertionError, writeToShelve, set([]), 'failed')
        self.assertRaises(AssertionError, writeToShelve,
                          set(['', 'simid']), 'failed')

    def test_writeToShelve_with_empty_tuple_string_argument(self):
        self.assertRaises(AssertionError, writeToShelve, tuple(), 'failed')
        self.assertRaises(AssertionError, writeToShelve,
                          ('', 'simid'), 'failed')

    def test_writeToShelve_with_empty_list_argument(self):
        self.assertRaises(AssertionError, writeToShelve, [], 'failed')
        self.assertRaises(
            AssertionError, writeToShelve, [
                '', 'simid'], 'failed')

    def test_writeToShelve_with_empty_string_argument(self):
        self.assertRaises(AssertionError, writeToShelve, '', 'failed')


class TestAssignSimsAsFailed(unittest.TestCase):

    def setUp(self):
        self.treeMocks = []
        for i in range(3):
            self.treeMocks.append(MagicMock())
            self.treeMocks[i].getRootNode(
            ).assignMemberAsFailed.return_value = 1

    def test_assignSimsAsFailed(self):
        simIds = [1, 2, 3, 4]
        results = assignNodeSimsAsFailed(self.treeMocks, simIds)
        expected = (12, 3)
        self.assertEqual(expected, results)
        for mock in self.treeMocks:
            self.assertEqual(
                4, len(
                    mock.getRootNode().assignMemberAsFailed.mock_calls))
