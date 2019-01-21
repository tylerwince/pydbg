import inspect


def dbg(o, fancy=False):
    if not fancy:
        for idx, el in enumerate(reversed(inspect.stack())):
            if "dbg" in el.code_context[0]:
                var_name = el.code_context[0][el.code_context[0].find("(")+1:el.code_context[0].find(")")]
                print(f"[{el.filename}:{el.lineno}] {var_name} = {o}  {type(o)}")
                break
    else:
        # TODO(tyler): Build the entire callstack
        # TODO(tyler): colorize the output
        """
        [filename:lineno]

            var_name = o

            call_stack

        """
        out = ""


