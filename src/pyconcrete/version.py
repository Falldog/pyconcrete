from os.path import abspath, dirname, exists, join

CUR_DIR = abspath(dirname(__file__))
VERSION_FILE = join(CUR_DIR, "VERSION")

if exists(VERSION_FILE):
    with open(VERSION_FILE) as f:
        __version__ = f.read().strip()
else:
    __version__ = '0.0.1'
