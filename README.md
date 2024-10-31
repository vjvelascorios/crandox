# crandox

## Description
I don't like being connected everytime to internet to access the CRAN documentation. So I wrote a script to download the entire documentation from the CRAN website and save it to a folder named 'dox'.


## Code

Folder structure is simple, you only need to run the script `dlcran.py` and it will download the documentation for all the packages in CRAN. Also, I set up a workflow to get entire pdf's from the CRAN website (not tested), so, maybe you only need to clone the repo.

```python

### Requirements

- `requests`
- `beautifulsoup4`
- `concurrent.futures`
```


Enjoy.