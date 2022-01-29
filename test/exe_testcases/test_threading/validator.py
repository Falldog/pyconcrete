#!/usr/bin/env python
# -*- coding: utf8 -*-
# Create on : 2019/07/13
from __future__ import unicode_literals


def validate(output_lines, *args, **kwargs):
    assert set(output_lines) == {'0', '1', '4', '9', '16'}, output_lines
    return True
