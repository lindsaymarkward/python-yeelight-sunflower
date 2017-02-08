from distutils.core import setup

# TODO check/add Python 2 support

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    "Topic :: Software Development :: Libraries :: Python Modules",
    'License :: OSI Approved :: MIT License',
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6"
]

setup(
    name='yeelightsunflower',
    version='0.0.1',
    packages=['yeelightsunflower'],
    classifiers=classifiers,
    url='https://github.com/lindsaymarkward/python-yeelight-sunflower',
    license='MIT',
    author='Lindsay Ward',
    author_email='lindsay.ward@jcu.edu.au',
    description='Python package for interacting with Yeelight Sunflower bulbs'
)
