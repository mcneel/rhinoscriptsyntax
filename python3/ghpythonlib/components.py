import clr
clr.AddReference('Grasshopper, Culture=neutral, PublicKeyToken=dda4f5ec2cd80803')

import Grasshopper as gh
import os

from Rhino.NodeInCode import Components as ghc
import System
from System.Collections import IEnumerable, IEnumerator


class namedtupleiterator(IEnumerator):
    def __init__(self, namedtuple):
        self.namedtuple = namedtuple
        self.position = -1

    def get_Current(self):
        if self.position == -1: return None
        if self.position >= len(self.namedtuple): return None
        return self.namedtuple[self.position]

    def MoveNext(self):
        self.position += 1
        return self.position < len(self.namedtuple)

    def Reset(self):
        self.position = -1

class __namedtuple(IEnumerable):
    def __init__(self, attributes, values=None):
        if isinstance(attributes, dict):
            new_attributes = [key for key in attributes]
            values = [attributes[key] for key in new_attributes]
            attributes = new_attributes

        self.myattributes = attributes
        self.myvalues = values

    def __getattr__(self, name):
        return self.__find_by_name(name)

    def __getitem__(self, key):
        if isinstance(key, basestring):
            return self.__find_by_name(key)
        else:
            return self.myvalues[key]

    def __len__(self):
        return len(self.myvalues)


    def __repr__(self):
        return 'namedtuple(' + self.__str__() + ')'

    def __str__(self):
        return (
            repr(dict(
                (self.myattributes[i],self.myvalues[i])
                    for i in xrange(len(self.myattributes))))
                 )

    def __find_by_name(self, name):
        try:
            index = System.Array[str].IndexOf(self.myattributes, name)
        except System.Collections.Generic.KeyNotFoundException as ex:
            raise ValueError(
                str.format(
                'namedtuple does not have an attribute for \'{}\'. Available: {}',
                name, repr(list(self.myattributes)))
                )
        return self.myvalues[index]

    def __iter__(self):
       for a in self.myattributes:
          yield a

    def __contains__(self, item):
        return item in self.myattributes

    def __dir__(self):
        return sorted(set((dir(type(self)) + list(self.__dict__) +
                  self.myattributes)))

    def GetEnumerator(self):
        return namedtupleiterator(self)


class namespace_object(object):
    pass

def __make_function__(info, inputnames, outputnames, keep_tree):
    def component_function(*args, **kwargs):
        result = None
        warnings = None
        final_args = None
        if kwargs:
            final_args = [System.Reflection.Missing.Value] * len(inputnames)
            for kwarg in kwargs:
                if kwarg in inputnames:
                    index = inputnames[kwarg]
                    final_args[index] = kwargs[kwarg]
                else:
                    raise ValueError(
                        str.Format("{0} argument is not a valid parameter of the function. Valid parameters are: {1}.",
                                   kwarg, repr([x.lower().replace(" ", "_") for x in sorted(inputnames.keys())]) )
                    )
            if (len(args) + len(kwargs)) > len(inputnames):
                raise ValueError(str.Format("Expected at most {0} aguments, but got {1}.", len(inputnames), len(args)))
            for i,arg in enumerate(args): final_args[i] = arg
            result, warnings = info.Evaluate(final_args, keep_tree)
        elif args:
            result, warnings = info.Evaluate(args, keep_tree)
        else:
            result, warnings = info.Evaluate(None, keep_tree)
        if result:
            if not keep_tree:
                for i, result_item in enumerate(result):
                    if result_item == None:
                        continue
                    elif len(result_item)<1:
                        result[i] = None
                    elif len(result_item)==1:
                        result[i] = result_item[0]
            if len(result) == 1: result = result[0]
            elif len(result) > 1: result = __namedtuple(outputnames, result)
        if warnings:
            import scriptcontext as sc
            do_this = None
            if hasattr(sc.doc, 'Component') and sc.doc.Component != None:
                do_this = sc.doc.Component.AddMessageForWarnings
            for warning in warnings:
                if do_this: do_this(warning)
                print("Warning: " + warning)
        return result
    return component_function

def __add_to_module(f, module, name, description):
    setattr(module, name, f)
    a = module.__dict__[name]
    a.__name__ = name
    a.__doc__ = description
    return f

def __build_module():
    import Rhino
    def function_description(info, inputnames, outputnames):
        rc = ['', info.Description, "Input:"]
        for i, inputname in enumerate(inputnames):
            if info.InputsOptional[i]:
                s = "\t{0} (in, optional) [{1}] - {2}"
            else:
                s = "\t{0} [{1}] - {2}"
            rc.append(s.format(inputname, info.InputTypeNames[i], info.InputDescriptions[i]))
        if outputnames.Count == 1:
            rc.append("Returns: [{0}] - {1}".format(info.OutputTypeNames[0], info.OutputDescriptions[0]))
        elif outputnames.Count > 1:
            rc.append("Returns:")
            for i, out in enumerate(outputnames):
                s = "\t{0} [{1}] - {2}"
                rc.append(s.format(out, info.OutputTypeNames[i], info.OutputDescriptions[i]))
        return '\n'.join(rc)

    import sys, types, re
    code_name = 'ghpythonlib.components'
    core_module = sys.modules[code_name]
    translate_from = u"|+-*\u2070\u00B9\u00B2\u00B3\u2074\u2075\u2076\u2077\u2078\u2079"
    translate_to = "X__x0123456789"
    transl = dict(zip(translate_from, translate_to))

    tree_module = __add_to_module(
        namespace_object(), core_module, "trees",
        "Functions in this module accept and always return datatrees.")

    for info_names in ghc.NodeInCodeFunctions.GetDynamicMemberNames():
        info = ghc.NodeInCodeFunctions[info_names]
        try:
            name = info.Name
            name = re.sub("[^a-zA-Z0-9]", lambda match: transl[match.group()] if (match.group() in transl) else '', name)
            if len(name) == 0 or not name[0].isalpha(): name = 'x' + name
            inputnames = info.InputNames
            inputnames_dict = dict((el,i) for i, el in enumerate(inputnames))
            outputnames = info.OutputNames
            function_flatten = __make_function__(info, inputnames_dict, outputnames, False)
            function_tree = __make_function__(info, inputnames_dict, outputnames, True)
            m = core_module
            tm = tree_module
            if info.Namespace:
                module_name = info.Namespace.replace(" ", "")
                if module_name in core_module.__dict__:
                    m = core_module.__dict__[module_name]
                    tm = tree_module.__dict__[module_name]
                else:
                    description="Third-party add-on: " + info.Namespace
                    m =__add_to_module(
                        namespace_object(), core_module, module_name, description)
                    tm =__add_to_module(
                        namespace_object(), tree_module, module_name, description + ". With trees")
            description = function_description(info, inputnames, outputnames)
            __add_to_module(function_flatten, m, name, description)
            __add_to_module(function_tree, tm, name, description)
        except Exception as err:
            Rhino.RhinoApp.WriteLine(str(err))
            Rhino.Runtime.HostUtils.ExceptionReport("ghpythonlib.components.py|" + info.Name, err.clsException)


__build_module()
