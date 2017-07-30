pyconcrete
==============
[![Build Status](https://travis-ci.org/Falldog/pyconcrete.svg?branch=master)](https://travis-ci.org/Falldog/pyconcrete)
[![PyPI Version](https://img.shields.io/pypi/v/pyconcrete.svg)](https://pypi.python.org/pypi/pyconcrete)
[![PyPI PyVersion](https://img.shields.io/pypi/pyversions/pyconcrete.svg)](https://pypi.python.org/pypi/pyconcrete)
[![PyPI License](https://img.shields.io/pypi/l/pyconcrete.svg)](https://pypi.python.org/pypi/pyconcrete)

Protect your python script, encrypt .pyc to .pye and decrypt when import it

--------------


Protect python script work flow
--------------
* your_script.py `import pyconcrete`
* pyconcrete will hook import module
* when your script do `import MODULE`, pyconcrete import hook will try to find `MODULE.pye` first
  and then decrypt `MODULE.pye` via `_pyconcrete.pyd` and execute decrypted data (as .pyc content)
* encrypt & decrypt secret key record in `_pyconcrete.pyd` (like DLL or SO)
  the secret key would be hide in binary code, can't see it directly in HEX view


Encryption
--------------
* only support AES 128 bit now
* encrypt & decrypt by library OpenAES


Installation
--------------
  * need to input your passphrase create secret key for encrypt python script.
  * same passphrase will generate the same secret key
  * installation will add `pyconcrete.pth` into your `site-packages` for execute `sitecustomize.py` under pyconcrete which will automatic import pyconcrete

### pip
```sh
$ pip install pyconcrete
```
  > If you only execute `pip install` will not display any prompt(via stdout) from pyconcrete. 
  > Installation will be `blocked` and `waiting for user input passphrase twice`.
  > You must input passphrase for installation continuously.

```sh
$ pip install pyconcrete --egg --install-option="--passphrase=<your passphrase>"
```
  > pyconcrete installed as egg, if you want to uninstall pyconcrete will need to manually delete `pyconcrete.pth`.
  
### source
* get the pyconcrete source code
```sh
$ git clone <pyconcrete repo> <pyconcre dir>
```

* install pyconcrete
```sh
$ python setup.py install
```


Usage
--------------

### Full encrypted
* convert all of your `.py` to `*.pye`
```sh
$ pyconcrete-admin.py compile --source=<your py script>  --pye
$ pyconcrete-admin.py compile --source=<your py module dir> --pye
```

* remove `*.py` `*.pyc` or copy `*.pye` to other folder
* *main*.py encrypted as *main*.pye, it can't be executed by normal `python`. 
You must use `pyconcrete` to process the *main*.pye script. 
`pyconcrete`(*exe*) will be installed in your system path (ex: /usr/local/bin)

```sh
pyconcrete main.pye
src/*.pye  # your libs
```


### Partial encrypted (pyconcrete as lib)
* download pyconcrete source and install by setup.py
```sh
$ python setup.py install \
  --install-lib=<your project path> \
  --install-scripts=<where you want to execute pyconcrete-admin.py and pyconcrete(exe)>
```

* import pyconcrete in your main script
  * recommendation project layout
```sh
main.py       # import pyconcrete and your lib
pyconcrete/*  # put pyconcrete lib in project root, keep it as original files
src/*.pye     # your libs
```


Test
--------------
* test all case
```sh
$ ./pyconcrete-admin.py test
```


* test all case, setup `TEST_PYE_PERFORMANCE_COUNT` env to reduce testing time
```sh
$ TEST_PYE_PERFORMANCE_COUNT=1 ./pyconcrete-admin.py test
```


Building on Windows
--------------
https://matthew-brett.github.io/pydagogue/python_msvc.html
https://github.com/cython/cython/wiki/CythonExtensionsOnWindows


Announcement
--------------
pyconcrete is an experimental project, there is always a way to decrypt .pye files, but pyconcrete just make it harder.

