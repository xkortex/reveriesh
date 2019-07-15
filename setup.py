import os
from setuptools import find_packages, setup
from distutils.util import convert_path

pkgname = 'reveriesh'


def get_version(pkg_name):
    main_ns = {}
    ver_path = convert_path('{}/version.py'.format(pkg_name))
    with open(ver_path) as ver_file:
        text = ver_file.read()
    try:
        ver = text.split('version=')[1]
    except IndexError:
        raise RuntimeError('Could not parse version string: {}'.format(text))
    return ver.strip('"').strip("'")


packages = find_packages()

deps = [
]

setup(
    name=pkgname,
    version=get_version(pkgname),
    script_name='setup.py',
    python_requires='>=2.7,!=3.0.*,!=3.1.*',
    zip_safe=False,
    packages=packages,
    install_requires=deps,
    include_package_data=True,
    extras_require={
        'server': ['future']
    }
)
