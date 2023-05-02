# Adobe Fonts Revealer

Install Adobe fonts that are synced to your computer as a standard font file that can be used anywhere.

## Usage
The `fonttools` package needs to be installed first. Download it with pip:
```shell
python -m pip install fonttools
```
Then run the script, filing the required positional argument:
```shell
python main.py [-h] {copy,install}

positional arguments:
  {copy,install}

options:
  -h, --help      show this help message and exit
```

 - `copy` will only copy the .OTF font files to the current folder.
 - `install` will install the fonts **for all users.**
