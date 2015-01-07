/* 
 * ---------------------------------------------------------------------------
 * OpenAES License
 * ---------------------------------------------------------------------------
 * Copyright (c) 2013, Nabil S. Al Ramli, www.nalramli.com
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * 
 *   - Redistributions of source code must retain the above copyright notice,
 *     this list of conditions and the following disclaimer.
 *   - Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 * ---------------------------------------------------------------------------
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define OAES_DEBUG 1
#include "oaes_lib.h"
#include "oaes_base64.h"

#if defined(_WIN32) && !defined(__SYMBIAN32__)
#include <io.h>
#else
__inline static int setmode(int a, int b)
{
	return 0;
}
#endif

typedef OAES_RET (*oaes_thread_func_t)(void *);

#if defined(_WIN32) && !defined(__SYMBIAN32__)
#include <windows.h>
#include <process.h>

uintptr_t start_thread(oaes_thread_func_t f, void *p)
{
	uintptr_t _id = _beginthreadex(NULL, 0, (int (__stdcall *)(void *)) f, p, 0, NULL);

	if( -1L == _id )
		_id = 0;
	return _id;
}

void join_thread(uintptr_t id)
{
	if( NULL == id )
		return;

	WaitForSingleObject((HANDLE) id, INFINITE);
}
#else
#include <pthread.h>

uintptr_t start_thread(oaes_thread_func_t f, void *p)
{
	pthread_t _id = NULL;
	pthread_attr_t attr;
	int retval = 0;

	(void) pthread_attr_init(&attr);
	(void) pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_JOINABLE);
	retval = pthread_create(&_id, &attr, f, p);
	return _id;
}

void join_thread(uintptr_t id)
{
	if( NULL == id )
		return;

	pthread_join(id, NULL);
}
#endif

#ifndef __max
	#define __max(a,b)  (((a) > (b)) ? (a) : (b))
#endif // __max

#ifndef __min
	#define __min(a,b)  (((a) < (b)) ? (a) : (b))
#endif // __min

#if defined(_WIN32) && !defined(__SYMBIAN32__)
#else
	#ifndef _fprintf_p
		#define _fprintf_p fprintf
	#endif // _fprintf_p
#endif

#define OAES_BASE64_LEN_ENC 3072
#define OAES_BASE64_LEN_DEC 4096
#define OAES_AES_LEN_ENC 4096 - 2 * OAES_BLOCK_SIZE
#define OAES_AES_LEN_DEC 4096
#define OAES_BUF_LEN 4096
#define OAES_THREADS 16

static void usage( const char * exe_name )
{
	if( NULL == exe_name )
		return;
	
	_fprintf_p( stderr,
			"Usage:\n"
			"  %1$s gen-key < 128 | 192 | 256 > <key_file>\n"
			"\n"
			"  %1$s <base64_command> [options]\n"
			"\n"
			"    base64_command:\n"
			"      base64-enc: encode\n"
			"      base64-dec:  decode\n"
			"\n"
			"    options:\n"
			"      --in <path_in>\n"
			"      --out <path_out>\n"
			"\n"
			"  %1$s <aes_command> --key <base64_encoded_key_data> [options]\n"
			"  %1$s <aes_command> --key-file <key_file> [options]\n"
			"\n"
			"    aes_command:\n"
			"      aes-enc: encrypt\n"
			"      aes-dec:  decrypt\n"
			"\n"
			"    options:\n"
			"      --ecb: use ecb mode instead of cbc\n"
			"      --in <path_in>\n"
			"      --out <path_out>\n"
			"\n",
			exe_name
	);
}

static uint8_t _key_data[32] = "";
static size_t _key_data_len = 0;
static short _is_ecb = 0;

typedef struct _do_block
{
	intptr_t id;
	size_t in_len;
	uint8_t in[OAES_BUF_LEN];
	size_t out_len;
	uint8_t *out;
} do_block;

// caller must free b->out if it's not NULL
static OAES_RET _do_base64_encode(do_block *b)
{
	OAES_CTX * ctx = NULL;
	OAES_RET _rc = OAES_RET_SUCCESS;

	if( NULL == b )
		return OAES_RET_ARG1;

	b->out = NULL;
	b->out_len = 0;
	_rc = oaes_base64_encode(
		b->in, b->in_len, (char *) b->out, &(b->out_len) );
	if( OAES_RET_SUCCESS != _rc )
	{
		fprintf(stderr, "Error: Failed to encrypt.\n");
		oaes_free(&ctx);
		return _rc;
	}
	b->out = (uint8_t *) calloc(b->out_len, sizeof(uint8_t));
	if( NULL == b->out )
	{
		fprintf(stderr, "Error: Failed to allocate memory.\n");
		oaes_free(&ctx);
		return OAES_RET_MEM;
	}
	_rc = oaes_base64_encode(
		b->in, b->in_len, (char *) b->out, &(b->out_len) );

	return _rc;
}

// caller must free b->out if it's not NULL
static OAES_RET _do_base64_decode(do_block *b)
{
	OAES_CTX * ctx = NULL;
	OAES_RET _rc = OAES_RET_SUCCESS;

	if( NULL == b )
		return OAES_RET_ARG1;

	b->out = NULL;
	b->out_len = 0;
	_rc = oaes_base64_decode(
		(const char *) b->in, b->in_len, b->out, &(b->out_len) );
	if( OAES_RET_SUCCESS != _rc )
	{
		fprintf(stderr, "Error: Failed to decrypt.\n");
		oaes_free(&ctx);
		return _rc;
	}
	b->out = (uint8_t *) calloc(b->out_len, sizeof(uint8_t));
	if( NULL == b->out )
	{
		fprintf(stderr, "Error: Failed to allocate memory.\n");
		oaes_free(&ctx);
		return OAES_RET_MEM;
	}
	_rc = oaes_base64_decode(
		(const char *) b->in, b->in_len, b->out, &(b->out_len) );

	return _rc;
}

// caller must free b->out if it's not NULL
static OAES_RET _do_aes_encrypt(do_block *b)
{
	OAES_CTX * ctx = NULL;
	OAES_RET _rc = OAES_RET_SUCCESS;

	if( NULL == b )
		return OAES_RET_ARG1;

	ctx = oaes_alloc();
	if( NULL == ctx )
	{
		fprintf(stderr, "Error: Failed to initialize OAES.\n");
		return OAES_RET_MEM;
	}

	if( _is_ecb )
		if( OAES_RET_SUCCESS != oaes_set_option( ctx, OAES_OPTION_ECB, NULL ) )
			fprintf(stderr, "Error: Failed to set OAES options.\n");

	oaes_key_import_data( ctx, _key_data, _key_data_len );

	b->out = NULL;
	b->out_len = 0;
	_rc = oaes_encrypt( ctx,
			b->in, b->in_len, b->out, &(b->out_len) );
	if( OAES_RET_SUCCESS != _rc )
	{
		fprintf(stderr, "Error: Failed to encrypt.\n");
		oaes_free(&ctx);
		return _rc;
	}
	b->out = (uint8_t *) calloc(b->out_len, sizeof(uint8_t));
	if( NULL == b->out )
	{
		fprintf(stderr, "Error: Failed to allocate memory.\n");
		oaes_free(&ctx);
		return OAES_RET_MEM;
	}
	_rc = oaes_encrypt( ctx,
			b->in, b->in_len, b->out, &(b->out_len) );

	if( OAES_RET_SUCCESS !=  oaes_free(&ctx) )
		fprintf(stderr, "Error: Failed to uninitialize OAES.\n");
	
	return _rc;
}

// caller must free b->out if it's not NULL
static OAES_RET _do_aes_decrypt(do_block *b)
{
	OAES_CTX * ctx = NULL;
	OAES_RET _rc = OAES_RET_SUCCESS;

	if( NULL == b )
		return OAES_RET_ARG1;

	ctx = oaes_alloc();
	if( NULL == ctx )
	{
		fprintf(stderr, "Error: Failed to initialize OAES.\n");
		return OAES_RET_MEM;
	}

	if( _is_ecb )
		if( OAES_RET_SUCCESS != oaes_set_option( ctx, OAES_OPTION_ECB, NULL ) )
			fprintf(stderr, "Error: Failed to set OAES options.\n");

	oaes_key_import_data( ctx, _key_data, _key_data_len );

	b->out = NULL;
	b->out_len = 0;
	_rc = oaes_decrypt( ctx,
			b->in, b->in_len, b->out, &(b->out_len) );
	if( OAES_RET_SUCCESS != _rc )
	{
		fprintf(stderr, "Error: Failed to decrypt.\n");
		oaes_free(&ctx);
		return _rc;
	}
	b->out = (uint8_t *) calloc(b->out_len, sizeof(uint8_t));
	if( NULL == b->out )
	{
		fprintf(stderr, "Error: Failed to allocate memory.\n");
		oaes_free(&ctx);
		return OAES_RET_MEM;
	}
	_rc = oaes_decrypt( ctx,
			b->in, b->in_len, b->out, &(b->out_len) );

	if( OAES_RET_SUCCESS !=  oaes_free(&ctx) )
		fprintf(stderr, "Error: Failed to uninitialize OAES.\n");
	
	return _rc;
}

int main(int argc, char** argv)
{
	size_t _i = 0, _j = 0;
	size_t _read_len = 0;
	char *_file_in = NULL, *_file_out = NULL, *_file_k = NULL;
	int _op = 0;
	FILE *_f_in = stdin, *_f_out = stdout, *_f_k = NULL;
	do_block _b[OAES_THREADS];
	
	fprintf( stderr, "\n"
		"*******************************************************************************\n"
		"* OpenAES %-10s                                                          *\n"
		"* Copyright (c) 2013, Nabil S. Al Ramli, www.nalramli.com                     *\n"
		"*******************************************************************************\n\n",
		OAES_VERSION );

	// pad the key
	for( _j = 0; _j < 32; _j++ )
		_key_data[_j] = _j + 1;

	if( argc < 2 )
	{
		usage( argv[0] );
		return EXIT_FAILURE;
	}

	if( 0 == strcmp( argv[1], "gen-key" ) )
	{
		OAES_CTX *_oaes = NULL;
		uint8_t _buf[16384];
		size_t _buf_len = sizeof(_buf);
		OAES_RET _rc = OAES_RET_SUCCESS;

		_i++;
		_i++; // key_length
		_i++; // key_file
		if( _i >= argc )
		{
			fprintf( stderr, "Error: No value specified for '%s'.\n",
					argv[1] );
			usage( argv[0] );
			return EXIT_FAILURE;
		}
		_key_data_len = atoi( argv[_i - 1] );
		_file_k = argv[_i];
		_oaes = oaes_alloc();
		if( NULL == _oaes )
		{
			fprintf(stderr, "Error: Failed to initialize OAES.\n");
			return OAES_RET_MEM;
		}
		switch( _key_data_len )
		{
			case 128:
				_rc = oaes_key_gen_128(_oaes);
				break;
			case 192:
				_rc = oaes_key_gen_192(_oaes);
				break;
			case 256:
				_rc = oaes_key_gen_256(_oaes);
				break;
			default:
				fprintf( stderr, "Error: Invalid value [%s] specified for '%s'.\n",
						argv[_i - 1], argv[_i - 2] );
				oaes_free(&_oaes);
				return EXIT_FAILURE;
		}
		if( OAES_RET_SUCCESS != _rc )
		{
			fprintf( stderr, "Error: Failed to generate OAES %lu bit key.\n",
				_key_data_len );
			oaes_free(&_oaes);
			return EXIT_FAILURE;
		}
		if( OAES_RET_SUCCESS != oaes_key_export(_oaes, _buf, &_buf_len) )
		{
			fprintf( stderr, "Error: Failed to retrieve key length %lu.\n",
				_key_data_len );
			oaes_free(&_oaes);
			return EXIT_FAILURE;
		}
		oaes_free(&_oaes);
		if( 0 == access(_file_k, 00) )
		{
			fprintf(stderr,
				"Error: '%s' already exists.\n", _file_k);
			return EXIT_FAILURE;
		}
		_f_k = fopen(_file_k, "wb");
		if( NULL == _f_k )
		{
			fprintf(stderr,
				"Error: Failed to open '%s' for writing.\n", _file_k);
			return EXIT_FAILURE;
		}
		fwrite(_buf, sizeof(uint8_t), _buf_len, _f_k);
		fclose(_f_k);
		return EXIT_SUCCESS;
	}
	else if( 0 == strcmp( argv[1], "base64-enc" ) )
	{
		_op = 0;
		_read_len = OAES_BASE64_LEN_ENC;
	}
	else if( 0 == strcmp( argv[1], "base64-dec" ) )
	{
		_op = 1;
		_read_len = OAES_BASE64_LEN_DEC;
	}
	else if( 0 == strcmp( argv[1], "aes-enc" ) )
	{
		_op = 2;
		_read_len = OAES_AES_LEN_ENC;
	}
	else if( 0 == strcmp( argv[1], "aes-dec" ) )
	{
		_op = 3;
		_read_len = OAES_AES_LEN_DEC;
	}
	else
	{
		fprintf(stderr, "Error: Unknown command '%s'.", argv[1]);
		usage( argv[0] );
		return EXIT_FAILURE;
	}

	for( _i = 2; _i < argc; _i++ )
	{
		int _found = 0;

		if( 0 == strcmp( argv[_i], "--ecb" ) )
		{
			_found = 1;
			_is_ecb = 1;
		}
		
		if( 0 == strcmp( argv[_i], "--key" ) )
		{
			uint8_t *_buf = NULL;
			size_t _buf_len = 0;
			_found = 1;
			_i++; // base64_encoded_key_data
			if( _i >= argc )
			{
				fprintf(stderr, "Error: No value specified for '%s'.\n",
						argv[_i - 1]);
				usage( argv[0] );
				return EXIT_FAILURE;
			}
			if( oaes_base64_decode(argv[_i], strlen(argv[_i]), NULL, &_buf_len) )
			{
				fprintf(stderr, "Error: Invalid value for '%s'.\n",
						argv[_i - 1]);
				usage( argv[0] );
				return EXIT_FAILURE;
			}
			_buf = (uint8_t *) calloc(_buf_len, sizeof(uint8_t));
			if( NULL == _buf )
			{
				fprintf(stderr, "Error: Failed to allocate memory.\n");
				return EXIT_FAILURE;
			}
			if( oaes_base64_decode(argv[_i], strlen(argv[_i]), _buf, &_buf_len) )
			{
				free(_buf);
				fprintf(stderr, "Error: Invalid value for '%s'.\n",
						argv[_i - 1]);
				usage( argv[0] );
				return EXIT_FAILURE;
			}
			_key_data_len = _buf_len;
			if( 16 >= _key_data_len )
				_key_data_len = 16;
			else if( 24 >= _key_data_len )
				_key_data_len = 24;
			else
				_key_data_len = 32;
			memcpy(_key_data, _buf, __min(32, _buf_len));
			for( _j = 0; _j < _buf_len; _j++ )
			{
				_key_data[_j % 32] ^= _buf[_j];
			}
			free(_buf);
		}
		
		if( 0 == strcmp( argv[_i], "--key-file" ) )
		{
			OAES_CTX *_ctx = NULL;
			uint8_t _buf[16384];
			size_t _read = 0;

			_found = 1;
			_i++; // key_file
			if( _i >= argc )
			{
				fprintf(stderr, "Error: No value specified for '%s'.\n",
						argv[_i - 1]);
				usage( argv[0] );
				return EXIT_FAILURE;
			}
			_file_k = argv[_i];
			_ctx = oaes_alloc();
			if( NULL == _ctx )
			{
				fprintf(stderr, "Error: Failed to initialize OAES.\n");
				return OAES_RET_MEM;
			}
			_f_k = fopen(_file_k, "rb");
			if( NULL == _f_k )
			{
				fprintf(stderr,
					"Error: Failed to open '%s' for reading.\n", _file_k);
				oaes_free(&_ctx);
				return EXIT_FAILURE;
			}
			_read = fread(_buf, sizeof(uint8_t), sizeof(_buf), _f_k);
			fclose(_f_k);
			if( OAES_RET_SUCCESS != oaes_key_import(_ctx, _buf, _read) )
			{
				fprintf(stderr,
					"Error: Failed to import '%s'.\n", _file_k);
				oaes_free(&_ctx);
				return EXIT_FAILURE;
			}
			_key_data_len = sizeof(_key_data);
			if( OAES_RET_SUCCESS != oaes_key_export_data(_ctx, _key_data, &_key_data_len) )
			{
				fprintf(stderr,
					"Error: Failed to export '%s' data.\n", _file_k);
				oaes_free(&_ctx);
				return EXIT_FAILURE;
			}
			oaes_free(&_ctx);
		}
		
		if( 0 == strcmp( argv[_i], "--in" ) )
		{
			_found = 1;
			_i++; // path_in
			if( _i >= argc )
			{
				fprintf(stderr, "Error: No value specified for '%s'.\n",
						argv[_i - 1]);
				usage( argv[0] );
				return EXIT_FAILURE;
			}
			_file_in = argv[_i];
		}
		
		if( 0 == strcmp( argv[_i], "--out" ) )
		{
			_found = 1;
			_i++; // path_out
			if( _i >= argc )
			{
				fprintf(stderr, "Error: No value specified for '%s'.\n",
						argv[_i - 1]);
				usage( argv[0] );
				return EXIT_FAILURE;
			}
			_file_out = argv[_i];
		}
		
		if( 0 == _found )
		{
			fprintf(stderr, "Error: Invalid option '%s'.\n", argv[_i]);
			usage( argv[0] );
			return EXIT_FAILURE;
		}			
	}

	switch(_op)
	{
	case 0:
	case 1:
		break;
	case 2:
	case 3:
		if( 0 == _key_data_len )
		{
			char _key_data_ent[8193] = "";
			uint8_t *_buf = NULL;
			size_t _buf_len = 0;

			fprintf(stderr, "Enter base64-encoded key: ");
			scanf("%8192s", _key_data_ent);
			if( oaes_base64_decode(
					_key_data_ent, strlen(_key_data_ent), NULL, &_buf_len ) )
			{
				fprintf(stderr, "Error: Invalid value for '%s'.\n",
						argv[_i - 1]);
				usage( argv[0] );
				return EXIT_FAILURE;
			}
			_buf = (uint8_t *) calloc(_buf_len, sizeof(uint8_t));
			if( NULL == _buf )
			{
				fprintf(stderr, "Error: Failed to allocate memory.\n");
				return EXIT_FAILURE;
			}
			if( oaes_base64_decode(
					_key_data_ent, strlen(_key_data_ent), _buf, &_buf_len ) )
			{
				free(_buf);
				fprintf(stderr, "Error: Invalid value for '%s'.\n",
						argv[_i - 1]);
				usage( argv[0] );
				return EXIT_FAILURE;
			}
			_key_data_len = _buf_len;
			if( 16 >= _key_data_len )
				_key_data_len = 16;
			else if( 24 >= _key_data_len )
				_key_data_len = 24;
			else
				_key_data_len = 32;
			memcpy(_key_data, _buf, __min(32, _buf_len));
			for( _j = 0; _j < _buf_len; _j++ )
			{
				_key_data[_j % 32] ^= _buf[_j];
			}
			free(_buf);
		}
		break;
	default:
		break;
	}

	if( _file_in )
	{
		_f_in = fopen(_file_in, "rb");
		if( NULL == _f_in )
		{
			fprintf(stderr,
				"Error: Failed to open '%s' for reading.\n", _file_in);
			return EXIT_FAILURE;
		}
	}
	else
	{
		if( setmode(fileno(stdin), 0x8000) < 0 )
			fprintf(stderr,"Error: Failed in setmode().\n");
		_f_in = stdin;
	}

	if( _file_out )
	{
		if( 0 == access(_file_out, 00) )
		{
			fprintf(stderr,
				"Error: '%s' already exists.\n", _file_out);
			return EXIT_FAILURE;
		}
		_f_out = fopen(_file_out, "wb");
		if( NULL == _f_out )
		{
			fprintf(stderr,
				"Error: Failed to open '%s' for writing.\n", _file_out);
			if( _file_in )
				fclose(_f_in);
			return EXIT_FAILURE;
		}
	}
	else
	{
		if( setmode(fileno(stdout), 0x8000) < 0 )
			fprintf(stderr, "Error: Failed in setmode().\n");
		_f_out = stdout;
	}

	_i = 0;
	while( _b[_i].in_len =
		fread(_b[_i].in, sizeof(uint8_t), _read_len, _f_in) )
	{
		switch(_op)
		{
		case 0:
			_b[_i].id = start_thread(_do_base64_encode, &(_b[_i]));
			if( NULL == _b[_i].id )
				fprintf(stderr, "Error: Failed to start encryption.\n");
			break;
		case 1:
			_b[_i].id = start_thread(_do_base64_decode, &(_b[_i]));
			if( NULL == _b[_i].id )
				fprintf(stderr, "Error: Failed to start decryption.\n");
			break;
		case 2:
			_b[_i].id = start_thread(_do_aes_encrypt, &(_b[_i]));
			if( NULL == _b[_i].id )
				fprintf(stderr, "Error: Failed to start encryption.\n");
			break;
		case 3:
			_b[_i].id = start_thread(_do_aes_decrypt, &(_b[_i]));
			if( NULL == _b[_i].id )
				fprintf(stderr, "Error: Failed to start decryption.\n");
			break;
		default:
			break;
		}
		if( OAES_THREADS == _i + 1 )
		{
			for( _j = 0; _j < OAES_THREADS; _j++ )
			{
				if( _b[_j].id )
				{
					join_thread(_b[_j].id);
					_b[_j].id = 0;
					if( _b[_j].out )
					{
						fwrite(_b[_j].out, sizeof(uint8_t), _b[_j].out_len, _f_out);
						free(_b[_j].out);
						_b[_j].out = NULL;
					}
				}
			}
		}
		_i = (_i + 1) % OAES_THREADS;
	}
	for( _j = 0; _j < _i; _j++ )
	{
		if( _b[_j].id )
		{
			join_thread(_b[_j].id);
			_b[_j].id = 0;
			if( _b[_j].out )
			{
				fwrite(_b[_j].out, sizeof(uint8_t), _b[_j].out_len, _f_out);
				free(_b[_j].out);
				_b[_j].out = NULL;
			}
		}
	}


	if( _file_in )
		fclose(_f_in);
	if( _file_out )
		fclose(_f_out);

	fprintf(stderr, "done.\n");
	return (EXIT_SUCCESS);
}
