pyconcrete example for Django
==============


Environment setup
--------------
* install docker & execute below command to build and run
    ```bash
    $ ./bin/run-example-djnaog.sh
    ```
* access `http://127.0.0.1:5151` by browser


Environment
--------------
* Docker, Ubuntu 18.04
* Python 3.6
* Django 2


How the example working
--------------
* django in docker listen port `5151`
* install `pyconcrete` in system
* django source code be encrypted in docker image, `/code/`
* leave these two files as `.py`, and need add `import pyconcrete` at beginning
    * /code/pye_web/wsgi.py
    * /code/manage.py
* (Note) docker image will cache source code by image layer, the example only for testing. In production, you need to make sure docker image will not cache the original .py source code.
