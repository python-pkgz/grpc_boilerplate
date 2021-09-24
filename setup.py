from setuptools import setup, find_packages


VERSION = "0.5"

setup(
    name='grpc_boilerplate',
    version=VERSION,
    include_package_data=True,
    packages=find_packages(exclude='tests'),
    url='https://github.com/a1fred/grpc_boilerplate',
    license='MIT',
    author='a1fred',
    author_email='demalf@gmail.com',
    description='grpc bolerplate',
    classifiers=[
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
    ],
    test_suite="tests",
)
