pyconcrete example for Django
==============


Environment setup
--------------
* install vagrant && VirtualBox
    ```bash
    $ cd pyconcrete/example/django && vagrant up
    ```
* access `http://127.0.0.1:5151` by browser


Environment 
--------------
* Ubuntu 14.04
* Python 2.7
* Nginx + uwsgi
* Django 1.11


How the example working
--------------
* Django in VM listen port 5151
* install `pyconcrete` in system
* source code path in VM: `/home/pye_web_src`
* encrypted code path in VM: `/home/pye_web`
* leave these two files as `.py`, and need add `import pyconcrete` at beginning
    * pye_web/pye_web/wsgi.py 
    * pye_web/manage.py

