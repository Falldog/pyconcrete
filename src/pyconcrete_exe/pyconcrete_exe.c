#include <Python.h>
#include <stdlib.h>
#include "pyconcrete.h"


void execPycContent(PyObject* pyc_content);
void runFile(const char* filepath);


int main(int argc, char *argv[])
{
    Py_SetProgramName(argv[0]);  /* optional but recommended */
    Py_Initialize();
    PySys_SetArgv(argc, argv);

    runFile(argv[1]);

    Py_Finalize();
    return 0;
}

void execPycContent(PyObject* pyc_content)
{
    PyObject* py_marshal = NULL;
    PyObject* py_marshal_loads = NULL;
    PyObject* pyc_content_wo_magic = NULL;
    PyObject* py_code = NULL;
    PyObject* global = PyDict_New();
    PyObject* local = PyDict_New();
    Py_ssize_t content_size = 0;
    char* content = NULL;
#if PY_MAJOR_VERSION >= 3 && PY_MINOR_VERSION >=3
    int magic_offset = 12;
#else
    int magic_offset = 8;
#endif

    // load compiled source from .pyc content
    py_marshal = PyImport_ImportModule("marshal");
    py_marshal_loads = PyObject_GetAttrString(py_marshal, "loads");

    content = PyBytes_AS_STRING(pyc_content);
    content_size = PyBytes_Size(pyc_content);

    pyc_content_wo_magic = PyBytes_FromStringAndSize(content+magic_offset, content_size-magic_offset);
    py_code = PyObject_CallFunctionObjArgs(py_marshal_loads, pyc_content_wo_magic, NULL);

    // setup global and exec loaded py_code
    PyDict_SetItemString(global, "__name__", PyBytes_FromString("__main__"));
    PyDict_SetItemString(global, "__builtins__", PyEval_GetBuiltins());
    PyEval_EvalCode((PyCodeObject*)py_code, global, local);

    Py_DECREF(py_code);
    Py_DECREF(global);
    Py_DECREF(local);
    Py_DECREF(pyc_content_wo_magic);
    Py_DECREF(py_marshal_loads);
    Py_DECREF(py_marshal);
}

void runFile(const char* filepath)
{
    FILE* src = NULL;
    char* content = NULL;
    size_t s, size;
    PyObject* py_content = NULL;
    PyObject* py_plaint_content = NULL;
    PyObject* py_args = NULL;

    src = fopen(filepath, "rb");
    {
        fseek(src, 0, SEEK_END);
        size = ftell(src);

        fseek(src, 0, SEEK_SET);
        content = malloc(size * sizeof(char));
        s = fread(content, 1, size, src);
        if(s != size)
        {
            return;
        }
        py_content = PyBytes_FromStringAndSize(content, size);
        py_args = PyTuple_New(1);
        PyTuple_SetItem(py_args, 0, py_content);
        py_plaint_content = fnDecryptBuffer(NULL, py_args);

        Py_DECREF(py_args);
        Py_DECREF(py_content);
        free(content);
    }
    fclose(src);

    execPycContent(py_plaint_content);

    Py_DECREF(py_plaint_content);
}

