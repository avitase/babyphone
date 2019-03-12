import setuptools

setuptools.setup(
    name='camera',
    version='0.0.1',
    author='Nis Meinert',
    author_email='mail@nismeinert.de',
    description='Camera for babyphone (server)',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'picamera==1.13',
        'pyzmq==17.1.2',
    ],
)
