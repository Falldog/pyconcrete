import os
import py_compile
from os.path import join, splitext

from .str_tools import to_bytes


def lib_gen_py(py_code, py_filename, folder):
    """folder = None -> use @_tmp_dir"""
    assert py_filename.endswith('.py')
    py_filepath = join(folder, py_filename)
    with open(py_filepath, 'wb') as f:
        f.write(to_bytes(py_code))
    return py_filepath


def lib_gen_pyc(py_code, pyc_filename, folder, keep_py=False):
    """folder = None -> use @_tmp_dir"""
    assert pyc_filename.endswith('.pyc')
    filename = splitext(pyc_filename)[0]
    py_filepath = join(folder, filename + '.py')
    pyc_filepath = join(folder, filename + '.pyc')

    # create .py
    with open(py_filepath, 'wb') as f:
        f.write(to_bytes(py_code))

    # create .pyc
    py_compile.compile(py_filepath, cfile=pyc_filepath)

    # remove files
    if not keep_py:
        os.remove(py_filepath)

    return pyc_filepath


def lib_gen_pye(py_code, pye_filename, folder, keep_py=False, keep_pyc=False):
    """folder = None -> use @_tmp_dir"""
    assert pye_filename.endswith('.pye')
    filename = os.path.splitext(pye_filename)[0]
    py_filepath = join(folder, filename + '.py')
    pyc_filepath = join(folder, filename + '.pyc')
    pye_filepath = join(folder, filename + '.pye')

    # create .py
    with open(py_filepath, 'wb') as f:
        f.write(to_bytes(py_code))

    # create .pyc
    py_compile.compile(py_filepath, cfile=pyc_filepath)

    # create .pye & remove .py & .pyc
    import pyconcrete

    pyconcrete.encrypt_file(pyc_filepath, pye_filepath)

    # remove files
    if not keep_py:
        os.remove(py_filepath)
    if not keep_pyc:
        os.remove(pyc_filepath)

    return pye_filepath
