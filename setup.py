import os
import re

from setuptools import find_packages, setup

HERE = os.path.abspath(os.path.dirname(__file__))


def read_version():
    """Read the version from the package without importing it (the build env does not have it on sys.path)."""
    init_path = os.path.join(HERE, "userdefinedtables", "__init__.py")
    with open(init_path, mode="r") as f:
        match = re.search(r'^__version__ = "([^"]+)"', f.read(), re.M)
    if not match:
        raise RuntimeError("Unable to find __version__ in userdefinedtables/__init__.py")
    return match.group(1)


VERSION = read_version()


def long_desc(root_path):
    FILES = ["README.md"]
    for filename in FILES:
        filepath = os.path.realpath(os.path.join(root_path, filename))
        if os.path.isfile(filepath):
            with open(filepath, mode="r") as f:
                yield f.read()


long_description = "\n\n".join(long_desc(HERE))


setup(
    name="django_userdefinedtables",
    version=VERSION,
    setup_requires=["setuptools_scm"],
    license="MIT",
    description="Generic EAV-style table creation in the user's hands",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Peter Wood",
    author_email="peterelmwood@gmail.com",
    maintainer="Peter Wood",
    url="https://github.com/peterelmwood/django_userdefinedtables",
    project_urls={
        "Bug Tracker": "https://github.com/peterelmwood/django_userdefinedtables/issues",
        "Documentation": "https://github.com/peterelmwood/django_userdefinedtables#readme",
        "Source Code": "https://github.com/peterelmwood/django_userdefinedtables",
        "Changelog": "https://github.com/peterelmwood/django_userdefinedtables/blob/main/CHANGELOG.md",
    },
    packages=find_packages(exclude=["tests*"]),
    install_requires=["Django>=3.2", "Pillow"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
    ],
    zip_safe=False,
)
