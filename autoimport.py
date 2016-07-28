PIP_ENABLED = False

from functools import partial
import ast
import re

# Determine if we have Colorama - if not, use a failsafe
try:
    import colorama
    colorama.init()
    pre = (colorama.Fore.CYAN + colorama.Style.BRIGHT +
        "AutoImport: " + colorama.Style.NORMAL +
        colorama.Fore.WHITE)
except:
    pre = "AutoImport: "


class GetOutException(Exception):
    ...


stored_imports = set()

def import_module(ipython, import_base, import_as=None, import_child=None):
    if import_as is not None and import_child is not None:
        ipython.run_code("from {} import {} as {}".format(import_base,
                                                          import_child,
                                                          import_as))
        print(pre + "From {} impored {} as {}".format(import_base,
                                                      import_child,
                                                      import_as))
    elif import_as is not None:
        ipython.run_code("import {} as {}".format(import_base, import_as))
        print(pre + "Imported {} as {}".format(import_base, import_as))
    elif import_child is not None:
        ipython.run_code("from {} import {}".format(import_base, import_child))
        print(pre + "From {} imported {}".format(import_base, import_child))
    else:
        ipython.run_code("import {}".format(import_base))
        print(pre + "Imported {}".format(import_base))

def custom_exc(ipython, shell, etype, evalue, tb, tb_offset=None):
    while tb.tb_next:
            tb = tb.tb_next
    if not re.match("\\A<ipython-input-.*>\\Z", tb.tb_frame.f_code.co_filename):
        # Innermost frame is not the IPython interactive environment.
        return

    expression_result = str(evalue)
    results = re.match("\\Aname '(.*)' is not defined\\Z", expression_result)
    if not results:
        return
    import_raw_name = results.group(1)

    class Visitor(ast.NodeVisitor):
        def __init__(self):
            super()
            self.should_continue = False

        def visit_Attribute(self, node):
            global should_continue
            # Used in an x._ context
            try:
                print("Hey, an attribute!")
                print(node.value.id)
                if node.value.id == import_raw_name:
                    print("True")
                    self.should_continue = True
                return node
            except Exception as e:
                print(e)
                ...

        def visit_Call(self, node):
            global should_continue
            # Used as a call 
            try:
                print("Hey, a call!")
                if node.func.id == import_raw_name:
                    print("True")
                    self.should_continue = True
                return node
            except Exception as e:
                print(e)
                ...
            
    
    v = Visitor()
    v.visit(ast.parse(list(ipython.history_manager.get_range())[-1][-1]))
    
    if not v.should_continue:
        return

    # Test basic import
    try:
        __import__(import_raw_name)
        import_module(ipython, import_raw_name)
        try:
            ipython.run_cell(list(ipython.history_manager.get_range())[-1][-1])
        except Exception as e:
            shell.showtraceback((type(e), e, None), None)
        return
    except:
        # Module with that name doesn't exist
        ...

    # Items of stored_imports are in form:
    # (x, y, z) for `from x import y as z` where z is NameError
    # (x, y, None) for `from x import y` where y is NameError
    # (x, None, y) for `import x as y` where y is NameError
    
    # "Temporary fix" for not running code if no ifs triggered
    try:
        for item in stored_imports:
            # If (x, y, z)
            if all(item):
                if item[-1] == import_raw_name:
                    try:
                        import_module(ipython, item[0], item[-1], item[1])
                        raise GetOutException
                    except GetOutException:
                        raise
                    except Exception as e:
                        shell.showtraceback((type(e), e, None), None)
            # If (x, y, None)
            elif item[-1] is None:
                if item[1] == import_raw_name:
                    try:
                        import_module(ipython, item[0], None, item[1])
                        raise GetOutException
                    except GetOutException:
                        raise
                    except Exception as e:
                        shell.showtraceback((type(e), e, None), None)
            # If (x, None, y)
            elif item[1] is None:
                if item[-1] == import_raw_name:
                    try:
                        import_module(ipython, item[0], item[-1])
                        raise GetOutException
                    except GetOutException:
                        raise
                    except Exception as e:
                        shell.showtraceback((type(e), e, None), None)        
    except GetOutException:
        try:
            ipython.run_cell(list(ipython.history_manager.get_range())[-1][-1])
        except Exception as e:
            shell.showtraceback((type(e), e, None), None)
        return

    # All else failed, show the original traceback
    shell.showtraceback((etype, evalue, tb), tb_offset)


def load_ipython_extension(ipython):
    global stored_imports

    # Get previous imports from history
    class Visitor(ast.NodeVisitor):
        def visit_Import(self, node):
            stored_imports.update((alias.name, None, alias.asname) for alias in node.names)
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            if not node.level:  # Skip relative imports.
                stored_imports.update((node.module, alias.name, alias.asname)
                            for alias in node.names)
            self.generic_visit(node)

    for _, _, entry in (
            ipython.history_manager.get_tail(ipython.history_load_length, raw=False)):
        try:
            parsed = ast.parse(entry)
        except SyntaxError:
            continue
        Visitor().visit(parsed)
    
    ipython.set_custom_exc((NameError,), partial(custom_exc, ipython))