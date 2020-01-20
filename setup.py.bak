#!/usr/bin/env python3

"""Setup for ProDis"""

import re

from ast import literal_eval
from os import chdir
from pathlib import Path
from setuptools import setup, find_packages


PROJECT_ROOT = 'https://github.com/blubberdiblub/prodis'


def get_version(filename='version.py', path=''):

    """Build version number from git repository tag"""

    version_file_path = Path(path).joinpath(filename)

    try:
        with open(version_file_path, 'r') as f:
            version_file_content = f.read()

    except FileNotFoundError:
        m = None

    else:
        m = re.match(r'^\s*version\s*=\s*(?P<version>.*)$',
                     version_file_content, re.M)

    return literal_eval(m.group('version')) if m else None


def get_long_description(filename='README.md', path=''):

    """Read long description from file"""

    description_file_path = Path(path).joinpath(filename)

    try:
        with open(description_file_path, 'r') as f:
            description_file_content = f.read()

    except FileNotFoundError:
        return None

    return description_file_content


if __name__ == '__main__':
    chdir(Path(__file__).parent)

    setup(
        name='prodis',
        # version=get_version(),
        use_scm_version={
            'write_to': 'src/prodis/_version.py',
        },
        entry_points={
            'console_scripts': [
                'prodis = prodis.cli:main',
            ],
        },
        author='Niels Boehm',
        author_email='blubberdiblub@gmail.com',
        description="Protocol Dissector",
        long_description=get_long_description(),
        long_description_content_type='text/markdown',
        license='MIT',
        keywords=[
            'minecraft',
        ],
        url=PROJECT_ROOT + '.git',
        project_urls={
            'Project': PROJECT_ROOT,
            'Merge Requests': PROJECT_ROOT + '/merge_requests',
        },
        python_requires='>=3.7',
        setup_requires=[
            'setuptools_scm',
        ],
        install_requires=[
        ],
        extras_require={
            'test': ['pytest'],
        },
        test_suite='tests',
        packages=find_packages(
            where='src',
            exclude=[
                'tests',
                'tests.*',
                '*.tests',
                '*.tests.*',
            ],
        ),
        package_dir={'': 'src'},
        zip_safe=True,
        classifiers=[
            'Development Status :: 3 - Alpha',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3 :: Only',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
        ],
    )
