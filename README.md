pyconcrete
==============
[![Travis](https://img.shields.io/travis/Falldog/pyconcrete.svg?label=travis)](https://travis-ci.org/Falldog/pyconcrete)
[![AppVeyor](https://img.shields.io/appveyor/ci/Falldog/pyconcrete.svg?label=appveyor)](https://ci.appveyor.com/project/Falldog/pyconcrete)
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
You must set up environment variable `PYCONCRETE_PASSPHRASE` for installation continuously.
```sh
$ PYCONCRETE_PASSPHRASE=<your passphrase here> pip install pyconcrete
```

or, if you use an old pip version that supports --egg:

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
* test in local
```sh
$ ./pyconcrete-admin.py test
```

* test in docker environment
```sh
$ ./bin/run-test.sh
```

* add test case for pyconcrete.exe
  * reference exists test case
  * add folder in `test/exe_testcases/`
  * add testing code at `test/exe_testcases/src/main.py`
  * add validator at `test/exe_testcases/validator.py`

Example
--------------

[Django with pyconcrete](example/django)



Building on Linux
--------------

### Python 3.7 - fix Ubuntu 14.04 build error
```bash
x86_64-linux-gnu-gcc: error: unrecognized command line option `-fstack-protector-strong`
```
Reference by [Stackoverflow solution](https://stackoverflow.com/questions/27182042/pip-error-unrecognized-command-line-option-fstack-protector-strong)
* you should install `gcc-4.9` first
* symlink `/usr/bin/x86_64-linux-gnu-gcc` to `gcc-4.9`
* build pycocnrete again
* rollback symlink


Building on Windows
--------------

### Python 2.7 - Visual Studio 2008
https://www.microsoft.com/en-us/download/details.aspx?id=44266

* Open VS2008 Command Prompt
* `set DISTUTILS_USE_SDK=1`
* `set SET MSSdk=1`
* create `distutils.cfg` and put inside
    ```text
    [build]
    compiler=msvc
    ```

### Python 3.5, 3.6, 3.7 - Visual Studio 2015

[MSVC 2015 Build Tools](http://landinghub.visualstudio.com/visual-cpp-build-tools)

[Document](https://matthew-brett.github.io/pydagogue/python_msvc.html#python-3-5-3-6)

* make sure setuptools >= 24.0
    ```sh
    python -c 'import setuptools; print(setuptools.__version__)'
    ```

* Open VS2015 Build Tools Command Prompt
* `set DISTUTILS_USE_SDK=1 `
* `setenv /x64 /release`  or `setenv /x86 /release`


### Reference
https://matthew-brett.github.io/pydagogue/python_msvc.html
https://github.com/cython/cython/wiki/CythonExtensionsOnWindows


Announcement
--------------
pyconcrete is an experimental project, there is always a way to decrypt .pye files, but pyconcrete just make it harder.
