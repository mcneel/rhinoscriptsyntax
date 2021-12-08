import System.Threading.Tasks as tasks
from System import Exception, AggregateException

__run_native = None

def run(function, data_list, flatten_results = False):
    """for each item in data_list execute the input function. Execution is
    done on as many threads as there are CPUs on the computer.
    Parameters:
        function: function to execute for each item in the data_list
        data_list: list, tuple, or other enumerable data structure
        flatten_list [opt]: if True, when results are lists of lists the
          results are flattened into a single list of results. If this is True,
          you cannot depend on the result list being the same size as the input list
    Returns:
        list of results containing the return from each call to the input function
    """
    global __run_native
    if __run_native!=None:
        return __run_native(function, data_list, flatten_results)
    pieces = [(i,data) for i,data in enumerate(data_list)]
    results = range(len(pieces))

    def helper(piece):
        i, data = piece
        local_result = function(data)
        results[i] = local_result
    # Run first piece serial in case there is "set up" code in the function
    # that needs to be done once. All other iterations are done parallel
    helper(pieces[0])
    pieces = pieces[1:]
    if pieces: tasks.Parallel.ForEach(pieces, helper)
    if flatten_results:
        temp = []
        for result in results:
            if type(result) is list:
                for r in result: temp.append(r)
            else:
                temp.append(result)
        results = temp
    return results


def __build_module():
    try:
        import GhPython
        global __run_native
        __run_native = GhPython.ScriptHelpers.Parallel.Run
    except:
        __run_native = None


__build_module()