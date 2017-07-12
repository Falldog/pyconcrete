#include <Python.h>
#include "pyconcrete.h"

int main(int argc, char *argv[])
{
    Py_SetProgramName(argv[0]);  /* optional but recommended */
    Py_Initialize();

    PyRun_SimpleString("import os, sys\n"
                       "sys.path.append(os.getcwd())\n"
                       "print('\\n'.join(sys.path))\n");
    PyImport_ImportModule("pyconcrete");

    PyRun_SimpleString("import concrete\n"
                       "concrete.main()\n");
    Py_Finalize();
    return 0;
}

