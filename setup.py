# setup.py
from setuptools import setup, find_packages
# nottested
setup(
    name="crandox",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "tqdm>=4.66.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "crandox=crandox.cli:main",
        ],
    },
    author="Victor Velasco Ríos",
    author_email="your.email@example.com",
    description="A CLI tool to download CRAN documentation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vjvelascorios/crandox",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)