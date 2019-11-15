# -*- coding: utf-8 -*-


"""NUSL app"""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()

tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'isort>=4.3.3',
    'mock>=2.0.0',
    'pydocstyle>=1.0.0',
    'pytest-cache>=1.0',
    'pytest-invenio>=1.0.2,<1.1.0',
    'pytest-mock>=1.6.0',
    'pytest-cov>=1.8.0',
    'pytest-random-order>=0.5.4',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0',
    'selenium>=3.4.3',
]

extras_require = {
    'docs': [
        'Sphinx>=1.5.1',
    ],
    'tests': tests_require,
    'all': []
}

for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

setup_requires = [
    'pytest-runner>=2.6.2',
]

install_requires = [
    'invenio-oarepo>=1.0.0',
    'invenio-nusl-common>=1.0.0',
    'invenio-oarepo-ui>=1.0.0',
    'click',
    'pycountry',
    'requests',
    'flask',
    'langcodes',
    'sqlalchemy'
    # 'invenio-nusl-theses>=1.0.0'

]

packages = find_packages()

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio_nusl', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='invenio-nusl',
    version=version,
    description=__doc__,
    long_description=readme,
    keywords='NUSL Invenio',
    license='MIT',
    author='Daniel Kopecký',
    author_email='Daniel.Kopecky@techlib.cz',
    url='',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'flask.commands': [
            'nusl = invenio_nusl.cli:nusl',
        ],
        'console_scripts': [

        ],
        'invenio_base.blueprints': [
        ],

        'invenio_config.module': [
        ],
        'invenio_i18n.translations': [
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Development Status :: 3 - Planning',
    ],
)
