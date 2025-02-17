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
* Build the execution `pyconcrete` and read the `MAIN.pye` which encrypted by your passphrase.
* pyconcrete will decrypt the source file and then launch python interpreter to do the normal python behavior.
* pyconcrete will hook import module
* when your script do `import MODULE`, pyconcrete import hook will try to find `MODULE.pye` first
  and then decrypt `MODULE.pye` via `_pyconcrete.pyd` and execute decrypted data (as .pyc content)
* encrypt & decrypt secret key record in `_pyconcrete.pyd` (like DLL or SO)
  the secret key would be hide in binary code, can't see it directly in HEX view


Encryption
--------------
* only support AES 128 bit now
* encrypt & decrypt by library OpenAES


Compatibility
--------------
Pyconcrete has transitioned to using [meson-python](https://github.com/mesonbuild/meson-python) as its build backend
starting from version 1.0.0. This provides a more powerful build mechanism and supports newer Python versions.

For older Python support:
* Pyconcrete versions prior to 0.15.2 only support up to Python 3.10.
* If you need support for Python 3.6 or Python 2.7, please use versions before 0.15.2.
* Pyconcrete no longer supports Python versions earlier than 3.6.


Requirements
--------------
For unix base
* apt: pkg-config, build-essential, python{version}-dev
* pip: 23.1+


Installation
--------------
Due to security considerations, you must provide a passphrase to create a secret key for encrypting Python scripts:
* The same passphrase will generate the same secret key.
* Pre-built packages are not provided, so users must build the package yourself.

Build Process
* Pyconcrete relies on Meson to compile the C extension.
* The installation process will add a `pyconcrete.pth` file to your `site-packages`, enabling `sitecustomize.py` to automatically import Pyconcrete.

### pip
* Need to config the passphrase for installation. And only pip 23.1+ support passing argument via `-C` or `--config-settings`.
* Remember to assign `--no-cache-dir` to avoid use pip's cached package which already built by old passphrase.
```sh
$ pip install pyconcrete \
  --no-cache-dir \
  --config-settings=setup-args="-Dpassphrase=<Your_Passphrase>"
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


### Partial encrypted (pyconcrete as lib) -> (DEPRECATED and not Safe)
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
$ pytest tests
```

* test in docker environment
```sh
$ make test
```

* test in docker environment for specific python version
```sh
$ make test 3.10
```

Example
--------------

[Django with pyconcrete](example/django)


### Reference
https://matthew-brett.github.io/pydagogue/python_msvc.html
https://github.com/cython/cython/wiki/CythonExtensionsOnWindows


Announcement
--------------
pyconcrete is an experimental project, there is always a way to decrypt .pye files, but pyconcrete just make it harder.
