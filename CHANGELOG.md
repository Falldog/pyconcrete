# Pyconcrete Changelog

## 1.0.1 (2025-??-??)

### Features
* Support to assign customized file extension. Which default is .pye https://github.com/Falldog/pyconcrete/pull/115

### Bug fixes
* Fix return code should not be 0 when python script is exception https://github.com/Falldog/pyconcrete/pull/114



## 1.0.0 (2025-02-23)

### Features
* Build-system migrate to `meson-python`
* Migrate `setup.py` to `pyproject.toml`
* Migrate test framework to pytest
* Support python 3.11 3.12, 3.13

### Breaking Changes
* No longer support python versions earlier than 3.6
* Assign passphrase by argument when pip installation, rather than assign env
* Pip installation passphrase naming be `passphrase`
* Rename `pyconcrete-admin.py` to `pyecli`



## 0.15.2 (2025-02-17)

### Features
* Migrate PyeLoader from meta_path to path_hook https://github.com/Falldog/pyconcrete/pull/108

### Bug fixes
* Fix django example Dockerfile get-pip.py for python 3.6 compatability https://github.com/Falldog/pyconcrete/pull/100



## 0.15.1 (2022-02-28)

### Bug fixes
* Fix passphrase secret_key generation issue. https://github.com/Falldog/pyconcrete/issues/73
* Remove installation default passphrase. https://github.com/Falldog/pyconcrete/issues/58
* Update pip installation passphrase env name to `PYCONCRETE_PASSPHRASE`



## 0.14.1 (2022-02-13)

### Bug fixes
* Fix pip installation issue



## 0.14.0 (2022-01-29)

### Features
* Support python 3.9 & 3.10



## 0.13.0 (2021-09-28)

### Features
* Support python 3.8

### Bug fixes
* Fix pyconcrete.exe PY_Finalize exception issue https://github.com/Falldog/pyconcrete/issues/71
* Fix threading global variable issue https://github.com/Falldog/pyconcrete/issues/61
* Fix python 3.7 link issue on Mac



## 0.12.1 (2018-09-15)

### Features
* Support python 3.7
* pyconcrete-admin support ignore file pattern https://github.com/Falldog/pyconcrete/pull/24
* pyconcrete-admin support multiple source files https://github.com/Falldog/pyconcrete/pull/43

### Bug fixes
* Fix double release memory issue https://github.com/Falldog/pyconcrete/pull/37



## 0.11.3 (2017-10-07)

### Features
* Support windows build with AppVeyor

### Bug fixes
* Fix several windows build issues



## 0.11.1 (2017-07-31)

### Features
* Support full encryption by pyconcrete(exe) for execute .pye as main script

### Bug fixes
* Fix python3 support compatible issue
* Fix Travis.ci unit test silent exception issue
