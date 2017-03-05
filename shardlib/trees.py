import dbaccess as dba
import dataProcessing as dp
import numpy as np
import time
import colorsys
import copy
from types import *

colLabels = ['Lvl', 'Branch', 'Total', 'Succ.', 'Fail', 'Graph']
treeRootNodeName = 'All analyses'
treeLevelParameterNames = [
    'crackRatio',
    'analysisType',
    'modelType',
    'elements']


class TreeNode(object):

    def __init__(self, name):
        self.name = name
        self.parent = None
        self.children = []
        self.failedMembers = set()
        self.successfulMembers = set()
        self.xmark = 0
        self.barWidth = 0
        self.legendName = ''
        self.faceColor = '0.9'
        self.edgeColor = '0.0'
        self.hueRange = []
        self.currentMarker = '<--'
        self.cols = colLabels

    def setParent(self, parent):
        if (isinstance(parent, NoneType) or
                isinstance(parent, TreeNode)):
            self.parent = parent
        else:
            raise TypeError('parent must be wither NoneType or TreeNode')

    def setChild(self, child):
        if isinstance(child, TreeNode):
            self.children.append(child)
            self.sortChildren()
        else:
            raise TypeError('child must be wither NoneType or TreeNode')

    def sortChildren(self):
        try:
            self.children.sort(key=lambda k: float(k.getName()))
        except ValueError:
            self.children.sort(key=lambda k: k.getName())

    def addMembers(self, members, memberType):
        assert memberType in ['successful', 'failed']
        assert isinstance(
            members, (NoneType, str, list, tuple, set, frozenset))
        setsDict = {'successful': self.successfulMembers,
                    'failed': self.failedMembers}
        if isinstance(members, NoneType):
            pass
        elif isinstance(members, str):
            setsDict[memberType].add(members)
        else:
            for m in members:
                setsDict[memberType].add(m)

    def addFailedMember(self, member):
        # self.failedMembers.add(member)
        self.addMembers(member, 'failed')

    def addSuccessfulMember(self, member):
        # self.successfulMembers.add(member)
        self.addMembers(member, 'successful')

    def setXMark(self, mark):
        self.xmark = mark

    def setBarWidth(self, width):
        self.barWidth = width

    def setLegendName(self, name):
        self.legendName = name

    def setFaceColor(self, color):
        self.faceColor = color

    def setEdgeColor(self, color):
        self.edgeColor = color

    def setHueRange(self, hueRange):
        self.hueRange = hueRange

    def addMember(self, entryObj):
        key = entryObj.getEntryKey()
        if entryObj.getAnalysisSuccess():
            self.addSuccessfulMember(key)
        else:
            self.addFailedMember(key)

    def assignMemberAsFailed(self, simId, printChanges=True, rowlen=80):
        assert isinstance(simId, str)
        root = self.getRootNode()
        leaves = self.getChildLeafNodes(root)
        for l in leaves:
            if simId in l.successfulMembers:
                l.successfulMembers.remove(simId)
                l.failedMembers.add(simId)
                if printChanges:
                    l.printNode(l, rowlen)
                return 1
            if simId in l.failedMembers:
                pass
        return 0

    def getParent(self):
        return self.parent

    def getChildren(self):
        return self.children

    def getName(self):
        return self.name

    def getChildLeafNodes(self, node):
        stack = [node]
        leaves = []
        while len(stack) > 0:
            tmp = stack.pop()
            if tmp.getChildren() == [] and tmp != node:
                leaves.append(tmp)
            stack = tmp.getChildren() + stack
        return leaves

    def getSuccessfulMembers(self):
        def getSM(node):
            if node.getChildren() == []:
                return node.successfulMembers
            else:
                ch = node.getChildren()
                return frozenset().union(*[getSM(c) for c in ch])
        return copy.deepcopy(getSM(self))

    def getFailedMembers(self):
        def getSM(node):
            if node.getChildren() == []:
                return node.failedMembers
            else:
                ch = node.getChildren()
                return frozenset().union(*[getSM(c) for c in ch])
        return copy.deepcopy(getSM(self))

    def getAllMembers(self):
        return self.getFailedMembers() | self.getSuccessfulMembers()

    def getXMark(self):
        return self.xmark

    def getBarWidth(self):
        return self.barWidth

    def getFaceColor(self):
        return self.faceColor

    def getEdgeColor(self):
        return self.edgeColor

    def getHueRange(self):
        return self.hueRange

    def getLegendName(self):
        return self.legendName

    def getRootNode(self):
        root = self
        while root.getParent():
            root = root.getParent()
        return root

    def hasChildNode(self, nodeName):
        for child in self.getChildren():
            if child.getName() == nodeName:
                return child
        return False

    def getNodeLevelInTree(self):
        if self.getParent():
            return 1 + self.getParent().getNodeLevelInTree()
        else:
            return 0

    def getNodeLevel(self, node):
        path = tracePath(node)
        return len(path) - 1

    def getChildrenOfBranch(self, branchNames):
        return self.getTreeBranch(branchNames).getChildren()

    def getTreeBranch(self, branchNames):
        stack = [self.getRootNode()]
        nodes = []
        ind1 = -(len(branchNames))
        while len(stack) > 0:
            tmp = stack.pop()
            path = tracePath(tmp)
            nodeNames = [a.getName() for a in path]
            if nodeNames[ind1:] == branchNames:
                nodes.append(tmp)
            stack = tmp.getChildren() + stack
        if len(nodes) == 1:
            return nodes[0]
        elif len(nodes) > 1:
            raise KeyError(
                '{0} is ambiguous. Corresponds to more than one node.'.format(
                    branchNames))
        else:
            raise KeyError('{0} not in the tree'.format(branchNames))

    def countNumberOfTreeLevels(self):
        maxLevel = 0
        stack = [self.getRootNode()]
        while len(stack) > 0:
            tmp = stack.pop()
            lvl = self.getNodeLevel(tmp)
            if lvl > maxLevel:
                maxLevel = lvl
            stack = tmp.getChildren() + stack
        return maxLevel

    def countMaxNodeNameLength(self):
        maxLen = 0
        stack = [self.getRootNode()]
        while len(stack) > 0:
            tmp = stack.pop()
            name = self.createNameStr(tmp)
            if len(name) + 1 > maxLen:
                maxLen = len(name) + 1
            stack = tmp.getChildren() + stack
        return maxLen

    def getMemberCounts(self, node):
        tot, succ, failed = 0, 0, 0
        succ = len(node.getSuccessfulMembers())
        failed = len(node.getFailedMembers())
        tot = succ + failed
        return [tot, succ, failed]

    def getMaxMemberCounts(self):
        return self.getMemberCounts(self.getRootNode())

    def calcColumnsLength(self, rowlen):
        lengths = [self.countNumberOfTreeLevels(), self.countMaxNodeNameLength(
        )] + [len(str(a)) for a in self.getMaxMemberCounts()]
        for i in range(len(self.cols) - 1):
            if len(self.cols[i]) > lengths[i]:
                lengths[i] = len(self.cols[i])
        lengths.append(rowlen - sum(lengths))
        return lengths

    def printTitle(self, rowlen):
        row = ''
        sep = ''
        lens = self.calcColumnsLength(rowlen)
        for i in range(len(self.cols)):
            colStr = self.createAlignedColStr(
                self.cols[i], lens[i], 'center')
            row = row + '|' + colStr
            sep = sep + '|' + lens[i] * '-'
        print row
        print sep

    def createAlignedColStr(self, value, colLen, align):
        assert align in ['left', 'center', 'right']
        vl = len(str(value))
        if align == 'center':
            f = (colLen - vl) / 2
            b = colLen - vl - f
        elif align == 'right':
            b = 1
            f = colLen - vl - b
        elif align == 'left':
            f = 0
            b = colLen - vl - f
        colStr = f * ' ' + str(value) + b * ' '
        return colStr

    def createNameStr(self, node):
        level = self.getNodeLevel(node)
        isCurrent = (self == node)
        nodeName = str(node.getName())
        nameStr = level * '-' + ' ' + nodeName
        if isCurrent:
            nameStr = nameStr + ' ' + self.currentMarker
        return nameStr

    def createBarGraph(self, node, length):
        mt, ms, mf = self.getMaxMemberCounts()
        t, s, f = self.getMemberCounts(node)
        l = (length - 2) * float(t) / mt
        plen = int(l * s / t)
        mlen = int(l - plen)
        blanks = int(l - (plen + mlen))
        return '[' + plen * '+' + mlen * '-' + blanks * ' ' + ']'

    def printNode(self, node, rowlen):
        lens = self.calcColumnsLength(rowlen)
        row = ''
        total, succ, failed = self.getMemberCounts(node)
        ncols = [self.getNodeLevel(node), self.createNameStr(node),
                 total, succ, failed]
        alignment = ['right', 'left', 'right', 'right', 'right']
        for i in range(len(ncols)):
            row = row + '|' + self.createAlignedColStr(
                ncols[i], lens[i], alignment[i])
        row = row + '|' + self.createBarGraph(node, lens[-1])
        print row

    def printStats2(self, rowlen=80):
        self.printTitle(rowlen)
        path = tracePath(self)
        for node in path:
            if node is not self:
                self.printNode(node, rowlen)
            else:
                break
        stack = [self]
        while len(stack) > 0:
            tmp = stack.pop()
            self.printNode(tmp, rowlen)
            stack = stack + tmp.getChildren()

    def printStructure(self):
        root = self.getRootNode()
        stack = [root]
        while len(stack) > 0:
            print generateNodePrStr(stack[0], stack[0] is self)
            temp = stack.pop(0)
            stack = temp.getChildren() + stack

    def __eq__(self, other):
        assert isinstance(self, type(other))
        return self.getName() == other.getName()

    def __str__(self):
        return self.name

    def printStats(self, maxChars=80):
        root = self.getRootNode()
        maxLen = 0
        stack = [root]
        while len(stack) > 0:
            nodePrStr = generateNodePrStr(stack[0], stack[0] is self)
            if len(nodePrStr) > maxLen:
                maxLen = len(nodePrStr)
            temp = stack.pop(0)
            stack = temp.getChildren() + stack
        print genNodePrintStrWithBar(
            root, root, root is self, maxLen, maxChars)
        for node in root.getChildren():
            stack = [node]
            while len(stack) > 0:
                print genNodePrintStrWithBar(
                    stack[0], node, stack[0] is self, maxLen, maxChars)
                temp = stack.pop(0)
                stack = temp.getChildren() + stack


def createTreeFromDbKeys(dbKeys):
    root = TreeNode(treeRootNodeName)
    for key in dbKeys:
        parent = root
        anDataObj = dp.AnalysisData(key)

        for tlevel in treeLevelParameterNames:
            nodeName = anDataObj.getParameter(tlevel)
            node = parent.hasChildNode(nodeName)
            if not node:
                node = TreeNode(nodeName)
                node.setParent(parent)
                parent.setChild(node)
            if tlevel == treeLevelParameterNames[-1]:
                node.addMember(anDataObj)
            parent = node
    return root


def nodesPerLevel(root):
    stack = [root]
    levelNodes = {}
    while len(stack) > 0:
        level = stack[0].getNodeLevelInTree()
        if level not in levelNodes.keys():
            levelNodes[level] = set()
        levelNodes[level].add(stack[0])
        temp = stack.pop(0)
        stack = stack + temp.getChildren()
    return levelNodes


def tracePath(node, limitLevel=0):
    def getPathToRoot(node):
        if not node.getParent():
            return [node]
        else:
            return getPathToRoot(node.getParent()) + [node]
    path = getPathToRoot(node)
    if (limitLevel <= len(path) and limitLevel >= 0) or limitLevel is None:
        return path[limitLevel:]
    else:
        raise IndexError(
            'limitLevel argument must be >= 0 and <= {0}'.format(
                len(path)))


def createTreeOfKeys(root):
    leaves = nodesPerLevel(root)
    leaves = leaves[max(leaves.keys())]
    nroot = TreeNode('analyses')
    for leaf in leaves:
        path = tracePath(leaf, 2)
        parent = nroot
        for node in path:
            if node.getName() not in [a.getName()
                                      for a in parent.getChildren()]:
                newNode = TreeNode(node.getName())
                newNode.setParent(parent)
                parent.setChild(newNode)
            for n in parent.getChildren():
                if n == node:
                    parent = n
    return nroot


def maxNodesPerLevel(root):
    maxChildren = {0: 1}
    stack = [root]
    while len(stack) > 0:
        level = stack[0].getNodeLevelInTree() + 1
        if len(stack[0].getChildren()) > maxChildren.get(level, 0):
            maxChildren[level] = len(stack[0].getChildren())
        temp = stack.pop(0)
        stack = stack + temp.getChildren()
    return maxChildren


def nodeNamesPerLevel(root):
    levelNodes = nodesPerLevel(root)
    namedNodes = {}
    for key in levelNodes.keys():
        nodes = list(levelNodes[key])
        namedNodes[key] = set()
        for node in nodes:
            namedNodes[key].add(node.getName())
    for key in namedNodes.keys():
        namedNodes[key] = sorted(namedNodes[key])
    return namedNodes


def generateNodePrStr(node, current):
    level = node.getNodeLevelInTree()
    if level < 9:
        number = '  ' + str(level)
    elif level > 9 and level < 99:
        number = ' ' + str(level)
    else:
        number = str(level)
    branch = level * ' ' + '|' + '-'
    branch = '|' + level * '-'
    if current:
        nodeName = node.getName() + ' <--'
    else:
        nodeName = node.getName()
    return "{0} {1} {2}".format(number, branch, nodeName)


def genNodePrintStrWithBar(
        node, root, current, maxStrLen, maxChars):
    if (len(node.getSuccessfulMembers()) +
            len(node.getFailedMembers()) > 0):
        barLength = maxChars - maxStrLen - 3
        s, f, b = calcNodeBarNumbers(node, root, barLength)
        nodeStr = generateNodePrStr(node, current)
        blankSpace = maxChars - len(nodeStr) - s - f - b - 2
        nps = '{0}{1}[{2}{3}{4}]'.format(
            nodeStr, blankSpace * ' ', s * '+', f * '-', b * ' ')
        return nps
    else:
        return generateNodePrStr(node, current)


def calcNodeBarNumbers(node, root, barLength):
    nsm = len(node.getSuccessfulMembers())
    nfm = len(node.getFailedMembers())
    totm = (len(root.getSuccessfulMembers()) +
            len(root.getFailedMembers()))
    barUnitLen = barLength / float(totm)
    totBarUnits = int(round(barUnitLen * (nsm + nfm)))
    sBarUnits = int(round(barUnitLen * nsm))
    fBarUnits = totBarUnits - sBarUnits
    blankBarUnits = barLength - totBarUnits
    return sBarUnits, fBarUnits, blankBarUnits


def calcBarWidth(node, refTree,
                 ulen=1.0, relPad=0.05, root=None, tlevelIncrement=1):
    if not root:
        root = node.getRootNode()
    if node is not root:
        maxNodes = maxNodesPerLevel(refTree)
        nodeLevel = node.getNodeLevelInTree()
        numNodes = maxNodes[nodeLevel - tlevelIncrement]
        ulen = node.getParent().getBarWidth()
        barWidth = (1 - (numNodes + 1) * relPad) * ulen / numNodes
    else:
        barWidth = (1 - 2 * relPad) * ulen
    node.setBarWidth(barWidth)


def getRefSiblingsOfNode(node, refTree):
    candidates = []
    stack = [refTree]
    while len(stack) > 0:
        if stack[0] == node:
            candidates.append(stack[0])
        temp = stack.pop(0)
        stack = temp.getChildren() + stack
    parent = node.getParent()
    for c in candidates:
        if ((parent == c.getParent()) or
                (c.getParent() is refTree)):
            return c.getParent().getChildren(), c


def calcXMark(node, refTree):
    parent = node.getParent()
    pxmark = parent.getXMark()
    refSiblings, rs = getRefSiblingsOfNode(node, refTree)
    index = refSiblings.index(rs)
    n = len(refSiblings)
    pbw = parent.getBarWidth()
    a = node.getBarWidth()
    b = (pbw - a * n) / float(n + 1)
    c = pxmark + b * (index + 1) + a * index
    node.setXMark(c)


def assignBarWidthsAndMarks(root, refTree, ulen=1.0, relPad=0.05):
    valNodes = root.getChildren()
    count = 0
    for node in valNodes:
        stack = [node]
        while len(stack) > 0:
            calcBarWidth(stack[0], refTree,
                         ulen, relPad, node, 1)
            if stack[0] is node:
                stack[0].setXMark((count + relPad) * ulen)
            else:
                calcXMark(stack[0], refTree)
            temp = stack.pop(0)
            stack = stack + temp.getChildren()
        count += 1


def setLegendName(node):
    if node is node.getRootNode():
        return None
    name = node.getName()
    analyses = ['FEM', 'XFEM']
    elements = ['LinearTet', 'LinearRI', 'LinearFI']
    types = {
        'crackPartition': 'CP - xfem',
        'multiplePartitions': 'MP - xfem', 'simple': 'S - xfem',
        'elliptic': 'Elliptic tr.', 'simpleScale': 'Scale tr.'}
    if name in analyses:
        node.setLegendName('{0} - {1}'.format(name, 'analyses'))
    elif name in elements:
        n2 = node.getParent().getParent().getName()
        node.setLegendName('{0} - {1}'.format(name, n2))
    elif name in types.keys():
        node.setLegendName(types[name])
    elif node.getParent() == node.getRootNode():
        node.setLegendName('All analyses')


def assignLegendNames(root):
    stack = [root]
    while len(stack) > 0:
        setLegendName(stack[0])
        temp = stack.pop(0)
        stack = stack + temp.getChildren()


def setColorForNode(node, refNode, refTree):
    level = node.getNodeLevelInTree() - refNode.getNodeLevelInTree()
    n = 1000
    if node is refNode:
        hueRange = list(range(n))
    else:
        refSiblings, rc = getRefSiblingsOfNode(node, refTree)
        lrs = len(refSiblings)
        hueRange = node.getParent().getHueRange()
        start = len(hueRange) / lrs * refSiblings.index(rc)
        end = len(hueRange) / lrs * (1 + refSiblings.index(rc))
        hueRange = hueRange[start:end]

    h = hueRange[int(len(hueRange) / 2)] / float(n)
    s = 1.0 - 1 / float(1 + level)
    v = 0.9 / float(level + 1)
    node.setHueRange(hueRange)
    rgb = colorsys.hsv_to_rgb(h, s, v)
    node.setFaceColor(rgb)
    if node is refNode:
        rgb = colorsys.hsv_to_rgb(h, 0., 0.)
    else:
        rgb = colorsys.hsv_to_rgb(h, 1.0, 1.0)
    node.setEdgeColor(rgb)


def barPlot(root, refTree, fig):
    ax = fig.add_subplot(111)
    bars = {}
    totals = []
    count = 1
    for node in root.getChildren():
        stack = [node]
        cc = 1
        totals.append(node.getName())
        while len(stack) > 0:
            color = str(0.9 / cc)
            setColorForNode(stack[0], node, refTree)
            color = stack[0].getFaceColor()
            ec_color = stack[0].getEdgeColor()
            bars[stack[0].getLegendName()] = ax.bar(
                                        stack[0].getXMark(),
                                        len(stack[0].getSuccessfulMembers()),
                                        width=stack[0].getBarWidth(),
                                        color=color,
                                        ec=ec_color)
            bars['Errors'] = ax.bar(
                                stack[0].getXMark(),
                                len(stack[0].getFailedMembers()),
                                width=stack[0].getBarWidth(),
                                bottom=len(stack[0].getSuccessfulMembers()),
                                color='DarkRed',
                                ec='red')
            temp = stack.pop(0)
            stack = stack + temp.getChildren()
            cc += 1
    ax.legend([bars[k] for k in sorted(bars.keys())], sorted(bars.keys()),
              bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0)
    ax.set_xticks([0.5 + i for i in range(len(totals))])
    ax.set_xticklabels(totals)
    ax.set_xlabel('Crack ratio')
    ax.set_ylabel('Number of simulations')
    ax.set_title('Database summary')
    ax.grid(True)


def plot(root, refTree, fig):
    assignBarWidthsAndMarks(root, refTree)
    assignLegendNames(root)
    barPlot(root, refTree, fig)


def getTreeLeaves(root):
    root = root.getRootNode()
    stack = [root]
    leaves = []
    while len(stack) > 0:
        temp = stack.pop()
        stack = temp.getChildren() + stack
        if len(temp.getChildren()) == 0:
            leaves.append(temp)
    return leaves
