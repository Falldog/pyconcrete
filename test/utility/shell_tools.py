#!/usr/bin/env python
#
# Copyright 2015 Falldog Hsieh <falldog7@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
from os.path import join
from pathlib import Path


def touch(file_path):
    open(file_path, 'a').close()


def make_py_packages(base_dir: str, child_path: str):
    children_paths = child_path.split('/')
    cur_dir = base_dir
    touch(join(cur_dir, '__init__.py'))
    for p in children_paths:
        if p == '':
            continue
        dir_path = join(cur_dir, p)
        os.makedirs(dir_path, exist_ok=True)
        touch(join(dir_path, '__init__.py'))
        cur_dir = dir_path
    return join(base_dir, child_path)


def _tree_iter(dir_path: str | Path, prefix: str = ''):
    """
    A recursive generator, given a directory Path object
    will yield a visual tree structure line by line
    with each line prefixed by the same characters
    """
    # prefix components
    space = '    '
    branch = '│   '
    # pointers
    tee = '├── '
    last = '└── '

    contents = list(dir_path.iterdir())
    # contents each get pointers that are ├── with a final └── :
    pointers = [tee] * (len(contents) - 1) + [last]
    for pointer, path in zip(pointers, contents):
        yield prefix + pointer + path.name
        if path.is_dir():  # extend the prefix and recurse:
            extension = branch if pointer == tee else space
            # i.e. space because last, └── , above so no more |
            yield from _tree_iter(path, prefix=prefix + extension)


def tree(dir_path: str | Path, prefix: str = ''):
    """debug tool for dump folder structure as tree view"""
    dir_path = Path(dir_path)
    for line in _tree_iter(dir_path, prefix=prefix):
        print(line)
