import re
from pathlib import Path

from setuptools import find_packages, setup

long_description = Path('README.md').read_text(encoding='utf-8')

VERSION = re.search(r'__version__ = \'(.*?)\'',
                    Path('is_api/__init__.py').read_text(encoding='utf-8')
                    ).group(1)

requirements = ['requests', 'lxml', 'coloredlogs', 'defusedxml']

extra_requirements = {
    'dev': [
        'pytest',
        'coverage',
        'mock',
        'responses',
    ],
    'docs': ['sphinx']
}

setup(name='muni_is_api',
      version=VERSION,
      description='IS MUNI API Client',
      author='Peter Stanko',
      author_email='stanko@mail.muni.cz',
      maintainer='Peter Stanko',
      url='https://gitlab.fi.muni.cz/grp-kontr2/is-api',
      packages=find_packages(exclude=("tests",)),
      long_description=long_description,
      long_description_content_type='text/markdown',
      include_package_data=True,
      install_requires=requirements,
      extras_require=extra_requirements,
      entry_points={},
      classifiers=[
          "Programming Language :: Python :: 3",
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          "Operating System :: OS Independent",
          "License :: OSI Approved :: Apache Software License",
          'Intended Audience :: Developers',
          'Topic :: Utilities',
      ],
      )
