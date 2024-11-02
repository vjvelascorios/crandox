<!-- readme2cli -->
<!-- # nottested -->

# CRAN Documentation Downloader
****
## Description
A Python tool that downloads and saves the complete CRAN (Comprehensive R Archive Network) documentation locally. This allows you to access R package documentation offline without requiring an internet connection.

## Features
- Downloads PDF documentation for all CRAN packages
- Parallel downloading using ThreadPool for better performance
- Automated weekly updates via GitHub Actions
- Caches downloaded packages to avoid duplicates
- Simple and easy to use

## Installation

1. Clone the repository:
```sh
git clone https://github.com/vjvelascorios/crandox.git
cd crandox
```

2. Install dependencies:
```sh
pip install -r requirements.txt
```

## Usage

CRANDOX provides a rich command-line interface with the following capabilities:

### Basic Operations

Download specific packages:
```sh
crandox --download ggplot2 dplyr tidyr
crandox -d ggplot2 dplyr tidyr  # Short form
```

The script will:

1. Create a dox folder if it doesn't exist
2. Download all available CRAN package documentation
3. Save PDFs in the dox folder

## Requirements
- `Python 3.x`
- `requests`
- `beautifulsoup4`
- `tqdm`
- `concurrent.futures`



## Automated Updates
This repository includes a GitHub Action that automatically downloads and updates the documentation every Saturday at midnight UTC. You can simply clone this repository to get the latest documentation.

## TODO
- [ ] Include complete ussage instructions and examples
- [ ] Convert to PyPI package
- [ ] Convert to a CRAN Package
