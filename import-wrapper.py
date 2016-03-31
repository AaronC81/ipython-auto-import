import sys
import IPython
import colorama
import re

colorama.init()

common_others = {"pd": "pandas", "np": "numpy", "sp": "scipy"}


def custom_exc(shell, etype, evalue, tb, tb_offset=None):
    pre = (colorama.Fore.CYAN + colorama.Style.BRIGHT +
           "AutoImport: " + colorama.Style.NORMAL +
           colorama.Fore.WHITE)
    if etype == NameError:
        shell.showtraceback((etype, evalue, tb), tb_offset)
        try:
            # Get the name of the module you tried to import
            results = re.match("name '(.*)' is not defined", str(evalue))
            name = results.group(1)

            try:
                __import__(name)
            except:
                if common_others.get(name):
                    new_name = common_others.get(name)
                    try:
                        __import__(new_name)
                        p = IPython.get_ipython()
                        r = p.ask_yes_no(pre +
                                         "{0} isn't a module, but {1} is."
                                         " Import {1} as {0}? (Y/n)"
                                         .format(name, new_name))
                        if r:
                            name = "{} as {}".format(new_name, name)
                        else:
                            return
                    except Exception as e:
                        print(pre + "{} isn't a module and "
                              "nor is {}".format(name, new_name))
                        print(e)
                        return
                else:
                    print(pre + "{} isn't a module".format(name))
                    return

            # Import the module
            IPython.get_ipython().run_code("import {}".format(name))
            print(pre +
                  "Imported referenced module \"{}\", will retry".format(name))
            print(colorama.Fore.CYAN + "".join("-" for _ in range(75)))
        except Exception as e:
            print(pre + ("Attempted to import \"{}\""
                  "but an exception occured".format(name)))

        try:
            # Run the failed line again
            p = IPython.get_ipython()
            res = p.run_cell(list(p.history_manager.get_range())[-1][-1])
        except Exception as e:
            print(pre + "Another exception occured while retrying")
            shell.showtraceback((type(e), e, None), None)
    else:
        shell.showtraceback((etype, evalue, tb), tb_offset=tb_offset)


if IPython.get_ipython():
    # Bind the function we created to IPython's exception handler
    IPython.get_ipython().set_custom_exc((Exception,), custom_exc)
