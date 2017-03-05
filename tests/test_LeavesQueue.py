from unittest import TestCase, skip
from mock import Mock, MagicMock, patch
from queues import LeavesQueue


class TestLeavesQueue(TestCase):

    def setUp(self):
        self.lq = LeavesQueue()

    def test_constructor(self):
        self.assertEqual(set([]), self.lq.queue)
        self.assertEqual([], self.lq.namesLen)
        self.assertFalse(self.lq.updated)
        self.assertEqual(
            ['Num.', 'Analysis', 'Model', 'Elements'], self.lq.cols)

    def test_addLeaf_to_empty_queue_with_valid_args(self):
        self.lq.updated = True
        leaf = MagicMock()
        self.lq.addLeaf(leaf)
        self.assertEqual(set([leaf]), self.lq.queue)
        self.assertFalse(self.lq.updated)

    def test_addLeaf_to_nonempty_queue_with_valid_args(self):
        self.lq.updated = True
        leaf1 = MagicMock()
        self.lq.addLeaf(leaf1)
        self.assertFalse(self.lq.updated)
        self.assertEqual(set([leaf1]), self.lq.queue)
        self.lq.updated = True
        leaf2 = MagicMock()
        self.lq.addLeaf(leaf2)
        self.assertEqual(set([leaf1, leaf2]), self.lq.queue)
        self.assertFalse(self.lq.updated)

    def test_getNodeNames_with_a_single_node(self):
        node = MagicMock()
        node.getName.return_value = 'testnode'
        self.lq.nd = 0
        names1 = self.lq.getNodeNames(node, 0, [])
        self.assertEqual(['testnode'], names1)
        names2 = self.lq.getNodeNames(node, 0, [0])
        self.assertEqual(['testnode', 0], names2)

    def test_getNodeNames_with_two_nodes(self):
        childnode = MagicMock()
        childnode.getName.return_value = 'childnode'
        parentnode = MagicMock()
        parentnode.getName.return_value = 'parentnode'
        childnode.getParent.return_value = parentnode
        self.lq.nd = 1
        names = self.lq.getNodeNames(childnode, 0, [])
        self.assertEqual(['parentnode', 'childnode'], names)

    def test_createNodeNamesSL(self):
        with patch('queues.LeavesQueue.getNodeNames') as gnn:
            gnn.return_value = ['parent', 'child']
            self.lq.namesLen = [2, 10, 8]
            namespace = self.lq.createNodeNamesSL([])
            self.assertEqual(['parent    ', 'child   '], namespace)

    def test_initNamesLen_with_single_queue_item(self):
        node = MagicMock()
        node.getName.return_value = 'cnode'
        pnode = MagicMock()
        pnode.getName.return_value = 'parentnode'
        ppnode = MagicMock()
        ppnode.getName.return_value = 'parentparentnode'
        node.getParent.return_value = pnode
        pnode.getParent.return_value = ppnode
        self.lq.addLeaf(node)
        expected = [4, 16, 10, 8]
        self.lq.initNamesLen()
        self.assertEqual(expected, self.lq.namesLen)
