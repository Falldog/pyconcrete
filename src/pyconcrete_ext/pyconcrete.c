//
// Copyright 2015 Falldog Hsieh <falldog7@gmail.com>
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <stdio.h>
#include <stdlib.h>
#include <Python.h>
#include <bytesobject.h>
#include "oaes_lib.h"
#include "secret_key.h"  // auto generate at build time

// #define SECRET_KEY_LEN %d // defined in secret_key.h
#define AES_BLOCK_SIZE 16

#if PY_MAJOR_VERSION >= 3
#define IS_PY3K
#endif

const static unsigned int TRUE = 1;
const static unsigned int FALSE = 0;

static PyObject* g_PyConcreteError = NULL;

static void print_buffer(unsigned char* buf, int size)
{
    int i = 0;
    printf("print buffer 0x%P(%d) ", buf, size);
    for(i=0 ; i<size ; ++i)
        printf("%X ", *(buf+i));
    printf("\n");
}

static void KeyAlloc(OAES_CTX** key)
{
    *key = oaes_alloc();
    oaes_key_gen_128(*key);
    oaes_key_import_data(*key, GetSecretKey(), SECRET_KEY_LEN);
}

static void KeyDestroy(OAES_CTX** key)
{
    oaes_free(key);
}

static PyObject * fnInfo(PyObject *self, PyObject* null)
{
    return Py_BuildValue("s", "PyConcrete Info() AES 128bit");
}

static PyObject * fnEncryptFile(PyObject *self, PyObject* args)
{
    FILE* src = NULL;
    FILE* dest = NULL;
    const char* src_filepath = NULL;
    const char* dest_filepath = NULL;
    unsigned char buf[AES_BLOCK_SIZE];
    OAES_CTX* key = NULL;
    size_t s;
    int is_last_block_fragment = FALSE;
    
    if (!PyArg_ParseTuple(args, "ss", &src_filepath, &dest_filepath))
        return NULL;
    
    // printf("fnEncryptFile() src=%s, dest=%s\n", src_filepath, dest_filepath);
    
    KeyAlloc(&key);
    {
        src = fopen(src_filepath, "rb");
        if(!src)
        {
            PyErr_Format(g_PyConcreteError, "open source file fail! (%s)", src_filepath);
            return NULL;
        }
        
        dest = fopen(dest_filepath, "wb");
        if(!dest)
        {
            fclose(src);
            PyErr_Format(g_PyConcreteError, "open destination file fail! (%s)", dest_filepath);
            return NULL;
        }
        
        while(!feof(src))
        {
            s = fread(buf, 1, AES_BLOCK_SIZE, src);
            if(s == AES_BLOCK_SIZE)
            {
                oaes_encrypt_block(key, buf, AES_BLOCK_SIZE);
            }
            else
            {
                is_last_block_fragment = TRUE;
                memset(buf+s, AES_BLOCK_SIZE-s, AES_BLOCK_SIZE-s);  // fill padding number
                oaes_encrypt_block(key, buf, AES_BLOCK_SIZE);
                // printf("fnEncryptFile() is_last_block_fragment=TRUE, padding num = %d\n", AES_BLOCK_SIZE-s);
            }
            fwrite(buf, 1, AES_BLOCK_SIZE, dest);
        }
        if(!is_last_block_fragment)  // fill last padding block
        {
            memset(buf, AES_BLOCK_SIZE, AES_BLOCK_SIZE);
            oaes_encrypt_block(key, buf, AES_BLOCK_SIZE);
            fwrite(buf, 1, AES_BLOCK_SIZE, dest);
            // printf("fnEncryptFile() is_last_block_fragment=FALSE, padding num = %d\n", AES_BLOCK_SIZE);
        }
        
        fclose(src);
        fclose(dest);
    }
    KeyDestroy(&key);
    
    Py_INCREF(Py_True);
    return Py_True;
}

static PyObject * fnDecryptFile(PyObject *self, PyObject* args)
{
    FILE* src = NULL;
    const char* src_filepath = NULL;
    //unsigned char buf[AES_BLOCK_SIZE];
    unsigned char* plaint = NULL;
    unsigned char* cur_plaint = NULL;
    OAES_CTX* key = NULL;
    int is_find_last_block = FALSE;
    int file_size = 0;
    
    if (!PyArg_ParseTuple(args, "s", &src_filepath))
        return NULL;
    
    KeyAlloc(&key);
    {
        /*
        src = fopen(src_filepath, "rb");
        
        // error handling
        // if(!src)
        // {
        // }
        
        fseek(src, 0, SEEK_END);
        file_size = ftell(src);
        fseek(src, 0, SEEK_SET);
        
        plaint = (unsigned char*) malloc( file_size * sizeof(unsigned char) );
        cur_plaint = plaint;
        
        while(!feof(src))
        {
            s = fread(cur_plaint, 1, AES_BLOCK_SIZE, src);
            if(!feof(src))
            {
                oaes_decrypt_block(key, cur_plaint, AES_BLOCK_SIZE);
                cur_plaint += AES_BLOCK_SIZE;
            }
            else // last block
            {
            }
        }
        fclose(src);
        */
    }
    KeyDestroy(&key);
    return NULL;
}

static PyObject * fnDecryptBuffer(PyObject *self, PyObject* args)
{
    Py_ssize_t cipher_buf_size = 0;
    Py_ssize_t plain_buf_size = 0;
    Py_ssize_t proc_size = 0;        // process of decryption size
    int padding_size = 0;            // last block padding size
    unsigned char* cipher_buf = NULL;
    unsigned char* plain_buf = NULL;
    unsigned char* cur_cipher = NULL;
    unsigned char* cur_plain = NULL;
    unsigned char last_block[AES_BLOCK_SIZE];
    PyObject* py_plain_obj = NULL;
    OAES_CTX* key = NULL;

    if(!PyArg_ParseTuple(args, "s#", &cipher_buf, &cipher_buf_size))
        return NULL;
    
    if(cipher_buf_size % AES_BLOCK_SIZE != 0)  // file size not match, maybe not encrypted file
    {
        PyErr_SetString(g_PyConcreteError, "this file content doesn't matched");
        return NULL;
    }
    
    KeyAlloc(&key);
    {
        // decrypt last block first
        memcpy(last_block, cipher_buf+cipher_buf_size-AES_BLOCK_SIZE, AES_BLOCK_SIZE);
        
        oaes_decrypt_block(key, last_block, AES_BLOCK_SIZE);
        //print_buffer(last_block, AES_BLOCK_SIZE);
        padding_size = last_block[AES_BLOCK_SIZE-1];
        plain_buf_size = cipher_buf_size - padding_size;
        
        // printf("fnDecryptBuffer() cipher_size=%d, plain_size=%d padding_size=%d\n", cipher_buf_size, plain_buf_size, padding_size);
        
        py_plain_obj = PyBytes_FromStringAndSize(NULL, plain_buf_size);  // allocate whole string memory first, fill later
        plain_buf = PyBytes_AS_STRING(py_plain_obj);
        
        cur_plain = plain_buf;
        cur_cipher = cipher_buf;
        
        while(proc_size < plain_buf_size)
        {
            if(proc_size + AES_BLOCK_SIZE > plain_buf_size)
            {
                break;  // the last block already decrypt
            }
            else
            {
                memcpy(cur_plain, cur_cipher, AES_BLOCK_SIZE);
                oaes_decrypt_block(key, cur_plain, AES_BLOCK_SIZE);
                
                cur_plain += AES_BLOCK_SIZE;
                cur_cipher += AES_BLOCK_SIZE;
                proc_size += AES_BLOCK_SIZE;
            }
        }
        
        // fill last fragment block
        if(padding_size < AES_BLOCK_SIZE)
            memcpy(cur_plain, last_block, AES_BLOCK_SIZE-padding_size);
    }
    KeyDestroy(&key);
    return py_plain_obj;
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

