import unittest
from trees import TreeNode


class TreeSetUp(unittest.TestCase):

    def setUp(self):
        self.createRootNode()
        self.createNodesLevel_1()
        self.createBranch_1_FEM()
        self.createBranch_1_XFEM()
        self.createBranch_2_FEM()
        self.createBranch_3_FEM()
        self.createBranch_3_XFEM()
        self.createBranch_5_XFEM()
        self.createBranch_10_FEM()
        self.createBranch_10_XFEM()
        self.add_simIds_to_tree_leaf_nodes()

    def createRootNode(self):
        self.root = TreeNode('root')

    def createNodesLevel_1(self):
        self.node1 = TreeNode('1.0')
        self.root.setChild(self.node1)
        self.node1.setParent(self.root)
        self.node2 = TreeNode('2.0')
        self.root.setChild(self.node2)
        self.node2.setParent(self.root)
        self.node3 = TreeNode('3.0')
        self.root.setChild(self.node3)
        self.node3.setParent(self.root)
        self.node5 = TreeNode('5.0')
        self.root.setChild(self.node5)
        self.node5.setParent(self.root)
        self.node10 = TreeNode('10.0')
        self.root.setChild(self.node10)
        self.node10.setParent(self.root)

    def createBranch_1_FEM(self):
        self.node1FEM = TreeNode('FEM')
        self.node1.setChild(self.node1FEM)
        self.node1FEM.setParent(self.node1)
        self.node1FEMs = TreeNode('scale')
        self.node1FEM.setChild(self.node1FEMs)
        self.node1FEMs.setParent(self.node1FEM)
        self.node1FEMsQR = TreeNode('QR')
        self.node1FEMs.setChild(self.node1FEMsQR)
        self.node1FEMsQR.setParent(self.node1FEMs)
        self.node1FEMsLR = TreeNode('LR')
        self.node1FEMs.setChild(self.node1FEMsLR)
        self.node1FEMsLR.setParent(self.node1FEMs)

        self.node1FEMe = TreeNode('elliptic')
        self.node1FEM.setChild(self.node1FEMe)
        self.node1FEMe.setParent(self.node1FEM)
        self.node1FEMeQF = TreeNode('QF')
        self.node1FEMe.setChild(self.node1FEMeQF)
        self.node1FEMeQF.setParent(self.node1FEMe)
        self.node1FEMeLF = TreeNode('LF')
        self.node1FEMe.setChild(self.node1FEMeLF)
        self.node1FEMeLF.setParent(self.node1FEMe)

    def createBranch_1_XFEM(self):
        self.node1XFEM = TreeNode('XFEM')
        self.node1.setChild(self.node1XFEM)
        self.node1XFEM.setParent(self.node1)
        self.node1XFEMcp = TreeNode('cp')
        self.node1XFEM.setChild(self.node1XFEMcp)
        self.node1XFEMcp.setParent(self.node1XFEM)
        self.node1XFEMcpLT = TreeNode('LT')
        self.node1XFEMcp.setChild(self.node1XFEMcpLT)
        self.node1XFEMcpLT.setParent(self.node1XFEMcp)
        self.node1XFEMmp = TreeNode('mp')
        self.node1XFEMmp.setParent(self.node1XFEM)
        self.node1XFEM.setChild(self.node1XFEMmp)
        self.node1XFEMmpLR = TreeNode('LR')
        self.node1XFEMmp.setChild(self.node1XFEMmpLR)
        self.node1XFEMmpLR.setParent(self.node1XFEMmp)

    def createBranch_2_FEM(self):
        self.node2FEM = TreeNode('FEM')
        self.node2.setChild(self.node2FEM)
        self.node2FEM.setParent(self.node2)
        self.node2FEMs = TreeNode('scale')
        self.node2FEM.setChild(self.node2FEMs)
        self.node2FEMs.setParent(self.node2FEM)
        self.node2FEMsQF = TreeNode('QF')
        self.node2FEMsQF.setParent(self.node2FEMs)
        self.node2FEMs.setChild(self.node2FEMsQF)

    def createBranch_3_FEM(self):
        self.node3FEM = TreeNode('FEM')
        self.node3.setChild(self.node3FEM)
        self.node3FEM.setParent(self.node3)
        self.node3FEMe = TreeNode('elliptic')
        self.node3FEM.setChild(self.node3FEMe)
        self.node3FEMe.setParent(self.node3FEM)
        self.node3FEMeQR = TreeNode('QR')
        self.node3FEMe.setChild(self.node3FEMeQR)
        self.node3FEMeQR.setParent(self.node3FEMe)

    def createBranch_3_XFEM(self):
        self.node3XFEM = TreeNode('XFEM')
        self.node3.setChild(self.node3XFEM)
        self.node3XFEM.setParent(self.node3)
        self.node3XFEMmp = TreeNode('mp')
        self.node3XFEM.setChild(self.node3XFEMmp)
        self.node3XFEMmp.setParent(self.node3XFEM)
        self.node3XFEMmpLF = TreeNode('LF')
        self.node3XFEMmp.setChild(self.node3XFEMmpLF)
        self.node3XFEMmpLF.setParent(self.node3XFEMmp)

    def createBranch_5_XFEM(self):
        self.node5XFEM = TreeNode('XFEM')
        self.node5XFEM.setParent(self.node5)
        self.node5.setChild(self.node5XFEM)
        self.node5XFEMcp = TreeNode('cp')
        self.node5XFEMcp.setParent(self.node5XFEM)
        self.node5XFEM.setChild(self.node5XFEMcp)
        self.node5XFEMcpLT = TreeNode('LT')
        self.node5XFEMcp.setChild(self.node5XFEMcpLT)
        self.node5XFEMcpLT.setParent(self.node5XFEMcp)

    def createBranch_10_FEM(self):
        self.node10FEM = TreeNode('FEM')
        self.node10.setChild(self.node10FEM)
        self.node10FEM.setParent(self.node10)
        self.node10FEMe = TreeNode('elliptic')
        self.node10FEMe.setParent(self.node10FEM)
        self.node10FEM.setChild(self.node10FEMe)
        self.node10FEMeQF = TreeNode('QF')
        self.node10FEMe.setChild(self.node10FEMeQF)
        self.node10FEMeQF.setParent(self.node10FEMe)
        self.node10FEMeLF = TreeNode('LF')
        self.node10FEMe.setChild(self.node10FEMeLF)
        self.node10FEMeLF.setParent(self.node10FEMe)

    def createBranch_10_XFEM(self):
        self.node10XFEM = TreeNode('XFEM')
        self.node10.setChild(self.node10XFEM)
        self.node10XFEM.setParent(self.node10)
        self.node10XFEMcp = TreeNode('cp')
        self.node10XFEM.setChild(self.node10XFEMcp)
        self.node10XFEMcp.setParent(self.node10XFEM)
        self.node10XFEMcpLR = TreeNode('LR')
        self.node10XFEMcp.setChild(self.node10XFEMcpLR)
        self.node10XFEMcpLR.setParent(self.node10XFEMcp)

    def add_simIds_to_tree_leaf_nodes(self):
        # branch 1.0
        self.node1FEMsQR.successfulMembers = set(
            ['node1FEMsQR_sm_1', 'node1FEMsQR_sm_2'])
        self.node1FEMsQR.failedMembers = set(['node1FEMsQR_fm_1'])
        self.node1FEMsLR.successfulMembers = set(['node1FEMsLR_sm_1'])
        self.node1FEMsLR.failedMembers = set(['node1FEMsLR_fm_1'])

        self.node1FEMeQF.successfulMembers = set(['node1FEMeQF_sm_1'])
        self.node1FEMeQF.failedMembers = set(
            ['node1FEMeQF_fm_1', 'node1FEMeQF_fm_2'])
        self.node1FEMeLF.successfulMembers = set(
            ['node1FEMeLF_sm_1', 'node1FEMeLF_sm_2', 'node1FEMeLF_sm_3'])
        self.node1FEMeLF.failedMembers = set(['node1FEMeLF_fm_1'])

        self.node1XFEMcpLT.successfulMembers = set(
            ['node1XFEMcpLT_sm_1', 'node1XFEMcpLT_sm_2', 'node1XFEMcpLT_sm_3'])
        self.node1XFEMcpLT.failedMembers = set(['node1XFEMcpLT_fm_1'])
        self.node1XFEMmpLR.successfulMembers = set(
            ['node1XFEMmpLR_sm_1', 'node1XFEMmpLR_sm_2'])
        self.node1XFEMmpLR.failedMembers = set(['node1XFEMmpLR_fm_1'])

# branch 2.0
        self.node2FEMsQF.successfulMembers = set(
            ['node2FEMsQF_sm_1', 'node2FEMsQF_sm_2'])
        # self.node2FEMsQF.failedMembers  # None
# branch 3.0
        self.node3FEMeQR.successfulMembers = set(['node3FEMeQR_sm_1'])
        self.node3FEMeQR.failedMembers = set(
            ['node3FEMeQR_fm_1', 'node3FEMeQR_fm_2'])

        self.node3XFEMmpLF.successfulMembers = set(
            ['node3XFEMmpLF_sm_1', 'node3XFEMmpLF_sm_2'])
        self.node3XFEMmpLF.failedMembers = set(
            ['node3XFEMmpLF_fm_1', 'node3XFEMmpLF_fm_2', 'node3XFEMmpLF_fm_3'])
# branch 5.0
        self.node5XFEMcpLT.successfulMembers = set(
            ['node5XFEMcpLT_sm_1', 'node5XFEMcpLT_sm_2'])
        self.node5XFEMcpLT.failedMembers = set(
            ['node5XFEMcpLT_fm_1', 'node5XFEMcpLT_fm_2', 'node5XFEMcpLT_fm_3'])
# branch 10.0
        self.node10FEMeQF.successfulMembers = set(
            ['node10FEMeQF_sm_1', 'node10FEMeQF_sm_2'])
        self.node10FEMeQF.failedMembers = set(
            ['node10FEMeQF_fm_1', 'node10FEMeQF_fm_2'])
        self.node10FEMeLF.successfulMembers = set(
            ['node10FEMeLF_sm_1', 'node10FEMeLF_sm_2', 'node10FEMeLF_sm_3'])
        self.node10FEMeLF.failedMembers = set(
            ['node10FEMeLF_fm_1', 'node10FEMeLF_fm_2', 'node10FEMeLF_fm_3'])

        # self.node10XFEMcpLR.successfulMembers = set([])
        self.node10XFEMcpLR.failedMembers = set(
            ['node10XFEMcpLR_fm_1', 'node10XFEMcpLR_fm_2'])


class TestTreeSetUp(TreeSetUp):

    def test_treeSetUp_root_node(self):
        self.assertIsNone(self.root.getParent())
        exp = set([self.node1, self.node2, self.node3, self.node5, self.node10])
        self.assertEqual(exp, set(self.root.getChildren()))
        exp = set(['1.0', '2.0', '3.0', '5.0', '10.0'])
        self.assertEqual(exp, set([n.getName()
                                   for n in self.root.getChildren()]))

    def test_node1(self):
        self.assertIs(self.root, self.node1.getParent())
        self.assertEqual('1.0', self.node1.getName())
        self.assertEqual(set(['FEM', 'XFEM']),
                         set([n.getName() for n in self.node1.getChildren()]))
        self.assertEqual(set([self.node1FEM, self.node1XFEM]),
                         set(self.node1.getChildren()))

    def test_node1_FEM_branch(self):
        self.assertEqual('FEM', self.node1FEM.getName())
        self.assertIs(self.node1, self.node1FEM.getParent())
        self.assertEqual(set([self.node1FEMe, self.node1FEMs]),
                         set(self.node1FEM.getChildren()))
        self.assertEqual('scale', self.node1FEMs.getName())
        self.assertEqual('elliptic', self.node1FEMe.getName())

        self.assertIs(self.node1FEM, self.node1FEMs.getParent())
        self.assertEqual(set([self.node1FEMsQR, self.node1FEMsLR]),
                         set(self.node1FEMs.getChildren()))
        self.assertEqual('QR', self.node1FEMsQR.getName())
        self.assertIs(self.node1FEMs, self.node1FEMsQR.getParent())
        self.assertEqual('LR', self.node1FEMsLR.getName())
        self.assertIs(self.node1FEMs, self.node1FEMsLR.getParent())

        self.assertIs(self.node1FEM, self.node1FEMe.getParent())
        self.assertEqual(set([self.node1FEMeQF, self.node1FEMeLF]),
                         set(self.node1FEMe.getChildren()))
        self.assertEqual('QF', self.node1FEMeQF.getName())
        self.assertIs(self.node1FEMe, self.node1FEMeQF.getParent())
        self.assertEqual('LF', self.node1FEMeLF.getName())
        self.assertIs(self.node1FEMe, self.node1FEMeLF.getParent())
        self.assertEqual([], self.node1FEMsQR.getChildren())
        self.assertEqual([], self.node1FEMsLR.getChildren())
        self.assertEqual([], self.node1FEMeQF.getChildren())
        self.assertEqual([], self.node1FEMeLF.getChildren())

    def test_node1_XFEM_branch(self):
        self.assertEqual('XFEM', self.node1XFEM.getName())
        self.assertIs(self.node1, self.node1XFEM.getParent())
        self.assertEqual(set([self.node1XFEMcp, self.node1XFEMmp]),
                         set(self.node1XFEM.getChildren()))
        self.assertEqual('cp', self.node1XFEMcp.getName())
        self.assertEqual('mp', self.node1XFEMmp.getName())
        self.assertIs(self.node1XFEM, self.node1XFEMmp.getParent())

        self.assertIs(self.node1XFEM, self.node1XFEMcp.getParent())
        self.assertEqual([self.node1XFEMcpLT], self.node1XFEMcp.getChildren())
        self.assertIs(self.node1XFEMcp, self.node1XFEMcpLT.getParent())
        self.assertEqual('LT', self.node1XFEMcpLT.getName())

        self.assertIs(self.node1XFEM, self.node1XFEMmp.getParent())
        self.assertEqual([self.node1XFEMmpLR], self.node1XFEMmp.getChildren())
        self.assertIs(self.node1XFEMmp, self.node1XFEMmpLR.getParent())
        self.assertEqual('LR', self.node1XFEMmpLR.getName())

        self.assertEqual([], self.node1XFEMcpLT.getChildren())
        self.assertEqual([], self.node1XFEMmpLR.getChildren())

    def test_node2(self):
        self.assertIs(self.root, self.node2.getParent())
        self.assertEqual('2.0', self.node2.getName())
        self.assertIs(self.node2, self.node2FEM.getParent())
        self.assertEqual([self.node2FEM], self.node2.getChildren())

    def test_node2_FEM_branch(self):
        self.assertEqual('FEM', self.node2FEM.getName())
        self.assertIs(self.node2FEM, self.node2FEMs.getParent())
        self.assertEqual([self.node2FEMs], self.node2FEM.getChildren())
        self.assertEqual('scale', self.node2FEMs.getName())
        self.assertEqual([self.node2FEMsQF], self.node2FEMs.getChildren())
        self.assertIs(self.node2FEMs, self.node2FEMsQF.getParent())
        self.assertEqual('QF', self.node2FEMsQF.getName())
        self.assertEqual([], self.node2FEMsQF.getChildren())

    def test_node3(self):
        self.assertIs(self.root, self.node3.getParent())
        self.assertEqual('3.0', self.node3.getName())
        self.assertIs(self.node3, self.node3FEM.getParent())
        self.assertIs(self.node3, self.node3XFEM.getParent())
        self.assertEqual(set([self.node3FEM, self.node3XFEM]),
                         set(self.node3.getChildren()))

    def test_node3_FEM_branch(self):
        self.assertEqual('FEM', self.node3FEM.getName())
        self.assertEqual([self.node3FEMe], self.node3FEM.getChildren())
        self.assertEqual('elliptic', self.node3FEMe.getName())
        self.assertIs(self.node3FEM, self.node3FEMe.getParent())
        self.assertEqual([self.node3FEMeQR], self.node3FEMe.getChildren())
        self.assertEqual('QR', self.node3FEMeQR.getName())
        self.assertIs(self.node3FEMe, self.node3FEMeQR.getParent())
        self.assertEqual([], self.node3FEMeQR.getChildren())

    def test_node3_XFEM_branch(self):
        self.assertEqual('XFEM', self.node3XFEM.getName())
        self.assertEqual([self.node3XFEMmp], self.node3XFEM.getChildren())
        self.assertIs(self.node3XFEM, self.node3XFEMmp.getParent())
        self.assertEqual('mp', self.node3XFEMmp.getName())
        self.assertEqual([self.node3XFEMmpLF], self.node3XFEMmp.getChildren())
        self.assertIs(self.node3XFEMmp, self.node3XFEMmpLF.getParent())
        self.assertEqual('LF', self.node3XFEMmpLF.getName())
        self.assertEqual([], self.node3XFEMmpLF.getChildren())

    def test_node5(self):
        self.assertIs(self.root, self.node5.getParent())
        self.assertEqual('5.0', self.node5.getName())
        self.assertEqual([self.node5XFEM], self.node5.getChildren())
        self.assertIs(self.node5, self.node5XFEM.getParent())

    def test_node5_XFEM_branch(self):
        self.assertEqual('XFEM', self.node5XFEM.getName())
        self.assertEqual([self.node5XFEMcp], self.node5XFEM.getChildren())
        self.assertEqual('cp', self.node5XFEMcp.getName())
        self.assertIs(self.node5XFEM, self.node5XFEMcp.getParent())
        self.assertEqual([self.node5XFEMcpLT], self.node5XFEMcp.getChildren())
        self.assertEqual('LT', self.node5XFEMcpLT.getName())
        self.assertIs(self.node5XFEMcp, self.node5XFEMcpLT.getParent())
        self.assertEqual([], self.node5XFEMcpLT.getChildren())

    def test_node10(self):
        self.assertIs(self.root, self.node10.getParent())
        self.assertEqual('10.0', self.node10.getName())
        self.assertEqual(set([self.node10XFEM, self.node10FEM]),
                         set(self.node10.getChildren()))

    def test_node10_FEM_branch(self):
        self.assertEqual('FEM', self.node10FEM.getName())
        self.assertIs(self.node10, self.node10FEM.getParent())
        self.assertEqual([self.node10FEMe], self.node10FEM.getChildren())
        self.assertEqual('elliptic', self.node10FEMe.getName())
        self.assertIs(self.node10FEM, self.node10FEMe.getParent())
        self.assertEqual(set([self.node10FEMeQF, self.node10FEMeLF]),
                         set(self.node10FEMe.getChildren()))

        self.assertEqual('QF', self.node10FEMeQF.getName())
        self.assertIs(self.node10FEMe, self.node10FEMeQF.getParent())

        self.assertEqual('LF', self.node10FEMeLF.getName())
        self.assertIs(self.node10FEMe, self.node10FEMeQF.getParent())

        self.assertEqual([], self.node10FEMeQF.getChildren())
        self.assertEqual([], self.node10FEMeLF.getChildren())

    def test_node10_XFEM_branch(self):
        self.assertEqual('XFEM', self.node10XFEM.getName())
        self.assertIs(self.node10, self.node10XFEM.getParent())
        self.assertEqual([self.node10XFEMcp], self.node10XFEM.getChildren())
        self.assertEqual('cp', self.node10XFEMcp.getName())
        self.assertIs(self.node10XFEM, self.node10XFEMcp.getParent())
        self.assertEqual([self.node10XFEMcpLR],
                         self.node10XFEMcp.getChildren())
        self.assertEqual('LR', self.node10XFEMcpLR.getName())
        self.assertIs(self.node10XFEMcp, self.node10XFEMcpLR.getParent())
        self.assertEqual([], self.node10XFEMcpLR.getChildren())

    def test_simIds_on_leaf_nodes_1_FEM(self):
        node1FEMmembers(self)

    def test_simIds_on_leaf_nodes_1_XFEM(self):
        node1XFEMmembers(self)

    def test_simIds_on_leaf_nodes_2_FEM(self):
        node2FEMmembers(self)

    def test_simIds_on_leaf_nodes_3_FEM(self):
        node3FEMmembers(self)

    def test_simIds_on_leaf_nodes_3_XFEM(self):
        node3XFEMmembers(self)

    def test_simIds_on_leaf_nodes_5_XFEM(self):
        node5XFEMmembers(self)

    def test_simIds_on_leaf_nodes_10_FEM(self):
        node10FEMmembers(self)

    def test_simIds_on_leaf_nodes_10_XFEM(self):
        node10XFEMmembers(self)


def node1FEMmembers(self):
    self.assertEqual(set(['node1FEMsQR_sm_1', 'node1FEMsQR_sm_2']),
                     self.node1FEMsQR.getSuccessfulMembers())
    self.assertEqual(set(['node1FEMsQR_fm_1']),
                     self.node1FEMsQR.getFailedMembers())
    self.assertEqual(set(['node1FEMsLR_sm_1']),
                     self.node1FEMsLR.getSuccessfulMembers())
    self.assertEqual(set(['node1FEMsLR_fm_1']),
                     self.node1FEMsLR.getFailedMembers())

    self.assertEqual(set(['node1FEMeQF_sm_1']),
                     self.node1FEMeQF.getSuccessfulMembers())
    self.assertEqual(set(['node1FEMeQF_fm_1', 'node1FEMeQF_fm_2']),
                     self.node1FEMeQF.getFailedMembers())
    self.assertEqual(
        set(['node1FEMeLF_sm_1', 'node1FEMeLF_sm_2', 'node1FEMeLF_sm_3']),
        self.node1FEMeLF.getSuccessfulMembers())
    self.assertEqual(set(['node1FEMeLF_fm_1']),
                     self.node1FEMeLF.getFailedMembers())


def node1XFEMmembers(self):
    self.assertEqual(set([
        'node1XFEMcpLT_sm_1', 'node1XFEMcpLT_sm_2', 'node1XFEMcpLT_sm_3']),
        self.node1XFEMcpLT.getSuccessfulMembers())
    self.assertEqual(set(['node1XFEMcpLT_fm_1']),
                     self.node1XFEMcpLT.getFailedMembers())
    self.assertEqual(set(['node1XFEMmpLR_sm_1', 'node1XFEMmpLR_sm_2']),
                     self.node1XFEMmpLR.getSuccessfulMembers())
    self.assertEqual(set(['node1XFEMmpLR_fm_1']),
                     self.node1XFEMmpLR.getFailedMembers())


def node2FEMmembers(self):
    self.assertEqual(set(['node2FEMsQF_sm_1', 'node2FEMsQF_sm_2']),
                     self.node2FEMsQF.getSuccessfulMembers())
    self.assertEqual(set([]), self.node2FEMsQF.getFailedMembers())


def node3FEMmembers(self):
    self.assertEqual(set(['node3FEMeQR_sm_1']),
                     self.node3FEMeQR.getSuccessfulMembers())
    self.assertEqual(set(['node3FEMeQR_fm_1', 'node3FEMeQR_fm_2']),
                     self.node3FEMeQR.getFailedMembers())


def node3XFEMmembers(self):
    self.assertEqual(set(['node3XFEMmpLF_sm_1', 'node3XFEMmpLF_sm_2']),
                     self.node3XFEMmpLF.getSuccessfulMembers())
    self.assertEqual(set([
        'node3XFEMmpLF_fm_1', 'node3XFEMmpLF_fm_2', 'node3XFEMmpLF_fm_3']),
        self.node3XFEMmpLF.getFailedMembers())


def node5XFEMmembers(self):
    self.assertEqual(set(['node5XFEMcpLT_sm_1', 'node5XFEMcpLT_sm_2']),
                     self.node5XFEMcpLT.getSuccessfulMembers())
    self.assertEqual(set([
        'node5XFEMcpLT_fm_1', 'node5XFEMcpLT_fm_2', 'node5XFEMcpLT_fm_3']),
        self.node5XFEMcpLT.getFailedMembers())


def node10FEMmembers(self):
    self.assertEqual(set(['node10FEMeQF_sm_1', 'node10FEMeQF_sm_2']),
                     self.node10FEMeQF.getSuccessfulMembers())
    self.assertEqual(set(['node10FEMeQF_fm_1', 'node10FEMeQF_fm_2']),
                     self.node10FEMeQF.getFailedMembers())
    self.assertEqual(
        set(['node10FEMeLF_sm_1', 'node10FEMeLF_sm_2', 'node10FEMeLF_sm_3']),
        self.node10FEMeLF.getSuccessfulMembers())
    self.assertEqual(
        set(['node10FEMeLF_fm_1', 'node10FEMeLF_fm_2', 'node10FEMeLF_fm_3']),
        self.node10FEMeLF.getFailedMembers())


def node10XFEMmembers(self):
    self.assertEqual(set([]), self.node10XFEMcpLR.getSuccessfulMembers())
    self.assertEqual(set(['node10XFEMcpLR_fm_1', 'node10XFEMcpLR_fm_2']),
                     self.node10XFEMcpLR.getFailedMembers())
