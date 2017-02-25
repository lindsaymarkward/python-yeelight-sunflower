import io
from distutils.core import setup
from yeelightsunflower import __version__, __author__, __license__, __title__


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md', 'CHANGELOG.md')

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    "Topic :: Software Development :: Libraries :: Python Modules",
    'License :: OSI Approved :: MIT License',
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6"
]
setup(
    name=__title__,
    version=__version__,
    license=__license__,
    author=__author__,
    packages=['yeelightsunflower'],
    classifiers=classifiers,
    url='https://github.com/lindsaymarkward/python-yeelight-sunflower',
    author_email='lindsay.ward@jcu.edu.au',
    maintainer='Lindsay Ward',
    maintainer_email='lindsay.ward@jcu.edu.au',
    description='Python package for interacting with Yeelight Sunflower bulbs',
    long_description=long_description
)
