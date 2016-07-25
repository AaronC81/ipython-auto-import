from functools import partial
import re
import sys

try:
    import colorama
    colorama.init()
    pre = (colorama.Fore.CYAN + colorama.Style.BRIGHT +
        "AutoImport: " + colorama.Style.NORMAL +
        colorama.Fore.WHITE)
except:
    pre = "AutoImport: "

common_others = {"pd": "pandas", "np": "numpy", "sp": "scipy"}

class pipUnsuccessfulException(Exception):
    pass



def custom_exc(ipython, shell, etype, evalue, tb, tb_offset=None):
    shell.showtraceback((etype, evalue, tb), tb_offset)

    while tb.tb_next:
        tb = tb.tb_next
    if not re.match("\\A<ipython-input-.*>\\Z", tb.tb_frame.f_code.co_filename):
        # Innermost frame is not the IPython interactive environment.
        return

    try:
        # Get the name of the module you tried to import
        results = re.match("\\Aname '(.*)' is not defined\\Z", str(evalue))
        if not results:
            return
        name = results.group(1)
        custom_exc.last_name = name

        try:
            __import__(name)
        except:
            if common_others.get(name):
                new_name = common_others.get(name)
                try:
                    __import__(new_name)
                    r = ipython.ask_yes_no(
                        pre +
                        "{0} isn't a module, but {1} is. "
                        "Import {1} as {0}? (Y/n)".format(name, new_name))
                    if r:
                        name = "{} as {}".format(new_name, name)
                    else:
                        return
                except Exception as e:
                    print(pre +
                          "{} isn't a module and nor is {}"
                          .format(name, new_name))
                    print(e)
                    return
            else:
                print(pre + "{} isn't a module".format(name))
                try:
                    last_name = custom_exc.last_name
                    if ipython.ask_yes_no(pre + "Attempt to pip-install {}? (Y/n)"
                                                .format(last_name)):
                        if __import__("pip").main(["install", last_name]) != 0:
                            raise pipUnsuccessfulException
                    else:
                        return
                    print(pre + "Installation completed successfully, importing...")
                    try:
                        res = ipython.run_cell("import {}".format(last_name))
                        print(pre + "Imported referenced module {}".format(last_name))
                    except:
                        print(pre + "{} isn't a module".format(last_name))
                except pipUnsuccessfulException:
                    print(pre + "Installation with pip failed")

                except AttributeError:
                    print(pre + "No module to install")

                except ImportError:
                    print(pre + "pip not found")
                return

        # Import the module
        ipython.run_code("import {}".format(name))
        print(pre + "Imported referenced module {!r}, will retry".format(name))
        print("".join("-" for _ in range(75)))
    except Exception as e:
        print(pre + ("Attempted to import {!r}"
                     "but an exception occured".format(name)))

    try:
        # Run the failed line again
        res = ipython.run_cell(
            list(ipython.history_manager.get_range())[-1][-1])
    except Exception as e:
        print(pre + "Another exception occured while retrying")
        shell.showtraceback((type(e), e, None), None)



def load_ipython_extension(ipython):
    # Bind the function we created to IPython's exception handler
    ipython.set_custom_exc((NameError,), partial(custom_exc, ipython))
