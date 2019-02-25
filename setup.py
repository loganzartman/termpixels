import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="termpixels",
    version="0.0.2",
    author="Logan",
    author_email="logan.zartman@utexas.edu",
    description="Terminal I/O with a pixel-like abstraction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/loganzartman/termpixels",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
