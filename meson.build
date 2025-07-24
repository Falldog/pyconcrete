project(
    'pyconcrete',
    'c',
    meson_version: '>= 1.1',
    version: files('VERSION'),
    default_options: ['ext=.pye'],
)

fs = import('fs')

INSTALL_DIR = 'pyconcrete'
PYCONCRETE_EXE_NAME = 'pyconcrete'
PYECLI_EXE_NAME = 'pyecli'
BUILD_UTILITY_DIR = './meson_utility/'

version = meson.project_version()

# The python version will follow which user invoke menson-python
# Such as `python -m pip install ...` or `python -m build ...`
python_ins = import('python').find_installation(pure: false)
python_ver = python_ins.language_version()
python_exe_path = python_ins.full_path()
python_dependency = python_ins.dependency(embed: true)

macro_ext = '-D' + 'PYCONCRETE_EXT="@0@"'.format(get_option('ext'))
macro_version = '-D' + 'PYCONCRETE_VERSION=@0@'.format(version)
c_args = [
    macro_ext,
    macro_version,
]
if host_machine.system() == 'windows'
    c_args += ['-D' + 'WIN32']
endif

#----------------------------
# secret_key.h
#----------------------------

passphrase = get_option('passphrase')
if passphrase == ''
    error('Must assign a passphrase to build pyconcrete')
endif

gen_secret_key = custom_target(
    'gen_secret_key',
    input: join_paths(BUILD_UTILITY_DIR, 'gen_secret_key.py'),
    output: 'secret_key.h',
    build_by_default: true,
    command: [python_exe_path, '@INPUT@', passphrase],
)


#----------------------------
# pyconcrete lib w/ _pyconcrete ext
#----------------------------

if get_option('mode') == 'lib'
    ext_includes = [
        './src/pyconcrete_ext/',
        './src/pyconcrete_ext/openaes/inc/',
    ]
    ext_srcs = [
        gen_secret_key,  # make sure building dependency
        './src/pyconcrete_ext/pyconcrete.c',
        './src/pyconcrete_ext/pyconcrete_module.c',
        './src/pyconcrete_ext/openaes/src/oaes_base64.c',
        './src/pyconcrete_ext/openaes/src/oaes_lib.c',
    ]
    python_ins.extension_module(
        '_pyconcrete',
        ext_srcs,
        c_args: c_args,
        subdir: INSTALL_DIR,
        install: true,
        include_directories: ext_includes,
    )

    python_ins.install_sources(
        [
            'src/pyconcrete/__init__.py',
            'src/pyconcrete/version.py',
            'VERSION',
        ],
        pure: false,
        subdir: INSTALL_DIR,
    )
endif


#----------------------------
# pyconcrete exe
#----------------------------

pyconcrete_src = fs.read('./src/pyconcrete/__init__.py')
pyconcrete_src = pyconcrete_src.strip().replace('\\', '\\\\').replace('\n', '\\n').replace('"', '\\"')
pyconcrete_src_file = configure_file(
    input: './src/pyconcrete_exe/pyconcrete_py_src.h.template',
    output: 'pyconcrete_py_src.h',
    configuration: {
        'DATA': '@0@'.format(pyconcrete_src)
    }
)

if get_option('mode') == 'exe'
    exe_includes = [
        './src/pyconcrete_exe/',
        './src/pyconcrete_ext/',
        './src/pyconcrete_ext/openaes/inc/',
    ]
    exe_srcs = [
        gen_secret_key,  # make sure building dependency
        pyconcrete_src_file,
        './src/pyconcrete_exe/pyconcrete_exe.c',
        './src/pyconcrete_ext/pyconcrete.c',
        './src/pyconcrete_ext/pyconcrete_module.c',
        './src/pyconcrete_ext/openaes/src/oaes_base64.c',
        './src/pyconcrete_ext/openaes/src/oaes_lib.c',
    ]
    executable(
        PYCONCRETE_EXE_NAME,
        exe_srcs,
        c_args: c_args,
        include_directories: exe_includes,
        dependencies: python_dependency,
        install: true,
    )
endif


#----------------------------
# pyconcrete cli
#----------------------------

if get_option('install-cli')
    pyecli_src = fs.read('./src/pyecli/pyecli.py')
    pyecli_src = pyecli_src.strip().replace('\\', '\\\\').replace('\n', '\\n').replace('"', '\\"')
    pyecli_src_file = configure_file(
        input: './src/pyecli/pyecli_py_src.h.template',
        output: 'pyecli_py_src.h',
        configuration: {
            'DATA': '@0@'.format(pyecli_src)
        }
    )

    cli_includes = [
        './src/pyecli/',
        './src/pyconcrete_ext/',
        './src/pyconcrete_ext/openaes/inc/',
    ]
    cli_srcs = [
        gen_secret_key,  # make sure building dependency
        pyecli_src_file,
        pyconcrete_src_file,
        './src/pyecli/pyecli_wrap.c',
        './src/pyconcrete_ext/pyconcrete.c',
        './src/pyconcrete_ext/pyconcrete_module.c',
        './src/pyconcrete_ext/openaes/src/oaes_base64.c',
        './src/pyconcrete_ext/openaes/src/oaes_lib.c',
    ]
    executable(
        PYECLI_EXE_NAME,
        cli_srcs,
        c_args: c_args,
        include_directories: cli_includes,
        dependencies: python_dependency,
        install: true,
    )
endif


#----------------------------
# sdist
#----------------------------

# Meson dist not allow to config include/exclude file rules.
# And it only clone the sources in .git revision, not including the uncommitted files in local.
# So, we need to add dist_cleanup.sh to cleanup redundant files in dist/.
meson.add_dist_script(join_paths(BUILD_UTILITY_DIR, 'dist_cleanup.sh'))
