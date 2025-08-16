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

// WIN32 platform use wmain, all string related functions should change to wchar_t version
#ifdef WIN32
    #define _CHAR                                       wchar_t
    #define _T(s)                                       L##s
    #define _fopen                                      _wfopen
    #define _strncmp                                    wcsncmp
    #define _strlen                                     wcslen
    #define _PyConfig_SetArgv                           PyConfig_SetArgv
    #define _PyConfig_SetString                         PyConfig_SetString
    #define _PyUnicode_FromStringAndSize                PyUnicode_FromWideChar
#else
    #define _CHAR                                       char
    #define _T(s)                                       s
    #define _fopen                                      fopen
    #define _strncmp                                    strncmp
    #define _strlen                                     strlen
    #define _PyConfig_SetArgv                           PyConfig_SetBytesArgv
    #define _PyConfig_SetString                         PyConfig_SetBytesString
    #define _PyUnicode_FromStringAndSize                PyUnicode_FromStringAndSize
#endif


int createAndInitPyconcreteModule();
int execPycContent(PyObject* pyc_content, const _CHAR* filepath);
int runFile(const _CHAR* filepath);
int prependSysPath0(const _CHAR* script_path);
void initPython(int argc, _CHAR *argv[]);
PyObject* getFullPath(const _CHAR* filepath);


#ifdef WIN32
int wmain(int argc, wchar_t *argv[])
#else
int main(int argc, char *argv[])
#endif
{
    int ret = RET_OK;

    // PyImport_AppendInittab must set up before Py_Initialize
    if (PyImport_AppendInittab("_pyconcrete", PyInit__pyconcrete) == -1)
    {
        fprintf(stderr, "Error, can't load embedded _pyconcrete correctly!\n");
        return RET_FAIL;
    }

    initPython(argc, argv);
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
        if(argc == 2 && (_strncmp(argv[1], _T("-v"), 3)==0 || _strncmp(argv[1], _T("--version"), 10)==0))
        {
            printf("pyconcrete %s [Python %s]\n", TOSTRING(PYCONCRETE_VERSION), TOSTRING(PY_VERSION));  // defined by build-backend
        }
        else
        {
#if PY_MAJOR_VERSION >= 3 && PY_MINOR_VERSION <=7
    #if defined(WIN32)
            PySys_SetArgv(argc-1, argv+1);
    #else
            int i, len;
            wchar_t** argv_ex = NULL;
            argv_ex = (wchar_t**) malloc(sizeof(wchar_t*) * argc);
            // setup
            for(i=0 ; i<argc ; ++i)
            {
                len = mbstowcs(NULL, argv[i], 0);
                argv_ex[i] = (wchar_t*) malloc(sizeof(wchar_t) * (len+1));
                mbstowcs(argv_ex[i], argv[i], len);
                argv_ex[i][len] = 0;
            }

            // set argv
            PySys_SetArgv(argc-1, argv_ex+1);

            // release
            for(i=0 ; i<argc ; ++i)
            {
                free(argv_ex[i]);
            }
    #endif
#else
            prependSysPath0(argv[1]);
#endif // PY_MAJOR_VERSION >= 3 && PY_MINOR_VERSION <=7
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
    return ret;
}


void initPython(int argc, _CHAR *argv[]) {
#if PY_MAJOR_VERSION >= 3 && PY_MINOR_VERSION <=7
    #if defined(WIN32)
        Py_SetProgramName(argv[0]);
    #else
        int len = mbstowcs(NULL, argv[0], 0);
        wchar_t* arg0 = (wchar_t*) malloc(sizeof(wchar_t) * (len+1));
        mbstowcs(arg0, argv[0], len);
        arg0[len] = 0;
        Py_SetProgramName(arg0);
    #endif
#else
    PyStatus status;

    // ----------
    // PyPreConfig
    // ----------
    // On Windows platform invoke pyconcrete by subprocess may changed the console encoding to cp1252
    // force to set utf8 mode to avoid the issue.
    PyPreConfig preconfig;
    PyPreConfig_InitPythonConfig(&preconfig);
    preconfig.utf8_mode = 1;

    status = Py_PreInitialize(&preconfig);
    if (PyStatus_Exception(status)) {
        goto INIT_EXCEPTION;
    }

    // ----------
    // PyConfig
    // ----------
    PyConfig config;
    PyConfig_InitPythonConfig(&config);
    config.parse_argv = 0;
    config.isolated = 1;

    // Set program_name as pyconcrete. (Implicitly preinitialize Python)
    status = _PyConfig_SetString(&config, &config.program_name, argv[0]);
    if (PyStatus_Exception(status)) {
        goto INIT_EXCEPTION;
    }

    // Decode command line arguments. (Implicitly preinitialize Python)
    status = _PyConfig_SetArgv(&config, argc-1, argv+1);
    if (PyStatus_Exception(status))
    {
        goto INIT_EXCEPTION;
    }

    status = Py_InitializeFromConfig(&config);
    if (PyStatus_Exception(status))
    {
        goto INIT_EXCEPTION;
    }
    PyConfig_Clear(&config);
    return;

INIT_EXCEPTION:
    PyConfig_Clear(&config);
    if (PyStatus_IsExit(status))
    {
        return status.exitcode;
    }
    // Display the error message and exit the process with non-zero exit code
    Py_ExitStatusException(status);
#endif // ifdef PY_MAJOR_VERSION >= 3 && PY_MINOR_VERSION <=7
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


int execPycContent(PyObject* pyc_content, const _CHAR* filepath)
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
    PyObject* py_full_filepath = getFullPath(filepath);
    PyDict_SetItemString(global, "__name__", main_name);
    PyDict_SetItemString(global, "__file__", py_full_filepath);
    PyDict_SetItemString(global, "__builtins__", PyEval_GetBuiltins());
    PyEval_EvalCode(py_code, global, global);

ERROR:
    Py_XDECREF(py_full_filepath);
    Py_XDECREF(py_code);
    Py_XDECREF(global);
    Py_XDECREF(pyc_content_wo_magic);
    Py_XDECREF(py_marshal_loads);
    Py_XDECREF(py_marshal);
    return ret;
}


int runFile(const _CHAR* filepath)
{
    FILE* src = NULL;
    char* content = NULL;
    int ret = RET_OK;
    size_t s, size;
    PyObject* py_content = NULL;
    PyObject* py_plaint_content = NULL;
    PyObject* py_args = NULL;

    src = _fopen(filepath, _T("rb"));
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

    ret = execPycContent(py_plaint_content, filepath);

    Py_DECREF(py_plaint_content);
    return ret;
}


/*
    PySys_SetArgv is deprecated since python 3.11. It's original behavior will insert script's directory into sys.path.
    It's replace by PyConfig, but PyConfig only update sys.path when executing Py_Main or Py_RunMain.
    So it's better to update sys.path by pyconcrete.
 */
int prependSysPath0(const _CHAR* script_path)
{
    // script_dir = os.path.dirname(script_path)
    // sys.path.insert(0, script_dir)
    int ret = RET_OK;

    PyObject* py_script_path = getFullPath(script_path);
    PyObject* path_module = PyImport_ImportModule("os.path");
    PyObject* dirname_func = PyObject_GetAttrString(path_module, "dirname");
    PyObject* args = Py_BuildValue("(O)", py_script_path);
    PyObject* script_dir = PyObject_CallObject(dirname_func, args);

    PyObject* sys_path = PySys_GetObject("path");
    if (PyList_Insert(sys_path, 0, script_dir) < 0) {
        ret = RET_FAIL;
    }

    Py_XDECREF(py_script_path);
    Py_XDECREF(path_module);
    Py_XDECREF(dirname_func);
    Py_XDECREF(args);
    Py_XDECREF(script_dir);
    return ret;
}


PyObject* getFullPath(const _CHAR* filepath)
{
    // import os.path
    // return os.path.abspath(filepath)
    PyObject* path_module = PyImport_ImportModule("os.path");
    PyObject* abspath_func = PyObject_GetAttrString(path_module, "abspath");
    PyObject* py_filepath = _PyUnicode_FromStringAndSize(filepath, _strlen(filepath));
    PyObject* args = Py_BuildValue("(O)", py_filepath);
    PyObject* py_file_abspath = PyObject_CallObject(abspath_func, args);

    Py_XDECREF(path_module);
    Py_XDECREF(abspath_func);
    Py_XDECREF(py_filepath);
    Py_XDECREF(args);
    return py_file_abspath;
}
