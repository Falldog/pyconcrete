#include <Python.h>
#include <stdlib.h>
#include "pyconcrete.h"
#include "pyconcrete_module.h"
#include "pyconcrete_py_src.h"

#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)

#define RET_OK 0
#define RET_FAIL 1

#if PY_MAJOR_VERSION >= 3 && PY_MINOR_VERSION >=7
    #define MAGIC_OFFSET 16
#elif PY_MAJOR_VERSION >= 3 && PY_MINOR_VERSION >=3
    #define MAGIC_OFFSET 12
#else
    #define MAGIC_OFFSET 8
#endif


int createAndInitPyconcreteModule();
int execPycContent(PyObject* pyc_content);
int runFile(const char* filepath);


int main(int argc, char *argv[])
{
#if PY_MAJOR_VERSION >= 3
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
#else
    char** argv_ex = argv;
#endif

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
            printf("pyconcrete %s [Python %s]\n", TOSTRING(PYCONCRETE_VERSION), TOSTRING(PY_VERSION));  // defined by build-backend
        }
        else
        {
            PySys_SetArgv(argc-1, argv_ex+1);
            ret = runFile(argv[1]);
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

#if PY_MAJOR_VERSION >= 3
    for(i=0 ; i<argc ; ++i)
    {
        free(argv_ex[i]);
    }
    free(argv_ex);
#endif
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

int execPycContent(PyObject* pyc_content)
{
    int ret = RET_OK;
    PyObject* py_marshal = NULL;
    PyObject* py_marshal_loads = NULL;
    PyObject* pyc_content_wo_magic = NULL;
    PyObject* py_code = NULL;
    PyObject* global = PyDict_New();
    Py_ssize_t content_size = 0;
    char* content = NULL;
#if PY_MAJOR_VERSION >= 3
    PyObject* main_name = PyUnicode_FromString("__main__");
#else
    PyObject* main_name = PyBytes_FromString("__main__");
#endif

    // load compiled source from .pyc content
    py_marshal = PyImport_ImportModule("marshal");
    py_marshal_loads = PyObject_GetAttrString(py_marshal, "loads");

    content = PyBytes_AS_STRING(pyc_content);
    content_size = PyBytes_Size(pyc_content);

    pyc_content_wo_magic = PyBytes_FromStringAndSize(content+MAGIC_OFFSET, content_size-MAGIC_OFFSET);
    py_code = PyObject_CallFunctionObjArgs(py_marshal_loads, pyc_content_wo_magic, NULL);
    if(py_code == NULL && PyErr_Occurred() != NULL)
    {
        ret = RET_FAIL;
        PyErr_Print();
        goto ERROR;
    }

    // setup global and exec loaded py_code
    PyDict_SetItemString(global, "__name__", main_name);
    PyDict_SetItemString(global, "__builtins__", PyEval_GetBuiltins());
    PyEval_EvalCode(py_code, global, global);

ERROR:
    Py_XDECREF(py_code);
    Py_XDECREF(global);
    Py_XDECREF(pyc_content_wo_magic);
    Py_XDECREF(py_marshal_loads);
    Py_XDECREF(py_marshal);
    return ret;
}

int runFile(const char* filepath)
{
    FILE* src = NULL;
    char* content = NULL;
    int ret = RET_OK;
    size_t s, size;
    PyObject* py_content = NULL;
    PyObject* py_plaint_content = NULL;
    PyObject* py_args = NULL;

    src = fopen(filepath, "rb");
    if(src == NULL)
    {
        return RET_FAIL;
    }

    // read & parse file
    {
        fseek(src, 0, SEEK_END);
        size = ftell(src);

        fseek(src, 0, SEEK_SET);
        content = malloc(size * sizeof(char));
        s = fread(content, 1, size, src);
        if(s != size)
        {
            return RET_FAIL;
        }
        py_content = PyBytes_FromStringAndSize(content, size);
        py_args = PyTuple_New(1);
        PyTuple_SetItem(py_args, 0, py_content);
        py_plaint_content = fnDecryptBuffer(NULL, py_args);

        Py_DECREF(py_args);
        free(content);
    }
    fclose(src);

    ret = execPycContent(py_plaint_content);

    Py_DECREF(py_plaint_content);
    return ret;
}
