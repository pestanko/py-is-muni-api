from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = ['requests', 'lxml']

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
      version='0.1',
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
