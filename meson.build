project('pyconcrete', 'c')


#----------------------------
# secret_key.h
#----------------------------

# pip install . -Csetup-args="-Dpassphrase=ABC"
passphrase = get_option('passphrase')
python3 = find_program('python3')
gen_secret_key = custom_target(
    'gen_secret_key',
    input: './meson_utility/gen_secret_key.py',
    output: 'secret_key.h',
    build_by_default: true,
    command: [python3, '@INPUT@', passphrase],
)


#----------------------------
# _pyconcrete ext
#----------------------------

py_ext = import('python').find_installation(pure: false)
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
py_ext.extension_module(
    '_pyconcrete',
    ext_srcs,
    subdir: 'pyconcrete',
    install: true,
    include_directories: ext_includes,
)

py_ext.install_sources(
    [
        'src/pyconcrete/__init__.py',
        'src/pyconcrete/version.py',
    ],
    pure: false,
    subdir: 'pyconcrete',
)

py_ext.install_sources(
    'meson_utility/pyconcrete.pth',
    pure: false,
    # subdir: <install on the dist-packages>
)
