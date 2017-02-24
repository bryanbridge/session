from setuptools import setup, find_packages

setup(
    name='session',
    version='0.1',
    description='Manage programming project sessions.',
    url=None,
    author='bryanbridge',
    author_email=None,
    license=None,
    packages=find_packages(exclude=[]),
    package_data={'': ['dir.ini']},
    include_package_data=True,
    install_requires=['termcolor'],
    zip_safe=False)
