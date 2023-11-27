from os import path
import setuptools

# Collect additional information from separate files
dir = path.abspath(path.dirname(__file__))
with open(path.join(dir, "requirements.txt"), encoding="utf-8") as fp:
    install_requires = fp.read()
with open(path.join(dir, "version.txt"), encoding="utf-8") as fp:
    version = fp.readline().strip()
with open(path.join(dir, "README.md"), encoding="utf-8") as fp:
    readme = fp.read()

# Actual setup
setuptools.setup(
    name="nextmv",
    description="Nextmv's Python library for solving decision problems",
    long_description=readme,
    long_description_content_type="text/markdown",
    version=version,
    author="Nextmv inc.",
    author_email="support@nextmv.io",
    url="https://github.com/nextmv/sdk-python",
    packages=["nextmv"],
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
