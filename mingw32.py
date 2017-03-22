# -*- coding: utf-8 -*-
# by th. Sun Mar 19 2017 06:15:57 GMT+0900 (JST)
"""  """
import os


def mingw32():
    """Return true when using mingw32 environment.
    """
    if sys.platform=='win32':
        if os.environ.get('OSTYPE', '')=='msys':
            return True
        if os.environ.get('MSYSTEM', '')=='MINGW32':
            return True
    return False





def main():
    """main function"""



if __name__ == '__main__':
    main()
