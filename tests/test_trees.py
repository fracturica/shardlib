import unittest
from mock import Mock, MagicMock, patch, call
from test_treeSetUp import TreeSetUp, node1FEMmembers, node1XFEMmembers, node2FEMmembers, node3FEMmembers, node3XFEMmembers, node5XFEMmembers, node10FEMmembers, node10XFEMmembers
from trees import TreeNode, createTreeFromDbKeys, nodesPerLevel, tracePath, createTreeOfKeys, maxNodesPerLevel, nodeNamesPerLevel


class TestTreeNode_constructor_parent_child_members_methods(unittest.TestCase):

    def test_constructor(self):
        tn = TreeNode('nodeName')
        self.assertEqual('nodeName', tn.name)
        self.assertIsNone(tn.parent)
        self.assertEqual(0, len(tn.children))
        self.assertTrue(isinstance(tn.children, (set, list, tuple)))
        self.assertEqual(set([]), tn.failedMembers)
        self.assertEqual(set([]), tn.successfulMembers)

    def test_setParent_with_None(self):
        tn = TreeNode('nodeName')
        tn.setParent(None)
        self.assertIsNone(tn.parent)

    def test_setParent_with_TreeNode_instance(self):
        tn = TreeNode('nodeName')
        pn = TreeNode('parentNodeName')
        tn.setParent(pn)
        self.assertIs(pn, tn.parent)

    def test_setParent_with_Str_set_tuple(self):
        tn = TreeNode('nodeName')
        self.assertRaises(TypeError, tn.setParent, 'pnode')
        self.assertRaises(TypeError, tn.setParent, [1, 2])
        self.assertRaises(TypeError, tn.setParent, (1, 2))
        self.assertRaises(TypeError, tn.setParent, set([1, 2]))

    def test_setChild_with_invalid_argument(self):
        tn = TreeNode('nodeName')
        sortMock = MagicMock()
        with patch('trees.TreeNode.sortChildren') as sortMock:
            self.assertRaises(TypeError, tn.setChild, 'child')
            self.assertRaises(TypeError, tn.setChild, ('child',))
            self.assertRaises(TypeError, tn.setChild, ['child'])
            self.assertRaises(TypeError, tn.setChild, set(['child']))
        self.assertFalse(sortMock.called)

    def test_setChild_with_TreeNode_instances(self):
        tn = TreeNode('nodeName')
        cn1 = TreeNode('childNode1')
        cn2 = TreeNode('childNode2')
        sortMock = MagicMock()
        with patch('trees.TreeNode.sortChildren') as sortMock:
            tn.setChild(cn1)
            self.assertEqual([cn1], tn.children)
            sortMock.assert_called_once_with()
            tn.setChild(cn2)
            self.assertEqual(set([cn1, cn2]), set(tn.children))
            self.assertEqual([call(), call()], sortMock.mock_calls)

    def test_sortChildren_with_children_names_string_numbers(self):
        tn = TreeNode('nodeName')
        ch1Mock = MagicMock()
        ch2Mock = MagicMock()
        ch3Mock = MagicMock()
        ch1Mock.getName.return_value = '10'
        ch2Mock.getName.return_value = '9'
        ch3Mock.getName.return_value = '9.5'
        tn.children = [ch1Mock, ch2Mock, ch3Mock]
        tn.sortChildren()
        self.assertEqual([ch2Mock, ch3Mock, ch1Mock], tn.children)

    def test_sortChildren_with_strings(self):
        tn = TreeNode('nodeName')
        ch1Mock = MagicMock()
        ch2Mock = MagicMock()
        ch3Mock = MagicMock()
        ch1Mock.getName.return_value = 'a'
        ch2Mock.getName.return_value = 'b'
        ch3Mock.getName.return_value = 'c'
        tn.children = [ch2Mock, ch3Mock, ch1Mock]
        tn.sortChildren()
        self.assertEqual([ch1Mock, ch2Mock, ch3Mock], tn.children)

    def test_addMembers_with_str_member(self):
        tn = TreeNode('nodeName')
        tn.addMembers('simid1', 'successful')
        self.assertEqual(set(['simid1']), tn.successfulMembers)
        tn.addMembers('simid2', 'successful')
        tn.addMembers('simid3', 'failed')
        self.assertEqual(set(['simid3']), tn.failedMembers)
        tn.addMembers('simid4', 'failed')
        self.assertEqual(set(['simid3', 'simid4']), tn.failedMembers)
        self.assertEqual(set(['simid1', 'simid2']), tn.successfulMembers)

    def test_addMembers_with_sequence(self):
        tn = TreeNode('nodeName')
        tn.addMembers(['simid1', 'simid2'], 'successful')
        self.assertEqual(set(['simid1', 'simid2']), tn.successfulMembers)
        self.assertEqual(set([]), tn.failedMembers)
        tn.addMembers(['simid3', 'simid4'], 'failed')
        self.assertEqual(set(['simid3', 'simid4']), tn.failedMembers)
        self.assertEqual(set(['simid1', 'simid2']), tn.successfulMembers)

    def test_addMembers_with_None(self):
        tn = TreeNode('nodeName')
        tn.addMembers(None, 'successful')
        tn.addMembers(None, 'failed')
        self.assertEqual(set([]), tn.successfulMembers)
        self.assertEqual(set([]), tn.failedMembers)

    def test_addMembers_with_invalid_arguments(self):
        tn = TreeNode('nodeName')
        self.assertRaises(AssertionError, tn.addMembers, None, 'unknownType')
        self.assertRaises(AssertionError, tn.addMembers, 1, 'successful')

    def test_addFailedMember(self):
        tn = TreeNode('nodeName')
        tn.addFailedMember(None)
        self.assertEqual(set([]), tn.failedMembers)
        tn.addFailedMember('simid1')
        self.assertEqual(set(['simid1']), tn.failedMembers)
        tn.addFailedMember('simid2')
        self.assertEqual(set(['simid1', 'simid2']), tn.failedMembers)

    def test_addSuccessfulMember(self):
        tn = TreeNode('nodeName')
        tn.addSuccessfulMember(None)
        self.assertEqual(set([]), tn.successfulMembers)
        tn.addSuccessfulMember('simid1')
        self.assertEqual(set(['simid1']), tn.successfulMembers)
        tn.addSuccessfulMember('simid2')
        self.assertEqual(set(['simid1', 'simid2']), tn.successfulMembers)

    def test_addMember_with_successful_simid(self):
        sMock1 = MagicMock()
        sMock1.getEntryKey.return_value = 'simid1'
        sMock1.getAnalysisSuccess.return_value = True
        sMock2 = MagicMock()
        sMock2.getEntryKey.return_value = 'simid2'
        sMock2.getAnalysisSuccess.return_value = True
        tn = TreeNode('nodeName')
        tn.addMember(sMock1)
        self.assertEqual(set(['simid1']), tn.successfulMembers)
        tn.addMember(sMock2)
        self.assertEqual(set(['simid1', 'simid2']), tn.successfulMembers)
        self.assertEqual(set([]), tn.failedMembers)

    def test_addMember_with_failed_simid(self):
        fMock1 = MagicMock()
        fMock1.getEntryKey.return_value = 'simid1'
        fMock1.getAnalysisSuccess.return_value = False
        fMock2 = MagicMock()
        fMock2.getEntryKey.return_value = 'simid2'
        fMock2.getAnalysisSuccess.return_value = False
        tn = TreeNode('nodeName')
        tn.addMember(fMock1)
        self.assertEqual(set(['simid1']), tn.failedMembers)
        self.assertEqual(set([]), tn.successfulMembers)
        tn.addMember(fMock2)
        self.assertEqual(set(['simid1', 'simid2']), tn.failedMembers)
        self.assertEqual(set([]), tn.successfulMembers)

    def test__eq__(self):
        tn0 = TreeNode(0)
        tn1 = TreeNode(1)
        tn01 = TreeNode(0)
        self.assertFalse(tn0.__eq__(tn1))
        self.assertTrue(tn0.__eq__(tn01))
        self.assertRaises(AssertionError, tn0.__eq__, 0)


class TestTreeNode_tree_browsing(TreeSetUp):

    def test_getRootNode_with_nonroot_node_argument(self):
        self.assertIs(self.root, self.node1FEMs.getRootNode())
        self.assertIs(self.root, self.node1XFEMmpLR.getRootNode())
        self.assertIs(self.root, self.node2FEMsQF.getRootNode())
        self.assertIs(self.root, self.node3FEMeQR.getRootNode())
        self.assertIs(self.root, self.node5XFEMcp.getRootNode())
        self.assertIs(self.root, self.node10.getRootNode())
        self.assertIs(self.root, self.node10FEMeLF.getRootNode())

    def test_getRootNode_with_root_node_argument(self):
        self.assertIs(self.root, self.root.getRootNode())

    def test_getNodeLevelInTree(self):
        self.assertEqual(0, self.root.getNodeLevelInTree())
        self.assertEqual(1, self.node1.getNodeLevelInTree())
        self.assertEqual(1, self.node10.getNodeLevelInTree())
        self.assertEqual(1, self.node3.getNodeLevelInTree())
        self.assertEqual(2, self.node1FEM.getNodeLevelInTree())
        self.assertEqual(2, self.node1XFEM.getNodeLevelInTree())
        self.assertEqual(2, self.node2FEM.getNodeLevelInTree())
        self.assertEqual(3, self.node1FEMe.getNodeLevelInTree())
        self.assertEqual(3, self.node1FEMs.getNodeLevelInTree())
        self.assertEqual(3, self.node1XFEMcp.getNodeLevelInTree())
        self.assertEqual(3, self.node2FEMs.getNodeLevelInTree())
        self.assertEqual(4, self.node1FEMsQR.getNodeLevelInTree())
        self.assertEqual(4, self.node1FEMeQF.getNodeLevelInTree())
        self.assertEqual(4, self.node10FEMeLF.getNodeLevelInTree())
        self.assertEqual(4, self.node2FEMsQF.getNodeLevelInTree())

    def test_hasChildNode_with_existing_child_nodes(self):
        self.assertTrue(self.root.hasChildNode('1.0'))
        self.assertTrue(self.root.hasChildNode('10.0'))
        self.assertTrue(self.root.hasChildNode('5.0'))
        self.assertTrue(self.node1.hasChildNode('FEM'))
        self.assertTrue(self.node2FEMs.hasChildNode('QF'))

    def test_hasChildNode_with_non_existing_child_nodes(self):
        self.assertFalse(self.node10XFEMcp.hasChildNode(''))
        self.assertFalse(self.node5XFEM.hasChildNode('mp'))
        self.assertFalse(self.node2FEMs.hasChildNode('QR'))
        self.assertFalse(self.root.hasChildNode('sampleNode'))
        self.assertFalse(self.node1FEM.hasChildNode('FEM'))
        self.assertFalse(self.node1FEMsQR.hasChildNode('FEM'))
        self.assertFalse(self.node1XFEMmpLR.hasChildNode('mp'))
        self.assertFalse(self.node2FEMsQF.hasChildNode('2.0'))
        self.assertFalse(self.node10XFEMcpLR.hasChildNode('LF'))

    def test_getTreeBranch_with_ambiguous_path(self):
        self.assertRaises(
            KeyError, self.root.getTreeBranch, [
                'XFEM', 'cp', 'LT'])
        self.assertRaises(KeyError, self.root.getTreeBranch, ['QR'])
        self.assertRaises(KeyError, self.root.getTreeBranch,
                          ['FEM', 'elliptic', 'QF'])
        self.assertRaises(KeyError, self.root.getTreeBranch,
                          ['FEM', 'elliptic', 'LF'])

    def test_getTreeBranch_with_nonexisting_path(self):
        self.assertRaises(KeyError, self.root.getTreeBranch,
                          ['1.0', 'FEM', 'scale', 'QF'])
        self.assertRaises(
            KeyError, self.node2.getTreeBranch, [
                '11', 'FEM', 'cp'])

    def test_getTreeBranch_with_existing_and_unique_path(self):
        self.assertIs(self.node1FEMs,
                      self.root.getTreeBranch(['1.0', 'FEM', 'scale']))
        self.assertIs(self.node1FEMsQR,
                      self.root.getTreeBranch(['1.0', 'FEM', 'scale', 'QR']))
        self.assertIs(self.node1XFEMcpLT,
                      self.node1.getTreeBranch(['1.0', 'XFEM', 'cp', 'LT']))
        self.assertIs(self.node5XFEMcpLT,
                      self.root.getTreeBranch(['5.0', 'XFEM', 'cp', 'LT']))
        self.assertIs(self.node1XFEMmpLR,
                      self.node1XFEM.getTreeBranch(['mp', 'LR']))

    def test_countNumberOfTreeLevels(self):
        self.assertEqual(4, self.root.countNumberOfTreeLevels())
        tn0 = TreeNode('nodeLevel0')
        self.assertEqual(0, tn0.countNumberOfTreeLevels())
        tn1a = TreeNode('nodeLevel1a')
        tn1b = TreeNode('nodeLevel1b')
        tn0.setChild(tn1a)
        tn0.setChild(tn1b)
        tn1a.setParent(tn0)
        tn1b.setParent(tn0)
        self.assertEqual(1, tn0.countNumberOfTreeLevels())
        tn2a = TreeNode('nodeLevel2a')
        tn2a.setParent(tn1a)
        tn1a.setChild(tn2a)
        self.assertEqual(2, tn1b.countNumberOfTreeLevels())
        tn3a = TreeNode('nodeLevel3a')
        tn3a.setParent(tn2a)
        tn2a.setChild(tn3a)
        self.assertEqual(3, tn1b.countNumberOfTreeLevels())
        tn2b = TreeNode('nodeLevel2b')
        tn1b.setChild(tn2b)
        tn2b.setParent(tn1b)
        self.assertEqual(3, tn2b.countNumberOfTreeLevels())

    def test_getNodeLevel(self):
        self.assertEqual(0, self.root.getNodeLevel(self.root))
        self.assertEqual(1, self.node1.getNodeLevel(self.node1))
        self.assertEqual(1, self.root.getNodeLevel(self.node10))
        self.assertEqual(2, self.node1FEMs.getNodeLevel(self.node10XFEM))
        self.assertEqual(3, self.node5.getNodeLevel(self.node10XFEMcp))
        self.assertEqual(3, self.root.getNodeLevel(self.node3XFEMmp))
        self.assertEqual(4, self.root.getNodeLevel(self.node1FEMsQR))

    def test_getChildLeafNodes(self):
        self.assertEqual(set([]), set(
            self.node1FEMsQR.getChildLeafNodes(self.node10XFEMcpLR)))
        self.assertEqual(set([self.node1FEMsQR, self.node1FEMsLR]),
                         set(self.root.getChildLeafNodes(self.node1FEMs)))
        self.assertEqual(set([self.node1FEMsQR,
                              self.node1FEMsLR,
                              self.node1FEMeQF,
                              self.node1FEMeLF]),
                         set(self.root.getChildLeafNodes(self.node1FEM)))
        self.assertEqual(set([self.node2FEMsQF]),
                         set(self.root.getChildLeafNodes(self.node2)))
        self.assertEqual(set([self.node3FEMeQR, self.node3XFEMmpLF]),
                         set(self.root.getChildLeafNodes(self.node3)))
        self.assertEqual(set([
            self.node1FEMsQR, self.node1FEMsLR,
            self.node1FEMeQF, self.node1FEMeLF,
            self.node1XFEMcpLT, self.node1XFEMmpLR,
            self.node2FEMsQF,
            self.node3FEMeQR, self.node3XFEMmpLF,
            self.node5XFEMcpLT,
            self.node10FEMeQF, self.node10FEMeLF,
            self.node10XFEMcpLR]),
            set(self.root.getChildLeafNodes(self.root)))


class TestTreeNode_member_assignment(TreeSetUp):

    def setUp_assignMemberAsFailed(self):
        tn0 = TreeNode('nodeLevel0')
        tn1a = TreeNode('nodeLevel1a')
        tn1b = TreeNode('nodeLevel1b')
        tn0.setChild(tn1a)
        tn0.setChild(tn1b)
        tn1a.setParent(tn0)
        tn1b.setParent(tn0)
        tn1a.successfulMembers = set(['a1', 'a2', 'a3', 'a4'])
        tn1b.successfulMembers = set(['b1', 'b2', 'b3', 'b4'])
        return tn0, tn1a, tn1b

    def test_assignMemberAsFailed_existing_member_called_on_root_node_with_print(
            self):
        prMock1 = MagicMock()
        with patch('trees.TreeNode.printNode') as prMock1:
            res = self.root.assignMemberAsFailed(
                'node2FEMsQF_sm_1', printChanges=True, rowlen=21)
        prMock1.assert_called_once_with(self.node2FEMsQF, 21)
        self.assertEqual(1, res)
        self.assertEqual(set(['node2FEMsQF_sm_2']),
                         self.node2FEMsQF.successfulMembers)
        self.assertEqual(set(['node2FEMsQF_sm_1']),
                         self.node2FEMsQF.failedMembers)
        node1FEMmembers(self)
        node1XFEMmembers(self)
        node3FEMmembers(self)
        node3XFEMmembers(self)
        node5XFEMmembers(self)
        node10FEMmembers(self)
        node10XFEMmembers(self)

    def test_assignMemberAsFailed_existing_member_called_on_root_without_print(
            self):
        prMock1 = MagicMock()
        with patch('trees.TreeNode.printNode') as prMock1:
            res = self.root.assignMemberAsFailed(
                'node3FEMeQR_sm_1', printChanges=False)
        self.assertFalse(prMock1.called)
        self.assertEqual(1, res)
        self.assertEqual(set([]), set(self.node3FEMeQR.successfulMembers))
        self.assertEqual(set([
            'node3FEMeQR_sm_1', 'node3FEMeQR_fm_1', 'node3FEMeQR_fm_2']),
            set(self.node3FEMeQR.failedMembers))
        node1FEMmembers(self)
        node1XFEMmembers(self)
        node2FEMmembers(self)
        node3XFEMmembers(self)
        node5XFEMmembers(self)
        node10FEMmembers(self)
        node10XFEMmembers(self)

    def test_assignMemberAsFailed_existing_member_called_on_nonroot_without_print(
            self):
        res = self.node1FEM.assignMemberAsFailed(
            'node5XFEMcpLT_sm_2', printChanges=False)
        self.assertEqual(1, res)
        self.assertEqual(set(['node5XFEMcpLT_sm_1']),
                         set(self.node5XFEMcpLT.successfulMembers))
        self.assertEqual(set(['node5XFEMcpLT_sm_2',
                              'node5XFEMcpLT_fm_1',
                              'node5XFEMcpLT_fm_2',
                              'node5XFEMcpLT_fm_3']),
                         self.node5XFEMcpLT.failedMembers)
        node1FEMmembers(self)
        node1XFEMmembers(self)
        node2FEMmembers(self)
        node3FEMmembers(self)
        node3XFEMmembers(self)
        node10FEMmembers(self)
        node10XFEMmembers(self)

    def test_assignMemberAsFailed_nonexisting_member_without_print(self):
        res = self.root.assignMemberAsFailed('c1', printChanges=False)
        self.assertEqual(0, res)
        node1FEMmembers(self)
        node1XFEMmembers(self)
        node2FEMmembers(self)
        node3FEMmembers(self)
        node3XFEMmembers(self)
        node5XFEMmembers(self)
        node10FEMmembers(self)
        node10XFEMmembers(self)

    def test_assignMemberAsFailed_with_failed_member_without_print(self):
        res = self.root.assignMemberAsFailed(
            'node5XFEMcpLT_fm_1', printChanges=False)
        self.assertEqual(0, res)
        node1FEMmembers(self)
        node1XFEMmembers(self)
        node2FEMmembers(self)
        node3FEMmembers(self)
        node3XFEMmembers(self)
        node5XFEMmembers(self)
        node10FEMmembers(self)
        node10XFEMmembers(self)


class TestCreateTreeFromDbKeys(unittest.TestCase):

    def adMock_sf_1(self, param):
        parDict = {
            'crackRatio': '1.0', 'analysisType': 'FEM',
            'modelType': 'elliptic', 'elements': 'LinearRI'}
        return parDict[param]

    def adMock_sf_2(self, param):
        parDict = {
            'crackRatio': '1.0', 'analysisType': 'XFEM',
            'modelType': 'elliptic', 'elements': 'QuadraticFI'}
        return parDict[param]

    def mockFunc(self, key):
        if key == 'key1':
            self.adMock = MagicMock()
            self.adMock.getParameter.side_effect = self.adMock_sf_1
            self.adMock.getEntryKey.return_value = key
            self.adMock.getAnalysisSuccess.return_value = True
        elif key == 'key2':
            self.adMock = MagicMock()
            self.adMock.getParameter.side_effect = self.adMock_sf_2
            self.adMock.getAnalysisSuccess.return_value = False
            self.adMock.getEntryKey.return_value = key
        return self.adMock

    def setUp(self):
        self.adMock = MagicMock(side_effect=self.mockFunc)
        self.adPatch = patch(
            'dataProcessing.AnalysisData', self.adMock)
        self.adPatch.start()

    def tearDown(self):
        self.adPatch.stop()

    def test_createTreeFromDbKeys(self):
        root = createTreeFromDbKeys(['key1', 'key2'])
        self.assertIsNone(root.getParent())
        self.assertEqual(1, len(root.getChildren()))
        cnode = root.getChildren()[0]
        self.assertEqual('1.0', cnode.getName())

        self.assertEqual(2, len(cnode.getChildren()))
        self.assertEqual(set(['XFEM', 'FEM']), set(
            [n.getName() for n in cnode.getChildren()]))
        nodeFEM, nodeXFEM = cnode.getChildren()
        if nodeXFEM.getName() == 'FEM':
            nodeFEM, nodeXFEM = nodeXFEM, nodeFEM

        nodeXmt = nodeXFEM.getChildren()[0]
        nodeXel = nodeXmt.getChildren()[0]
        self.assertEqual(1, len(nodeXFEM.getChildren()))
        self.assertEqual(1, len(nodeXmt.getChildren()))
        self.assertEqual(0, len(nodeXel.getChildren()))

        self.assertEqual('XFEM', nodeXFEM.getName())
        self.assertEqual('elliptic', nodeXmt.getName())
        self.assertEqual('QuadraticFI', nodeXel.getName())
        self.assertEqual(set(['key2']), nodeXel.failedMembers)

        nodeFmt = nodeFEM.getChildren()[0]
        nodeFel = nodeFmt.getChildren()[0]
        self.assertEqual(1, len(nodeFEM.getChildren()))
        self.assertEqual(1, len(nodeFmt.getChildren()))
        self.assertEqual(0, len(nodeFel.getChildren()))

        self.assertEqual('FEM', nodeFEM.getName())
        self.assertEqual('elliptic', nodeFmt.getName())
        self.assertEqual('LinearRI', nodeFel.getName())
        self.assertEqual(set(['key1']), nodeFel.successfulMembers)


class TreeSetUp(unittest.TestCase):

    def setUp(self):
        self.root = TreeNode('root_0')
        self.node_1a_0 = TreeNode('nodeLevel_1a_0')
        self.node_1b_0 = TreeNode('nodeLevel_1b_0')
        self.root.setChild(self.node_1a_0)
        self.root.setChild(self.node_1b_0)
        self.node_1a_0.setParent(self.root)
        self.node_1b_0.setParent(self.root)
        self.levels = {0: set([self.root]), 1: set(
            [self.node_1a_0, self.node_1b_0])}
        self.node_2_1a = TreeNode('nodeLevel_2_1a')
        self.node_1a_0.setChild(self.node_2_1a)
        self.node_2_1a.setParent(self.node_1a_0)
        self.node_2a_1b = TreeNode('nodeLevel_2a_1b')
        self.node_2a_1b.setParent(self.node_1b_0)
        self.node_1b_0.setChild(self.node_2a_1b)
        self.node_2b_1b = TreeNode('nodeLevel_2b_1b')
        self.node_2b_1b.setParent(self.node_1b_0)
        self.node_1b_0.setChild(self.node_2b_1b)
        self.levels[2] = set(
            [self.node_2_1a, self.node_2a_1b, self.node_2b_1b])
        self.node_3_2 = TreeNode('nodeLevel_3_2')
        self.node_3_2.setParent(self.node_2_1a)
        self.node_2_1a.setChild(self.node_3_2)
        self.node_3_2a = TreeNode('nodeLevel_3_2a')
        self.node_3_2a.setParent(self.node_2a_1b)
        self.node_2a_1b.setChild(self.node_3_2a)
        self.levels[3] = set([self.node_3_2a, self.node_3_2])


class TestMaxNodesPerLevel(TreeSetUp):

    def testMaxNodesPerLevel(self):
        exp = {0: 1, 1: 2, 2: 2, 3: 1}
        self.assertEqual(exp, maxNodesPerLevel(self.root))


class TestNodeNamesPerLevel(TreeSetUp):

    def test_nodeNamesPerLevel(self):
        exp = {
            0: ['root_0'], 1: sorted(['nodeLevel_1a_0', 'nodeLevel_1b_0']),
            2: sorted(['nodeLevel_2_1a', 'nodeLevel_2a_1b', 'nodeLevel_2b_1b']),
            3: sorted(['nodeLevel_3_2', 'nodeLevel_3_2a'])}
        self.assertEqual(exp, nodeNamesPerLevel(self.root))


class TestNodesPerLevel(TreeSetUp):

    def test_nodesPerLevel(self):
        self.assertEqual(self.levels, nodesPerLevel(self.root))


class TestTracePath(TreeSetUp):

    def test_tracePath_with_limitLevel_None(self):
        exp = [self.root, self.node_1a_0, self.node_2_1a, self.node_3_2]
        self.assertEqual(exp, tracePath(self.node_3_2, limitLevel=None))
        exp = [self.root, self.node_1b_0, self.node_2a_1b, self.node_3_2a]
        self.assertEqual(exp, tracePath(self.node_3_2a, limitLevel=None))
        exp = [self.root, self.node_1b_0, self.node_2b_1b]
        self.assertEqual(exp, tracePath(self.node_2b_1b, limitLevel=None))

    def test_tracePath_with_limitLevel_zero(self):
        exp = [self.root, self.node_1a_0, self.node_2_1a, self.node_3_2]
        self.assertEqual(exp, tracePath(self.node_3_2, limitLevel=0))

    def test_tracePath_with_limitLevel_between_zero_and_max_tree_depth(self):
        exp = [self.node_1a_0, self.node_2_1a, self.node_3_2]
        self.assertEqual(exp, tracePath(self.node_3_2, limitLevel=1))
        exp = [self.node_2a_1b, self.node_3_2a]
        self.assertEqual(exp, tracePath(self.node_3_2a, limitLevel=2))
        exp = [self.node_3_2a]
        self.assertEqual(exp, tracePath(self.node_3_2a, limitLevel=3))
        exp = []
        self.assertEqual(exp, tracePath(self.node_3_2, limitLevel=4))

    def test_tracePath_with_limitLevel_higher_than_tree_depth(self):
        self.assertRaises(IndexError, tracePath, self.node_3_2, limitLevel=5)


class TestCreateTreeOfKeys(unittest.TestCase):

    def setUp(self):
        self.root = TreeNode('root')
        node1 = TreeNode('1.0')
        self.root.setChild(node1)
        node1.setParent(self.root)
        node1fem = TreeNode('FEM')
        node1fem.setParent(node1)
        node1.setChild(node1fem)
        node1femellip = TreeNode('elliptic')
        node1femellip.setParent(node1fem)
        node1fem.setChild(node1femellip)
        node1femellipL = TreeNode('LinearRI')
        node1femellipL.setParent(node1femellip)
        node1femellip.setChild(node1femellipL)
        node1xfem = TreeNode('XFEM')
        node1xfem.setParent(node1)
        node1.setChild(node1xfem)
        node1xfemCP = TreeNode('cp')
        node1xfemCP.setParent(node1xfem)
        node1xfem.setChild(node1xfemCP)
        node1xfemCPLT = TreeNode('LinearTet')
        node1xfemCPLT.setParent(node1xfemCP)
        node1xfemCP.setChild(node1xfemCPLT)

        node2 = TreeNode('2.0')
        self.root.setChild(node2)
        node2.setParent(self.root)
        node2fem = TreeNode('FEM')
        node2fem.setParent(node2)
        node2.setChild(node2fem)
        node2femscale = TreeNode('scale')
        node2femscale.setParent(node2fem)
        node2fem.setChild(node2femscale)
        node2femscaleQR = TreeNode('QuadRI')
        node2femscaleQR.setParent(node2femscale)
        node2femscale.setChild(node2femscaleQR)
        node2xfem = TreeNode('XFEM')
        node2xfem.setParent(node2)
        node2.setChild(node2xfem)
        node2xfemmp = TreeNode('mp')
        node2xfem.setChild(node2xfemmp)
        node2xfemmp.setParent(node2xfem)
        node2xfemmpLF = TreeNode('LinearFI')
        node2xfemmp.setChild(node2xfemmpLF)
        node2xfemmpLF.setParent(node2xfemmp)

        node3 = TreeNode('3.0')
        self.root.setChild(node3)
        node3.setParent(self.root)
        node3fem = TreeNode('FEM')
        node3.setChild(node3fem)
        node3fem.setParent(node3)
        node3femellip = TreeNode('elliptic')
        node3fem.setChild(node3femellip)
        node3femellip.setParent(node3fem)
        node3femellipQR = TreeNode('QuadRI')
        node3femellipQR.setParent(node3femellip)
        node3femellip.setChild(node3femellipQR)
        node3xfem = TreeNode('XFEM')
        node3xfem.setParent(node3)
        node3.setChild(node3xfem)
        node3xfemmp = TreeNode('mp')
        node3xfem.setChild(node3xfemmp)
        node3xfemmp.setParent(node3xfem)
        node3xfemmpQF = TreeNode('QuadFI')
        node3xfemmp.setChild(node3xfemmpQF)
        node3xfemmpQF.setParent(node3xfemmp)

    def test_createTreeOfKeys(self):
        nr = createTreeOfKeys(self.root)
        self.assertEqual(set(['FEM', 'XFEM']),
                         set([n.getName() for n in nr.getChildren()]))
        nodeF, nodeX = nr.getChildren()
        if nodeX.getName() == 'FEM':
            nodeX, nodeF = nodeF, nodeX
        self.assertEqual('FEM', nodeF.getName())
        self.assertEqual('XFEM', nodeX.getName())
        self.assertEqual(sorted(['elliptic', 'scale']),
                         sorted([n.getName() for n in nodeF.getChildren()]))
        nodeFe, nodeFs = nodeF.getChildren()
        if nodeFe.getName() == 'scale':
            nodeFe, nodeFs = nodeFs, nodeFe
        self.assertEqual('scale', nodeFs.getName())
        self.assertEqual('elliptic', nodeFe.getName())
        self.assertEqual(sorted(['LinearRI', 'QuadRI']),
                         sorted([n.getName() for n in nodeFe.getChildren()]))
        self.assertEqual(1, len(nodeFs.getChildren()))
        self.assertEqual('QuadRI', nodeFs.getChildren()[0].getName())

        self.assertEqual(sorted(['mp', 'cp']),
                         sorted([n.getName() for n in nodeX.getChildren()]))
        nodeXm, nodeXc = nodeX.getChildren()
        if nodeXm.getName() == 'cp':
            nodeXm, nodeXc = nodeXc, nodeXm
        self.assertEqual('cp', nodeXc.getName())
        self.assertEqual('mp', nodeXm.getName())
        self.assertEqual(1, len(nodeXc.getChildren()))
        self.assertEqual('LinearTet', nodeXc.getChildren()[0].getName())
        self.assertEqual(sorted(['LinearFI', 'QuadFI']),
                         sorted([n.getName() for n in nodeXm.getChildren()]))
