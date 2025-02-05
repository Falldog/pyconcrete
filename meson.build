project(
    'pyconcrete',
    'c',
    meson_version: '>= 1.1',
)

INSTALL_DIR = 'pyconcrete'
PYCONCRETE_EXE_NAME = 'pyconcrete'
BUILD_UTILITY_DIR = './meson_utility/'
version = run_command('cat', 'VERSION', check: true).stdout().strip()
python_ins = import('python').find_installation(pure: false)
python_ver = python_ins.language_version()


#----------------------------
# secret_key.h
#----------------------------

# pip install . -Csetup-args="-Dpassphrase=ABC"
passphrase = get_option('passphrase')
prog_python = find_program('python')
gen_secret_key = custom_target(
    'gen_secret_key',
    input: join_paths(BUILD_UTILITY_DIR, 'gen_secret_key.py'),
    output: 'secret_key.h',
    build_by_default: true,
    command: [prog_python, '@INPUT@', passphrase],
)


#----------------------------
# _pyconcrete ext
#----------------------------

ext_includes = [
    './src/pyconcrete_ext/',
    './src/pyconcrete_ext/openaes/inc/',
]
ext_srcs = [
    './src/pyconcrete_ext/pyconcrete.c',
    './src/pyconcrete_ext/pyconcrete_module.c',
    './src/pyconcrete_ext/openaes/src/oaes_base64.c',
    './src/pyconcrete_ext/openaes/src/oaes_lib.c',
]
python_ins.extension_module(
    '_pyconcrete',
    ext_srcs,
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

python_ins.install_sources(
    join_paths(BUILD_UTILITY_DIR, 'pyconcrete.pth'),
    pure: false,
    # subdir: <install on the dist-packages>
)


#----------------------------
# pyconcrete exe
#----------------------------

# ref: https://github.com/mesonbuild/meson/issues/5629
python_dep = dependency('python-@0@-embed'.format(python_ver), required: false)
if not python_dep.found()
    python_dep = dependency('python-@0@'.format(python_ver))
endif

exe_includes = [
    './src/pyconcrete_exe/',
    './src/pyconcrete_ext/',
    './src/pyconcrete_ext/openaes/inc/',
]
exe_srcs = [
    './src/pyconcrete_exe/pyconcrete_exe.c',
    './src/pyconcrete_ext/pyconcrete.c',
    './src/pyconcrete_ext/openaes/src/oaes_base64.c',
    './src/pyconcrete_ext/openaes/src/oaes_lib.c',
]
executable(
    PYCONCRETE_EXE_NAME,
    exe_srcs,
    c_args: '-D PYCONCRETE_VERSION=@0@'.format(version),
    include_directories: exe_includes,
    dependencies: python_dep,
    install: true,
)
