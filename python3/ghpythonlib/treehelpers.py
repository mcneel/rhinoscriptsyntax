import clr
clr.AddReference('Grasshopper, Culture=neutral, PublicKeyToken=dda4f5ec2cd80803')

from Grasshopper import DataTree as Tree
from Grasshopper.Kernel.Data import GH_Path as Path

from System import Array

def __proc_l2tree(input, tree, track, none_and_holes):
    path = Path(Array[int](track))
    if len(input) == 0 and none_and_holes: tree.EnsurePath(path); return
    for i,item in enumerate(input):
        if hasattr(item, '__iter__'): #if list or tuple
            track.append(i)
            __proc_l2tree(item,tree,track,none_and_holes)
            track.pop()
        else:
            if none_and_holes: tree.Insert(item,path,i)
            elif item is not None: tree.Add(item,path)

def list_to_tree(input, none_and_holes=True, source=[0]):
    """Transforms nestings of lists or tuples to a Grasshopper DataTree
    Inputs:
        input: A list to be transformed.
        none_and_holes=True: if True, holes in the tree structure will be preserved
            when possible.
        source=[0]: The root of the resulting tree.

    Returns:
        A Grasshopper.DataTree[object] object"""
    if input is not None:
        t=Tree[object]()
        __proc_l2tree(input,t,source[:], none_and_holes)
        return t

def __extend_at(path, index, simple_input, rest_list):
    target = path[index]
    if len(rest_list) <= target: rest_list.extend([None]*(target-len(rest_list)+1))
    if index == path.Length - 1:
        rest_list[target] = list(simple_input)
    else:
        if rest_list[target] is None: rest_list[target] = []
        __extend_at(path, index+1, simple_input, rest_list[target])

def tree_to_list(input, retrieve_base = lambda x: x[0]):
    """Returns a list representation of a Grasshopper DataTree.
    Inputs:
        input: A tree to be transformed.

        retrieve_base= lambda x: x[0]:
            Most trees start with a [0] path that is never changed.
            That is rendered as a list with a single item. However, for simplicity, most users
            will want to start using the first branch in that path. Therefore, retrieve_base
            defaults to a function that will just return the first item in the output.
        
            If a tree is created manually or edited,
            then it can also have paths starting with [1] etc. In this case, retrieve_base can
            be set to None. In this case, the entire result is returned, inside a single list.
            This is the equivalent of the "source" input for list_to_tree.

    Returns:
        A list object"""
    all = []
    for i in range(input.BranchCount):
        path = input.Path(i)
        __extend_at(path, 0, input.Branch(path), all)
    return retrieve_base(all) if retrieve_base else all