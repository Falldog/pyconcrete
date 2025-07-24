#ifndef __PYCONCRETE_MODULE_H__
#define __PYCONCRETE_MODULE_H__

#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC PyInit__pyconcrete(void);
#else
PyMODINIT_FUNC init_pyconcrete(void);
#endif

#endif  // __PYCONCRETE_MODULE_H__
