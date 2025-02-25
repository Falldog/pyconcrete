project(
    'pyconcrete',
    'c',
    meson_version: '>= 1.1',
    version: files('VERSION'),
    default_options: ['ext=.pye'],
)

INSTALL_DIR = 'pyconcrete'
PYCONCRETE_EXE_NAME = 'pyconcrete'
BUILD_UTILITY_DIR = './meson_utility/'

version = meson.project_version()

# The python version will follow which user invoke menson-python
# Such as `python -m pip install ...` or `python -m build ...`
python_ins = import('python').find_installation(pure: false)
python_ver = python_ins.language_version()
python_exe_path = python_ins.full_path()
python_dependency = python_ins.dependency(embed: true)

macro_ext = '-D PYCONCRETE_EXT="@0@"'.format(get_option('ext'))
macro_version = '-D PYCONCRETE_VERSION=@0@'.format(version)


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
    c_args: [macro_ext],
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
    c_args: [
        macro_ext,
        macro_version,
    ],
    include_directories: exe_includes,
    dependencies: python_dependency,
    install: true,
)


#----------------------------
# pyconcrete cli
#----------------------------

# for install the executable cli scripts, we use bindir here.
# meson-python will mapping `bindir`(meson) to `scripts`(python)
# ref:
#   https://github.com/mesonbuild/meson-python/blob/0.17.1/mesonpy/__init__.py#L83
#   https://docs.python.org/3/library/sysconfig.html#installation-paths
install_data(
    './pyecli',
    install_mode: 'rwxr-xr-x',
    install_dir: get_option('bindir'),
)


#----------------------------
# sdist
#----------------------------

# Meson dist not allow to config include/exclude file rules.
# And it only clone the sources in .git revision, not including the uncommitted files in local.
# So, we need to add dist_cleanup.sh to cleanup redundant files in dist/.
meson.add_dist_script(join_paths(BUILD_UTILITY_DIR, 'dist_cleanup.sh'))
