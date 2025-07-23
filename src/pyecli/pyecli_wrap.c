#include <Python.h>
#include <stdlib.h>
#include "pyconcrete.h"
#include "pyconcrete_module.h"
#include "pyconcrete_py_src.h"
#include "pyecli_py_src.h"

#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)

#define RET_OK 0
#define RET_FAIL 1


int createAndInitPyconcreteModule();


int main(int argc, char *argv[])
{
    int i, len;
    int ret = RET_OK;
    wchar_t** argv_ex = NULL;
    argv_ex = (wchar_t**) malloc(sizeof(wchar_t*) * argc);
    for(i=0 ; i<argc ; ++i)
    {
        len = mbstowcs(NULL, argv[i], 0);
        argv_ex[i] = (wchar_t*) malloc(sizeof(wchar_t) * (len+1));
        mbstowcs(argv_ex[i], argv[i], len);
        argv_ex[i][len] = 0;
    }

    Py_SetProgramName(argv_ex[0]);  /* optional but recommended */
    // PyImport_AppendInittab must set up before Py_Initialize
    if (PyImport_AppendInittab("_pyconcrete", PyInit__pyconcrete) == -1)
    {
        fprintf(stderr, "Error, can't load embedded _pyconcrete correctly!\n");
        return RET_FAIL;
    }
    Py_Initialize();
    PyGILState_Ensure();

    if (createAndInitPyconcreteModule() == -1)
    {
        fprintf(stderr, "Error: Failed to import embedded pyconcrete.\n");
        Py_Finalize();
        return RET_FAIL;
    }

    if(argc >= 2)
    {
        if(argc == 2 && (strncmp(argv[1], "-v", 3)==0 || strncmp(argv[1], "--version", 10)==0))
        {
            printf("pyecli %s [Python %s]\n", TOSTRING(PYCONCRETE_VERSION), TOSTRING(PY_VERSION));  // defined by build-backend
        }
        else
        {
            PySys_SetArgv(argc, argv_ex);
            ret = PyRun_SimpleString(pyecli_py_source);
        }
    }

    PyGILState_Ensure();

    if (PyErr_Occurred()) {
        ret = RET_FAIL;
        PyErr_Print();
    }

    // reference mod_wsgi & uwsgi finalize steps
    // https://github.com/GrahamDumpleton/mod_wsgi/blob/develop/src/server/wsgi_interp.c
    // https://github.com/unbit/uwsgi/blob/master/plugins/python/python_plugin.c
    PyObject *module = PyImport_ImportModule("atexit");
    Py_XDECREF(module);

    if (!PyImport_AddModule("dummy_threading")) {
        PyErr_Clear();
    }

    Py_Finalize();

    for(i=0 ; i<argc ; ++i)
    {
        free(argv_ex[i]);
    }
    free(argv_ex);
    return ret;
}

int createAndInitPyconcreteModule()
{
    int ret = 0;
    PyObject* module_name = PyUnicode_FromString("pyconcrete");
    PyObject* module = PyModule_New("pyconcrete");
    PyObject* module_dict = PyModule_GetDict(module);

    // Ensure built-ins are available in the module dict
    PyDict_SetItemString(module_dict, "__builtins__", PyEval_GetBuiltins());

    // assign module dict into run_string result
    PyObject* module_result = PyRun_String(pyconcrete_py_source, Py_file_input, module_dict, module_dict);
    if (!module_result)
    {
        PyErr_Print();
        ret = -1;
        goto ERROR;
    }

    // Add the module to sys.modules, making it available for import
    PyObject* sys_modules = PyImport_GetModuleDict();
    PyDict_SetItem(sys_modules, module_name, module);

    // Import the module to initialize pyconcrete file loader
    PyObject* imported_module = PyImport_ImportModule("pyconcrete");

ERROR:
    Py_XDECREF(imported_module);
    Py_XDECREF(module);
    Py_XDECREF(module_result);
    Py_XDECREF(module_name);
    Py_XDECREF(module_dict);
    return ret;
}
