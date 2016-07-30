# ipython-auto-import

How many times have you quickly wanted to test something, only to do this?

```
In [1]: df = pandas.read_clipboard()
---------------------------------------------------------------------------
NameError                                 Traceback (most recent call last)
<ipython-input-1-45ec783f831b> in <module>()
----> 1 df = pandas.read_clipboard()

NameError: name 'pandas' is not defined

In [2]: import pandas # *sigh*

In [3]: df = pandas.read_clipboard()
```

Inspired by [this SO question](http://stackoverflow.com/questions/36112275/make-ipython-import-what-i-mean/36116171#36116171), you'll never need to import a module again in IPython!

```
In [1]: pandas.read_clipboard()
AutoImport: Imported pandas
Out[1]:
       First,Last
0         Foo,Bar
1  John,Appleseed
```

The first time you reference a module, it imports it auto-magically!

## Installation

**NOTE**: It's recommended that you install `colorama` for best results: `pip install colorama`

### Easy way
Clone the repo and run `install.py`.

### Hard way
Add `autoimport.py` to `~/.ipython/extensions`, then call `%load_ext autoimport` either at the IPython prompt, or add
```
c.InteractiveShellApp.exec_lines.append("%load_ext autoimport")
```
at the end of `~/.ipython/profile_default/ipython_config.py`.
