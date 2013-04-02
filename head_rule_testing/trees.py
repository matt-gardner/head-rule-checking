#!/usr/bin/env python


class Tree(object):
    def __init__(self, root):
        self.root = root

    def copy(self):
        return Tree(self.root.copy())

    def pretty(self):
        return self.root.pretty(0)

    @classmethod
    def read(cls, text):
        current_node = None
        root = None
        c = 0
        while c < len(text):
            if text[c] == '(':
                end = c
                while text[end] not in ' \n':
                    end += 1
                label = text[c+1:end]
                new_node = Node(label, current_node, False)
                if current_node == None:
                    root = new_node
                current_node = new_node
                c = end
            elif text[c] == ')':
                current_node = current_node.parent
            elif text[c] not in ' \n':
                end = c
                while text[end] != ')':
                    end += 1
                label = text[c:end]
                c = end
                Node(label, current_node, True)
                current_node = current_node.parent
            c += 1
        return cls(root)


class Node(object):
    def __init__(self, label, parent, terminal_index=None):
        self.label = label
        self.parent = parent
        if parent:
            parent.children.append(self)
        self.terminal_index = terminal_index
        self.children = []

    def terminal_indices(self):
        indices = []
        if self.terminal_index is not None:
            indices.append(self.terminal_index)
        else:
            for child in self.children:
                indices.extend(child.terminal_indices())
        return indices

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def copy(self):
        """If this method is called, we assume that you want a copy with this
        node as the root, i.e., self.parent == None."""
        copy = Node(self.label, None, self.terminal_index)
        for child in self.children:
            child_copy = child.copy()
            # Because we don't retain parent relationships in the copy method,
            # we have to reset them here.
            child_copy.parent = copy
            copy.children.append(child_copy)
        return copy

    def pretty(self, indent=0):
        text = ''
        if not self.terminal_index:
            if indent != 0:
                text += '\n'
            for i in range(indent):
                text += '  '
            text +=  '('
        else:
            text += ' '
        text += self.label
        for child in self.children:
            text += child.pretty(indent+1)
        if not self.terminal_index:
            text += ')'
        return text



# vim: et sw=4 sts=4
