import os

from setuptools import find_packages, setup

from userdefinedtables import VERSION


def long_desc(root_path):
    FILES = ["README.md"]
    for filename in FILES:
        filepath = os.path.realpath(os.path.join(root_path, filename))
        if os.path.isfile(filepath):
            with open(filepath, mode="r") as f:
                yield f.read()


HERE = os.path.abspath(os.path.dirname(__file__))
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
    packages=find_packages(exclude=["tests*"]),
    install_requires=["Django>=2.2", "Pillow", "django-bootstrap-v5"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
    ],
    zip_safe=False,
)
