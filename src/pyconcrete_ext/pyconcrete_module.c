#include <stdio.h>
#include <stdlib.h>
#include <Python.h>
#include <bytesobject.h>
#include "pyconcrete.h"  // auto generate at build time

// #define SECRET_KEY_LEN %d // defined in secret_key.h

#if PY_MAJOR_VERSION >= 3
#define IS_PY3K
#endif

static PyObject * fnInfo(PyObject *self, PyObject* null)
{
    return Py_BuildValue("s", "PyConcrete Info() AES 128bit");
}

static PyMethodDef PyConcreteMethods[] = {
    {"info", fnInfo, METH_NOARGS, "Display PyConcrete info"},
    {"encrypt_file", fnEncryptFile, METH_VARARGS, "Encrypt whole file"},
    {"decrypt_file", fnDecryptFile, METH_VARARGS, "Decrypt whole file (not ready)"},
    {"decrypt_buffer", fnDecryptBuffer, METH_VARARGS, "Decrypt buffer"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef PyConcreteMethodDef = {
        PyModuleDef_HEAD_INIT,
        "_pyconcrete",       /* m_name */
        NULL,                /* m_doc */
        -1,                  /* m_size */
        PyConcreteMethods,   /* m_methods */
        NULL,                /* m_reload */
        NULL,                /* m_traverse */
        NULL,                /* m_clear */
        NULL,                /* m_free */
};
#define INITERROR return NULL
#else
#define INITERROR return
#endif


#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC
PyInit__pyconcrete(void)
#else
PyMODINIT_FUNC
init_pyconcrete(void)
#endif
{
    PyObject* m = NULL;
#if PY_MAJOR_VERSION >= 3
    m = PyModule_Create(&PyConcreteMethodDef);
#else
    m = Py_InitModule("_pyconcrete", PyConcreteMethods);
#endif
    if (m == NULL)
        INITERROR;

    g_PyConcreteError = PyErr_NewException("_pyconcrete.Error", NULL, NULL);
    Py_INCREF(g_PyConcreteError);
    PyModule_AddObject(m, "Error", g_PyConcreteError);

#if PY_MAJOR_VERSION >= 3
    return m;
#endif
}
