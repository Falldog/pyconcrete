#ifndef PYCONCRETE_H
#define PYCONCRETE_H

extern PyObject* g_PyConcreteError;

PyObject * fnEncryptFile(PyObject* self, PyObject* args);
PyObject * fnDecryptFile(PyObject* self, PyObject* args);
PyObject * fnDecryptBuffer(PyObject* self, PyObject* args);

#endif  // PYCONCRETE_H
