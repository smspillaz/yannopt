"""Installation and setup script for yannopt."""

from setuptools import find_packages
from setuptools import setup

setup(name="yannopt",
      version="0.0.1f",
      description="Yet Another Optimization Library",
      long_description="A hand implemented neural net",
      author="",
      author_email="",
      url="http://github.com/duckworthd/yannopt",
      classifiers=["Development Status :: 3 - Alpha",
                   "Programming Language :: Python :: 2",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3",
                   "Programming Language :: Python :: 3.1",
                   "Programming Language :: Python :: 3.2",
                   "Programming Language :: Python :: 3.3",
                   "Programming Language :: Python :: 3.4",
                   "Intended Audience :: Developers",
                   "Topic :: Software Development :: Build Tools",
                   "License :: OSI Approved :: MIT License"],
      license="MIT",
      keywords="machine-learning",
      packages=find_packages(exclude=["yannopt.tests"]),
      zip_safe=True,
      include_package_data=True)
