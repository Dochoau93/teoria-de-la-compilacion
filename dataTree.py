###< 2016-08-28 18:12:00.903563 >###

""" DataTree for Python

This module implements a generic tree data structure for storing and
retrieving hierarchical information.

This data structure is used to store the information generated
during the compilation process.
"""

class TreeNode:
    def __init__(self, tag, attrib = {}):
        self.tag = tag
        self.attrib = attrib.copy()
        self._children = []
        self.text = None

    def __repr__(self):
        return '<Node {}>'.format(repr(self.tag))

    # methods operating over subelements
    def __len__(self):
        return len(self._children)

    def __iter__(self):
        return self._children.__iter__()

    def __getitem__(self, index):
        return self._children[index]

    def __setitem__(self, index, value):
        self._children[index] = value

    def __delitem__(self, index):
        del self._children[index]

    def __str__(self):
        txt = '{0}'.format(self.tag)
        if len(self.attrib):
            txt +=  ' '
            keys = sorted(list(self.attrib.keys()))
            txt += '{'
            for k in keys:
                txt += k + ': '
                txt += str(self.attrib[k])
                if k != keys[-1]:
                    txt += ', '
            txt += '}'
        if not self.text is None:
            txt += ' :' + self.text
        return txt

    def append(self, subnode):
        self._children.append(subnode)

    def extend(self, subnodes):
        self._children.extend(subnodes)

    def insert(self, index, subnode):
        self._children.insert(index, subnode)

    def find(self, match):
        for node in self._children:
            if node.tag == match:
                return node
        return None

    def findall(self, match):
        result = []
        for node in self._children:
            if node.tag == match:
                result.append(node)
        return result

    def search(self, match, key, value):
        for node in self._children:
            if node.tag == match and node.attrib[key] == value:
                return node
        return None

    def searchall(self, match, key, value):
        result = []
        for node in self._children:
            if node.tag == match and node.attrib[key] == value:
                result.append(node)
        return result


    def iter(self, tag=None):
        for e in self._children:
            yield from e.iter(tag)


    # metodos que operan sobre los atributos (dict)
    def clear(self):
        self.text = None
        self.attrib.clear()
        self._children = []

    def get(self, key, default=None):
        return self.attrib.get(key, default)

    def set(self, key, value):
        self.attrib[key] = value

    def keys(self):
        return self.attrib.keys()

    def values(self):
        return self.attrib.values()

    def items(self):
        return self.attrib.items()

# retorna el nodo creado
def SubNode(parent, tag, attrib = {}):
    parent.append(TreeNode(tag, attrib))
    return parent._children[-1]

def printTree(node):
    def printTreeNode(prefix, node, lastNode):
        print(prefix + '+-- ' + str(node))
        for i, n in enumerate(node._children):
            isLastNode = True if i == len(node._children) - 1 else False
            if lastNode == True:
                printTreeNode(prefix + '    ', n, isLastNode)
            else:
                printTreeNode(prefix + '|   ', n, isLastNode)
    printTreeNode('', node, True)

def compTree(tree1, tree2):
    import sys

    def printError(node1, node2, counter, text):
        print('Error: : ' + text)
        print('Expected: [{:03d}] '.format(counter) + ' ' + str(node1) + \
              ' with ' + str(len(node1._children)) + ' branches.')
        print('Found:    [{:03d}] '.format(counter) + ' ' + str(node2) + \
              ' with ' + str(len(node2._children)) + ' branches.')
        sys.exit()

    def compNode(node1, node2, counter):

        if node1.tag != node2.tag:
            printError(node1, node2, counter, 'Different tag')

        if node1.text != node2.text:
            printError(node1, node2, counter, 'Different text')

        keys1 = sorted(list(node1.attrib.keys()))
        keys2 = sorted(list(node2.attrib.keys()))

        if keys1 != keys2:
            printError(node1, node2, counter, 'Different keys')

        for key in keys1:
            if node1.get(key) != node2.get(key):
                printError(node1, node2, counter, 'Different values')

        if len(node1._children) != len(node2._children):
            printError(node1, node2, counter, 'Different number of branches')

        for i, (n1, n2) in enumerate(zip(node1._children, node2._children)):
            compNode(n1, n2, counter + i + 1)

    compNode(tree1, tree2, 0)
    return True
