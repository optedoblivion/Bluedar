from distutils.core import setup, Extension
import sys

LINUX = sys.platform.startswith("linux")

def getpackagedir():
    if LINUX:
        return "src"
    else:
        raise Exception("Unsupported platform")

def getextensions():
    if LINUX:
        linux_ext = Extension("_pyrssi",
            define_macros=[('PYRSSI_DEBUG', '0')],	# set to '1' to print debug messges, now disabled...
            libraries=["bluetooth"], # C libraries
            sources=["src/pyrssi.c",
                     "src/pyrssi_wrap.c"],
            )
        return [linux_ext]
    return []

# install the main library
setup(name="pyrssi",
    version="0.0.1",
    author="Maxin B John",
    author_email="maxinbjohn@gmail.com",
    url="http://pysportslive.googlecode.com/svn/trunk/pyrssi/",
    description="RSSI module for Python in GNU/Linux",
    long_description="RSSI Module for Python.",
    license="MIT",
    packages=["pyrssi"],
    package_dir={"pyrssi":getpackagedir()},
    ext_modules=getextensions(),
    classifiers = [ "Development Status :: 1 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Networking",
        "Topic :: Communications",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Other OS" ]
    )
