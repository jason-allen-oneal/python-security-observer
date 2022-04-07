# python-security-observer
This program will submit a scan to Mozilla's HTTP Security Observatory and await the results.

__INSTALLATION__
`pip3 install -r requirements.txt`  

```
Usage: main.py [options]
example: python3 main.py -u www.example.com

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -v, --verbose         Show all output
  -u TARGET, --url=TARGET
                        Domain on which to perform tests. (REQUIRED)
  -o WRITE, --out=WRITE
                        File to which to write the program's output
```