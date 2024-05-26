import subprocess
import sys
from os.path import join

from .defines import ROOT_DIR
from .pyconcrete_builder import get_pyconcrete_env_path


def lib_compile_pyc(folder, remove_py=False):
    admin_path = join(ROOT_DIR, 'pyconcrete-admin.py')
    arg_remove_py = '--remove-py' if remove_py else ''
    subprocess.check_call(
        '%s %s compile --source=%s --pyc %s' % (sys.executable, admin_path, folder, arg_remove_py),
        env=get_pyconcrete_env_path(),
        shell=True,
    )


def lib_compile_pye(folder, remove_py=False, remove_pyc=False):
    admin_path = join(ROOT_DIR, 'pyconcrete-admin.py')
    arg_remove_py = '--remove-py' if remove_py else ''
    arg_remove_pyc = '--remove-pyc' if remove_pyc else ''
    subprocess.check_call(
        '%s %s compile --source=%s --pye %s %s' % (sys.executable, admin_path, folder, arg_remove_py, arg_remove_pyc),
        env=get_pyconcrete_env_path(),
        shell=True,
    )
