# webDisco

## Objective
```
Web discovery tool to capture screenshots from a list of hosts & vhosts. 
Requests are made via IP address and vhosts to determine differences.
Additionallty checks for common administrative interfaces and web server 
misconfigurations. 

webDisco outputs two (2) HTML files:
- File data.html displays sortable host and connection information with links to screenshots. 
- File screenshots.html displays thumbnails of all screenshots. 
All screenshots can be clicked through/viewed through a shadowbox viewer for quick viewing. 
```


## Usage
```
$ ./webDisco.py -h
usage: webdisco.py [-h] --targets TARGETS [--wkhtmltoimage WKHTMLTOIMAGE]
                   [--agent AGENT] [--topurls] [--maxprocesses MAXPROCESSES]
                   [--timeout TIMEOUT] [--output OUTPUT] [--proxy PROXY]
                   [--debug]

Yet another web discovery tool

optional arguments:
  -h, --help            show this help message and exit
  --targets TARGETS     File containing list of targets
                        (http|https,ip,port,hostname)
  --wkhtmltoimage WKHTMLTOIMAGE
                        Full path to wkhtmltoimage binary (Default:
                        wkhtmltoimage)
  --agent AGENT         User agent
  --topurls             Check for existance of common administrative
                        interfaces
  --maxprocesses MAXPROCESSES
                        Maximum number of processes (Default: number of cores)
  --timeout TIMEOUT     Javascript timeout <sec> (Default: 3)
  --output OUTPUT       Output directory
  --proxy PROXY         Proxy Host:Port (ex. 127.0.0.1:8080)
  --debug               Increase verbosity in a single threaded fashion
```

## Installation
```
Installation
---------------------------------------------------
webDisco was tested on Ubuntu 14.04, Kali 1.0.9 and OS X Mavericks
Requires wkhtmltoimage, which is part of the wkhtmltopdf package (http://wkhtmltopdf.org/)
----------- OSX -----------------------------------
OSX Deps: pip install -U -r requirements.txt
----------- Linux ---------------------------------
Linux: sudo apt-get install python-pip
Linux Deps: pip install -U -r requirements.txt
```

## Developing
```
Project code under active development
```

## Contact
```
Authors: Joey Belans -- joeybelans[t.a]gmail[t.o.d]com
         Ryan Dorey -- ryandorey[t.a]gmail[t.o.d]com
```
