#!/usr/bin/env python
from __future__ import unicode_literals


def validate(output_lines, *args, **kwargs):
    assert kwargs.get('return_code') == 99
    return True
