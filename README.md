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

If using in conjunction with Lair (https://github.com/fishnetsecurity/Lair), there is a 
Lair script available (https://github.com/fishnetsecurity/Lair-Browser-Scripts/blob/
master/generate_webdisco_target_list.js) to export all IPs and and vhosts into 
appropriately formatted target list. 
```


## Usage
```
usage: webDisco.py [-h] --targets TARGETS [--wkhtmltoimage WKHTMLTOIMAGE]
                   [--agent AGENT] [--topurls] [--maxprocesses MAXPROCESSES]
                   [--timeout TIMEOUT] [--output OUTPUT] [--proxy PROXY]
                   [--debug] [--version]

Yet another web discovery tool

optional arguments:
  -h, --help            show this help message and exit
  --targets TARGETS     file containing list of targets
                        (http|https,ip,port,hostname)
  --wkhtmltoimage WKHTMLTOIMAGE
                        full path to wkhtmltoimage binary (Default:
                        wkhtmltoimage)
  --agent AGENT         User agent
  --topurls             check for existance of common administrative
                        interfaces
  --maxprocesses MAXPROCESSES
                        maximum number of processes (Default: number of cores)
  --timeout TIMEOUT     javascript timeout <sec> (Default: 3)
  --output OUTPUT       output directory
  --proxy PROXY         proxy Host:Port (ex. 127.0.0.1:8080)
  --debug               increase verbosity
  --version             show program's version number and exit
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
Current: v0.1
Project code under active development
```

## Contact
```
Authors: Joey Belans -- joeybelans[t.a]gmail[t.o.d]com
         Ryan Dorey -- ryandorey[t.a]gmail[t.o.d]com
```
