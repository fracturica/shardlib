from unittest import TestCase
from mock import Mock, MagicMock, patch
from queues import CompQueue


class TestCompQueue(TestCase):

    def setUp(self):
        self.cq = CompQueue()

    def test_constructor(self):
        self.assertEqual(self.cq.queue, set([]))

    def test_addSimId_string(self):
        self.cq.addSimId('simid')
        self.cq.addSimId('simid')
        self.assertEqual(self.cq.queue, set(['simid']))
        self.cq.addSimId('simid1')
        self.assertEqual(self.cq.queue, set(['simid', 'simid1']))
        self.assertFalse(self.cq.updated)

    def test_addSimId_list_without_duplicate_elements(self):
        simids = ['simid1', 'simid2', 'simid3']
        self.cq.addSimId(simids)
        self.assertEqual(self.cq.queue, set(simids))
        self.assertFalse(self.cq.updated)

    def test_addSimId_list_with_duplicate_elements(self):
        simids = ['simid1', 'simid1', 'simid2']
        self.cq.addSimId(simids)
        self.assertEqual(self.cq.queue, set(simids))
        self.assertFalse(self.cq.updated)

    def test_addSimId_list_with_duplicates(self):
        simids = ['simid1', 'simid2', 'simid3']
        self.cq.addSimId('simid1')
        self.cq.addSimId(simids)
        self.assertEqual(self.cq.queue, set(simids))
        self.assertFalse(self.cq.updated)

    def test_addSimId_list_without_duplicates(self):
        simids = ['simid1', 'simid2']
        self.cq.addSimId('simid3')
        self.cq.addSimId(simids)
        self.assertEqual(self.cq.queue, set(['simid1', 'simid2', 'simid3']))
        self.assertFalse(self.cq.updated)

    def test_addSimId_frozenset(self):
        simids = frozenset(['simid1', 'simid2', 'simid3'])
        self.cq.addSimId(simids)
        self.assertEqual(self.cq.queue, set(['simid1', 'simid2', 'simid3']))
        self.assertFalse(self.cq.updated)

    def test_addSimId_frozenset_to_existing_queue(self):
        simids = frozenset(['simid1', 'simid2'])
        self.cq.addSimId('simid3')
        self.cq.addSimId(simids)
        self.assertEqual(self.cq.queue, set(['simid1', 'simid2', 'simid3']))
        self.assertFalse(self.cq.updated)

    def test_addSimId_with_invalid_argument_type(self):
        for arg in [1, 1.1]:
            self.assertRaises(TypeError, self.cq.addSimId, arg)

    def test_getQueue_empty_queue(self):
        self.assertEqual(self.cq.getQueue(), [])

    def test_getQueue_nonempty_queue(self):
        self.add_simids_to_queue()
        self.assertEqual(self.cq.getQueue(), ['simid1', 'simid2', 'simid3'])

    def test_getByNumber_with_invalid_argument_type(self):
        self.add_simids_to_queue()
        self.cq.updated = True
        for num in ['o', 1.2, [], (), set([]), {}]:
            self.assertTrue(self.cq.updated)
            self.assertRaises(AssertionError, self.cq.getByNumber, num)

    def test_getByNumber_with_outdated_queue(self):
        self.add_simids_to_queue()
        self.assertFalse(self.cq.updated)
        self.assertRaises(AssertionError, self.cq.getByNumber, 2)

    def test_getByNumber_with_empty_queue(self):
        self.cq.updated = True
        self.assertRaises(AssertionError, self.cq.getByNumber, 0)

    def test_getByNumber_with_out_of_range_index(self):
        self.add_simids_to_queue()
        self.cq.updated = True
        for num in [-20, -1, 0, 4, 10]:
            self.assertRaises(AssertionError, self.cq.getByNumber, num)

    def test_getByNumber_with_valid_arguments(self):
        self.add_simids_to_queue()
        self.cq.updated = True
        self.assertEqual('simid1', self.cq.getByNumber(1))
        self.assertEqual('simid2', self.cq.getByNumber(2))
        self.assertEqual('simid3', self.cq.getByNumber(3))

    def test_getQueueDict_on_empty_queue(self):
        self.assertEqual({}, self.cq.getQueueDict())

    def test_getQueueDict_on_outdated_queue(self):
        self.add_simids_to_queue()
        self.assertRaises(AssertionError, self.cq.getQueueDict)

    def test_getQueueDict_on_updated_queue(self):
        self.add_simids_to_queue()
        self.cq.updated = True
        self.assertEqual(
            {1: 'simid1', 2: 'simid2', 3: 'simid3'}, self.cq.getQueueDict())

    def add_simids_to_queue(self):
        simids = ['simid3', 'simid1', 'simid2', 'simid2']
        self.cq.addSimId(simids)

    def test_removeFromQueue_with_None(self):
        self.add_simids_to_queue()
        self.cq.removeFromQueue(None)
        self.assertEqual({'simid1', 'simid2', 'simid3'}, self.cq.queue)

    def test_removeFromQueue_with_invalid_arguments(self):
        self.add_simids_to_queue()
        self.cq.updated = True
        for ind in ['o', 1.2, [], (), set([]), {}]:
            self.assertRaises(AssertionError, self.cq.removeFromQueue, ind)
            self.assertEqual({'simid1', 'simid2', 'simid3'}, self.cq.queue)

    def test_removeFromQueue_with_valid_argument_and_oudated_queue(self):
        self.add_simids_to_queue()
        for ind in [1, 2, 3]:
            self.assertRaises(AssertionError, self.cq.removeFromQueue, ind)

    def test_removeFromQueue_with_valid_argument_and_updated_queue(self):
        self.add_simids_to_queue()
        self.cq.updated = True
        self.cq.removeFromQueue(3)
        self.assertEqual({'simid1', 'simid2'}, self.cq.queue)
        self.assertFalse(self.cq.updated)
        self.cq.updated = True
        self.cq.removeFromQueue(1)
        self.assertEqual({'simid2'}, self.cq.queue)
        self.assertFalse(self.cq.updated)
        self.cq.updated = True
        self.cq.removeFromQueue(1)
        self.assertEqual(set([]), self.cq.queue)
        self.assertFalse(self.cq.updated)

    def test_removeSimIdFromQueue_with_None_argument(self):
        self.add_simids_to_queue()
        self.cq.updated = True
        self.cq.removeSimIdFromQueue(None)
        self.assertEqual(set(['simid1', 'simid2', 'simid3']), self.cq.queue)
        self.assertTrue(self.cq.updated)

    def test_removeSimIdFromQueue_with_invalid_arguments(self):
        self.add_simids_to_queue()
        self.cq.updated = True
        for s in [(), [], {}, set([]), 1, 1.0]:
            self.assertRaises(AssertionError, self.cq.removeSimIdFromQueue, s)
            self.assertEqual({'simid1', 'simid2', 'simid3'}, self.cq.queue)
            self.assertTrue(self.cq.updated)

    def test_removeSimIdFromQueue_with_valid_argument_not_in_queue(self):
        self.add_simids_to_queue()
        self.cq.updated = True
        self.cq.removeSimIdFromQueue('simid4')
        self.assertEqual({'simid1', 'simid2', 'simid3'}, self.cq.queue)
        self.assertTrue(self.cq.updated)

    def test_removeSimIdFromQueue_with_valid_argument_in_updated_queue(self):
        self.add_simids_to_queue()
        self.cq.updated = True
        self.cq.removeSimIdFromQueue('simid1')
        self.assertEqual({'simid2', 'simid3'}, self.cq.queue)
        self.assertFalse(self.cq.updated)

    def test_removeSimIdFromQueue_with_valid_argument_in_outdated_queue(self):
        self.add_simids_to_queue()
        self.cq.updated = False
        self.cq.removeSimIdFromQueue('simid1')
        self.assertEqual({'simid2', 'simid3'}, self.cq.queue)
        self.assertFalse(self.cq.updated)

    def test_loadSession_on_empty_queue_with_disjoint_node_and_session(self):
        nodeMock = MagicMock()
        nodeMock.getSuccessfulMembers.return_value = set(['simid1', 'simid2'])
        self.cq.updated = True
        with patch('sessionFuncs.getSimIdsFromShelve') as sfsm:
            sfsm.return_value = set(['simid3', 'simid4'])
            self.cq.loadSession(nodeMock)
        sfsm.assert_called_once_with('successful')
        nodeMock.getSuccessfulMembers.assert_called_once_with()
        assert nodeMock.getSuccessfulMembers() == set(['simid1', 'simid2'])
        self.assertEqual(set([]), self.cq.queue)
        self.assertFalse(self.cq.updated)

    def test_loadSession_on_empty_queue_with_node_a_subset_of_session(self):
        nodeMock = MagicMock()
        nodeMock.getSuccessfulMembers.return_value = set(['simid1'])
        self.cq.updated = True
        with patch('sessionFuncs.getSimIdsFromShelve') as sfsm:
            sfsm.return_value = set(['simid1', 'simid2'])
            self.cq.loadSession(nodeMock)
        sfsm.assert_called_once_with('successful')
        nodeMock.getSuccessfulMembers.assert_called_once_with()
        assert nodeMock.getSuccessfulMembers() == set(['simid1'])
        self.assertEqual(set(['simid1']), self.cq.queue)
        self.assertFalse(self.cq.updated)

    def test_loadSession_on_nonempty_queue_with_node_a_subset_of_session(self):
        nodeMock = MagicMock()
        nodeMock.getSuccessfulMembers.return_value = set(['simid1'])
        self.cq.addSimId('simid3')
        self.cq.updated = True
        with patch('sessionFuncs.getSimIdsFromShelve') as sfsm:
            sfsm.return_value = set(['simid1', 'simid2'])
            self.cq.loadSession(nodeMock)
        sfsm.assert_called_once_with('successful')
        nodeMock.getSuccessfulMembers.assert_called_once_with()
        assert nodeMock.getSuccessfulMembers() == set(['simid1'])
        self.assertEqual(set(['simid1', 'simid3']), self.cq.queue)
        self.assertFalse(self.cq.updated)

    def test_loadSession_on_nonempty_queue_with_disjoint_node_and_session(
            self):
        nodeMock = MagicMock()
        nodeMock.getSuccessfulMembers.return_value = set(['simid1'])
        self.cq.addSimId('simid4')
        self.cq.updated = True
        with patch('sessionFuncs.getSimIdsFromShelve') as sfsm:
            sfsm.return_value = set(['simid2', 'simid3'])
            self.cq.loadSession(nodeMock)
        sfsm.assert_called_once_with('successful')
        nodeMock.getSuccessfulMembers.assert_called_once_with()
        assert nodeMock.getSuccessfulMembers() == set(['simid1'])
        self.assertEqual(set(['simid4']), self.cq.queue)
        self.assertFalse(self.cq.updated)
