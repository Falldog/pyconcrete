pyconcrete
=======
Protect your python script, encrypt .pyc to .pye and decrypt when import it

--------------

Version
--------------
1.0.x Beta


Protect python script work flow
--------------
* main.py `import pyconcrete`
* pyconcrete will hook import module
* when `import MODULE` will try to find `MODULE.pye`
  and then decrypt `MODULE.pye` via `_pyconcrete.pyd` and execute decrypted data (as .pyc content)
* encrypt & decrypt secret key record in _pyconcrete.pyd (like DLL or SO)
  the secret key would be hide in binary code, can't see it directly in HEX view


Encryption
--------------
* only support AES 128 bit now
* encrypt & decrypt by library OpenAES


Usage
--------------
* get the pyconcrete source code
```sh
$ git clone <pyconcrete repo> <pyconcre dir>
```

* install pyconcrete
```sh
$ python setup.py install
```
  need to input your passphrase create secret key and encrypt script
  same secret key will generate the same secret key

* convert your script to *.pye
```sh
$ pyconcrete-admin.py build_pye=<your py-module dir> --recursive
```

* remove *.py or copy *.pye to other folder

* import pyconcrete in your main script
  * recommendation project layout
```sh
main.py  # import pyconcrete and your lib
src/*.pye  # your libs
```


Usage (pyconcrete as Lib)
--------------
* install pyconcrete as lib
```sh
$ python setup.py install \
  --install-lib=<your project path> \
  --install-scripts=<where you want to execute pyconcrete-admin.py>
```
