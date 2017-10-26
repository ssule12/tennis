from node import Node
from node import BLACK
from node import RED


class Tree:
    """A red-black order statistic tree implementation.

    Attributes:
        _root: The root node of this tree.
        _size: The number of nodes currently stored in the tree.
    """

    def __init__(self):
        self._root = None
        self._size = 0

    def __len__(self):
        return self._size

    def insert(self, key, value):
        """Inserts a new node into the tree.

        Creates a new node from the provided key and values, then inserts into
        the red-black tree. Fixes any inconsistencies with the tree structure
        after insertion. Does not support NoneType keys.

        :param key: The key to insert.
        :param value: The optional value mapping for this key.
        :return: True if a new node was created, otherwise False.
        """

        # Disallow NoneType keys.
        if key is None:
            raise ValueError("Keys are not allowed to be of type None")

        # If tree does not already contain a root, simply add one in.
        if self._root is None:
            self._root = Node(key, value)
            self._size = 1
            return True

        # Locate the parent and where the node should be placed.
        node = Node(key, value)
        parent = self._root

        while parent:
            # Update node then return if same key already exists.
            if node.key == parent.key:
                parent.value = node.value
                return False

            # Otherwise keep searching for a free spot in the tree.
            if node.key < parent.key:
                if parent.left is None:
                    parent.left = node
                    break
                parent = parent.left
            else:
                if parent.right is None:
                    parent.right = node
                    break
                parent = parent.right

        # Update the node with its new parent.
        node.parent = parent

        # Fix the tree structure.
        self.__insert_repair(node)

        # Increment the size globally and of all ancestors.
        self._size += 1
        temp = parent
        while temp:
            temp.size += 1
            temp = temp.parent

        return True

    def __insert_repair(self, node):
        """Performs red-black tree insertion repairs.

        :param node: The newly inserted node.
        :return: None
        """

        # Case 2 - Do nothing if parent is black.
        while color_of(parent_of(node)) == RED:
            # Set the current state of insertion repair.
            if parent_of(node) == left_of(grandparent_of(node)):
                side_against = right_of
                rotate_towards = self.__rotate_left
                rotate_against = self.__rotate_right
            else:
                side_against = left_of
                rotate_towards = self.__rotate_right
                rotate_against = self.__rotate_left

            # Get the uncle node.
            uncle = side_against(grandparent_of(node))

            # Case 3 - When both the parent and the uncle are red:
            #          (Parent node must always be black due to case 2)
            #              1. Set the parent to black.
            #              2. Set the uncle to black.
            #              3. Set the grandparent to red.
            #              4. The grandparent may now be in violation, perform
            #                 repairs again, but this time for the grandparent.
            #              5. Repairs complete.
            #          Otherwise:
            #              1. Move to case 4.
            if color_of(uncle) == RED:
                set_color(parent_of(node), BLACK)
                set_color(uncle, BLACK)
                set_color(grandparent_of(node), RED)
                node = grandparent_of(node)
                continue

            # Case 4 - When the current node is on the "outside" of the subtree
            # Step 1   under the grandparent:
            #              1. Rotate the parent away from its relation to the
            #                 grandparent.
            #              2. Update the current node to the previous parent,
            #                 which has now become the child.
            #              3. Move to case 4, step 2.
            #          Otherwise:
            #              1. Move to case 4, step 2.
            if node == side_against(parent_of(node)):
                node = parent_of(node)
                rotate_towards(node)

            # Case 4 - The current node is now certain to be on the outside of
            # Step 2   its grandparents subtree.
            #              1. Set the parent to black.
            #              2. Set the grandparent to red.
            #              3. Rotate the grandparent away from our node.
            #              4. Move to case 1.
            set_color(parent_of(node), BLACK)
            set_color(grandparent_of(node), RED)
            rotate_against(grandparent_of(node))

        # Case 1 - Always set the root node to black.
        self._root.color = BLACK

    def find(self, key):
        """Finds the value for a key stored in the tree.

        Searches the tree for a node with a matching key, then provides the
        value of the matched node. NoneType keys are not supported.

        :param key: The key to search for.
        :return: The found node's value if found, otherwise None.
        """

        node = self.__find_node(key)

        if node:
            return node.value

        return None

    def __find_node(self, key):
        """Finds the mapped node of this key in the tree.

        :param key: The key of the node to find.
        :return: The mapped node if found, otherwise None.
        """

        if key is None:
            raise ValueError("Keys are not allowed to be of type None")

        return self._root.find(key)

    def select(self, index):
        """Finds the value of the node at the specified index.

        :param index: The position in this tree.
        :return: The node's value if found, otherwise None.
        """

        if index < 0 or index >= self._size:
            raise ValueError("Index out of bounds")

        node = self._root

        while node:
            size = node.left.size if node.left else 0

            if index == size:
                return node.value

            if index < size:
                node = node.left
            else:
                node = node.right
                index -= size + 1

    def rank(self, key):
        """Finds the index of the node mapped by the provided key.

        :param key: The key of the node to fetch the index of.
        :return: The index if this tree contains the key, otherwise None.
        """
        node = self.__find_node(key)

        if node is None:
            return None

        index = node.left.size if node.left else 0

        while node.parent:
            if node.parent.left is not node:
                index += node.parent.left.size + 1 if node.parent.left else 1
            node = node.parent

        return index

    def delete(self, key):
        """Deletes the node with the provided key.

        Finds the node in this tree with the same key mapping and removes it.
        Automatically fixes any red-black tree violations. NoneType keys are
        not supported.

        :param key: The key of the node to delete from this tree.
        :return: True if the node previously existed, otherwise False.
        """

        if self._root is None:
            return False

        node = self.__find_node(key)

        if node is None:
            return False

        # Decrement the size globally and of all ancestors.
        self._size -= 1
        temp = node.parent
        while temp:
            temp.size -= 1
            temp = temp.parent

        if node.left and node.right:
            # Find the successor to this node.
            # Decrement the size of all passed children.
            node.size -= 1
            successor = node.right

            while successor.left:
                successor.size -= 1
                successor = successor.left

            # Replace the current node with it's successor.
            node.key = successor.key
            node.value = successor.value
            node = successor

        # Find the replacement.
        replacement = node.left if node.left else node.right

        if replacement:
            # Replace the current node with it's replacement.
            replacement.parent = node.parent

            if node.parent is None:
                self._root = replacement
            elif node == node.parent.left:
                node.parent.left = replacement
            else:
                node.parent.right = replacement

            if node.color == BLACK:
                # Perform deletion fixes.
                self.__delete_repair(replacement)

            return

        # No replacement or parent found, this must be the new root node.
        if node.parent is None:
            self._root = None
            return

        if node.color == BLACK:
            # Perform deletion repairs.
            self.__delete_repair(node)

        # If the node still has a parent, remove it.
        if node.parent:
            if node is node.parent.left:
                node.parent.left = None
            elif node is node.parent.right:
                node.parent.right = None

    def __delete_repair(self, node: Node):
        """Performs red-black tree deletion repairs.

        :param node: The newly deleted node.
        :return: None
        """

        # Case 1 - When node is black and not the root node:
        #              1. Move to case 2.
        #          Otherwise:
        #              1. Ensure the root is black.
        #              2. The red black tree should be successfully repaired.
        while node is not self._root and color_of(node) == BLACK:
            # Set the current state of deletion repair.
            if node is left_of(parent_of(node)):
                side_towards = left_of
                side_against = right_of
                rotate_towards = self.__rotate_left
                rotate_against = self.__rotate_right
            else:
                side_towards = right_of
                side_against = left_of
                rotate_towards = self.__rotate_right
                rotate_against = self.__rotate_left

            # Get the sibling node.
            sibling = side_against(parent_of(node))

            # Case 2 - When sibling is red:
            #              1. Swap sibling and parent colors.
            #              2. Rotate the parent towards our node.
            #              4. Get the new sibling.
            #              3. Move to case 3.
            #          Otherwise:
            #              1. Move to case 3.
            if color_of(sibling) == RED:
                set_color(sibling, BLACK)
                set_color(parent_of(node), RED)
                rotate_towards(parent_of(node))
                sibling = side_against(parent_of(node))

            # Case 3 - When the root and both the siblings children are black:
            #          (Root is always black due to case 2)
            #              1. Change the sibling to red.
            #              2. Move to step 1 for the parent.
            #          Otherwise:
            #              1. Move to step 5.
            if color_of(side_towards(sibling)) == BLACK and \
                            color_of(side_against(sibling)) == BLACK:
                set_color(sibling, RED)
                node = parent_of(node)
                continue

            # Case 4 - (REDUNDANT SPECIFICATION)
            #          Requires both siblings children to be black and the root
            #          to be red. This statement never succeeds as case 3
            #          always passes to case 1 if both siblings children are
            #          black. The root will always be black due to step 2.

            # Case 5 - When the furthest child of sibling from our node is
            #          black and the closest child of sibling is red:
            #          (At least 1 child must be red due to case 3)
            #              1. Set the red siblings child to black.
            #              2. Set the sibling to red.
            #              3. Rotate the sibling away from our node.
            #              4. Get the new sibling.
            #              5. Move to case 6.
            if color_of(side_against(sibling)) == BLACK:
                set_color(sibling, RED)
                set_color(side_towards(sibling), BLACK)
                rotate_against(sibling)
                sibling = side_against(parent_of(node))

            # Case 6 - When the sibling is black and the siblings furthest
            #          child from our node is red:
            #              1. Set the sibling to the same color as the parent.
            #              2. Set the parent to black.
            #              3. Set the furthest siblings child to black.
            #              4. Rotate the parent towards us.
            #              5. Repairs complete, exit and ensure the root node
            #                 is black.
            set_color(sibling, color_of(parent_of(node)))
            set_color(parent_of(node), BLACK)
            set_color(side_against(sibling), BLACK)
            rotate_towards(parent_of(node))
            node = self._root

        set_color(node, BLACK)

    def __rotate_left(self, root: Node):
        """Performs a left rotation.

        Makes the provided root's right child (pivot) become the new root.
        Puts the pivot's left child in the newly empty right position in the
        old root node.

        :param root: The root node to rotate left.
        :return: None
        """

        if root is None:
            return

        pivot = root.right
        root.right = pivot.left
        pivot_left_size = 0

        if pivot.left:
            pivot.left.parent = root
            pivot_left_size = pivot.left.size

        pivot.parent = root.parent

        if root.parent is None:
            self._root = pivot
        elif root is root.parent.left:
            root.parent.left = pivot
        else:
            root.parent.right = pivot

        pivot.left = root
        root.size -= pivot.size
        pivot.size += root.size

        root.size += pivot_left_size
        root.parent = pivot

    def __rotate_right(self, root: Node):
        """Performs a right rotation.

        Makes the provided root's left child (pivot) become the new root.
        Puts the pivot's right child in the newly empty left position in the
        old root node.

        :param root: The root node to rotate left.
        :return: None
        """

        if root is None:
            return

        pivot = root.left
        root.left = pivot.right
        pivot_right_size = 0

        if pivot.right:
            pivot.right.parent = root
            pivot_right_size = pivot.right.size

        pivot.parent = root.parent

        if root.parent is None:
            self._root = pivot
        elif root is root.parent.left:
            root.parent.left = pivot
        else:
            root.parent.right = pivot

        pivot.right = root
        root.size -= pivot.size
        pivot.size += root.size

        root.size += pivot_right_size
        root.parent = pivot


def color_of(node: Node):
    return node.color if node else BLACK


def parent_of(node: Node):
    return node.parent if node else None


def grandparent_of(node: Node):
    return node.get_grandparent() if node else None


def set_color(node: Node, color: bool):
    if node: node.color = color


def left_of(node: Node):
    return node.left if node else None


def right_of(node: Node):
    return node.right if node else None
