#! /usr/bin/env python
# Coding: utf-8
# Project Name: webDisco
# Purpose: Web application discovery and screenshot tool
# Authors: Joey Belans -- joeybelans[t.a]gmail[t.o.d]com
#          Ryan Dorey -- ryandorey[t.a]gmail[t.o.d]com
#
#
# Installation
# ---------------------------------------------------
# webDisco was tested on Ubuntu 12.04 and OSX Mavericks
# ----------- OSX -----------------------------------
# OSX Deps: pip install -U -r requirements.txt
# ----------- Linux ---------------------------------
# Linux: sudo apt-get install python-pip
# Linux Deps: pip install -U -r requirements.txt


import multiprocessing
import argparse
import sys
import os
import re
import requests
from bs4 import BeautifulSoup

# Verify program is executable
def is_exe(program):
   def _is_exe(fpath):
      return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

   fpath, fname = os.path.split(program)
   if fpath:
      if _is_exe(program):
         return True
   else:
      for path in os.environ["PATH"].split(os.pathsep):
         path = path.strip('"')
         exe_file = os.path.join(path, program)
         if _is_exe(exe_file):
            return True

   return False


# Makes HTTP GET requests 
def httpGET(proxyurl, agent, protocol, ip, port, path, hostname, timeout):
   # Configure proxy, if necessary
   proxies = {}
   if proxyurl != None:
      proxies['http'] = 'http://' + proxyurl
      proxies['https'] = 'https://' + proxyurl 

   # Create request headers
   headers = {'User-Agent': agent}
   if hostname != '':
      if ip != '':
         headers['Host'] = hostname
      else:
         ip = hostname

   # Get port, if necessary
   if port == None:
      if protocol == 'http':
         port = '80'
      else:
         port = '443'

   # Request URL
   import requests.packages.urllib3 as urllib3
   urllib3.disable_warnings()
   try: 
      if len(proxies) == 0:
         r = requests.get(protocol + "://" + ip + ":" + port + path, headers=headers, timeout=timeout, verify=False, allow_redirects=False)
      else:
         r = requests.get(protocol + "://" + ip + ":" + port + path, headers=headers, proxies=proxies, timeout=timeout, verify=False)
   except:
      return {
         'status': 0,
         'server': '',
         'title': 'Unable to connect',
         'content': '', 
         'auth': '',
         'redirectURL': ''
         }

   # Create dictionary
   output = {
	      'status': r.status_code,
         'server': '',
         'title': '',
         'content': '', 
         'auth': '',
         'redirectURL': ''
   }
   if 'server' in r.headers:
      output['server'] = r.headers['server']
   if 'www-authenticate' in r.headers:
      output['auth'] = r.headers['www-authenticate']
   if 'location' in r.headers:
      output['redirectURL'] = r.headers['location']
   if 'content-location' in r.headers:
      output['redirectURL'] = r.headers['content-location']
   if r.text:
      output['content'] = r.text[:500].decode("ascii", "ignore")
      soup = BeautifulSoup(r.text)
      try:
         output['title'] = soup.find_all('title').contents[0].decode("ascii", "ignore")
      except:
         pass
      if soup.find_all('input', {'type':'password'}):
         output['auth'] = 'Form based auth'

   # Return output
   return output

# Checks for top interesting URLs
def requestTopURLs(proxyurl, agent, protocol, ip, port, hostname, timeout):
   # List of URLs to be checked
   topURLs = [
   "/CFIDE/", 
   "/doesnotexist.aspx",
   "/admin/",
   "/admin-console/",
   "/manager/",
   "/robots.txt",
   "/crossdomain.xml"
   "/.svn/",
   ".htaccess",
   "/FCKeditor/",
   "/axis2/",
   "/axis2-admin/",
   "/axis/",
   "/axis-admin/",
   "/phpmyadmin/"
   ]

   # Initialize dictionary
   output = {}

   # Loop through each URL and record output
   for path in topURLs:
      tempOut = httpGET(proxyurl, agent, protocol, ip, port, path, hostname, timeout)
      if (tempOut['status'] == 403 or (not (tempOut['status'] >= 400 and tempOut['status'] < 500)))  and tempOut['status'] != 0:
         output[path] = tempOut

   # Return the dictionary
   return output


def createScreenshot(wkhtmltoimage, proxyurl, outdir, protocol, ip, port, path, hostname):
   name = ip + '.' + port
   if hostname != '':
      name = name + '-' + hostname
   name = name + '.png'

   # Create screenshot
   cmd = wkhtmltoimage + ' --quiet'
   if proxyurl != None:
      cmd = cmd + ' --proxy ' + proxyurl
   if hostname != '':
      cmd = cmd + " --custom-header Host '" + hostname + "' --custom-header-propagation"
   cmd = cmd + " --quality 10 --width 800 --height 400 '" + protocol + '://' + ip + ':' + port + path + "' " + outdir + '/images/' + name + ' > /dev/null 2>&1'
   rtn = os.system(cmd)

   # Return the name of the image
   return name

def processTarget(params):
   # Split the parameter tuple
   target, args = params

   # Parse the target line
   protocol, ip, port, hostname = target.split(',')

   # Initialize disco dictionary
   disco = {
   'target' : {
	'protocol': protocol,
	'ip': ip,
	'port': port,
	'hostname': hostname
	 }
   }

   # Make initial request
   if args.debug:
      print "Initial target: " + target

   path = '/'
   disco['init'] = httpGET(args.proxy, args.agent, protocol, ip, port, path, hostname, args.timeout)
   if disco['init']['status'] == 0:
      if args.debug:
         print "Target failed: " + target
      disco['screenshot'] = ''
      disco['topURLs'] = {}
      return disco

   # Create screenshot image name
   if args.debug:
      print "Create screenshot: " + target

   disco['screenshot'] = createScreenshot(
	args.wkhtmltoimage,
	args.proxy,
	args.output,
	disco['target']['protocol'],
	disco['target']['ip'],
	disco['target']['port'],
	path,
	disco['target']['hostname']
   )

   # Get top URLs
   if args.topurls:
      if args.debug:
         print "Get top urls: " + target
      disco["topURLs"] = requestTopURLs(args.proxy, args.agent, protocol, ip, port, hostname, args.timeout)
   else:
      disco["topURLs"] = {}

   # Status out
   if hostname == '':
      targetURL = "%s://%s:%s/" % (protocol, ip, port)
   else:
      targetURL = "%s://%s[%s]:%s/" % (protocol, hostname, ip, port)
   print "Completed target: " + targetURL

   # Return discovery info
   return disco

# Generate the final report
def generateReport(results, outDir, debug):
   fd = open(outDir + '/data.html','w')
   print >> fd, '''
   <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
   <head>
      <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
      <title>webDisco Results</title>
      <script src="deps/js/jquery-1.11.0.min.js"></script>
      <script src="deps/js/lightbox.min.js"></script>
      <link href="deps/css/lightbox.css" rel="stylesheet" />
      <link rel="stylesheet" href="deps/css/style.css" type="text/css" id="" media="print, projection, screen" />
      <script type="text/javascript" src="deps/js/jquery-latest.js"></script>
      <script type="text/javascript" src="deps/js/jquery.tablesorter.js"></script>
      <script type="text/javascript">
      $(function() {
         $("table").tablesorter({debug: true});
      });
      </script>
   </head>
   <body>
   <center><b>Welcome to webDisco</b> 
   <br><img src=deps/img/disco.gif style="width:100px;height:100px"></center>
   <table id="rowspan" cellspacing="0" class="tablesorter">
   <thead>
         <tr>
         <th colspan="1">Protocol</th>
         <th colspan="1">IP</th>
         <th colspan="1">Hostname</th>
         <th colspan="1">Port</th>
         <th colspan="1">Path</th>
         <th colspan="1">Returned Status</th>
         <th colspan="1">Page Title</th>
         <th colspan="1">Server Banner</th>
         <th colspan="1">Authentication</th>
         <th colspan="1">Redirect</th>
         <th colspan="1">Screenshot</th>
         </tr>
   </thead>
   <tbody>
   '''
   os.system("cp -r " + sys.path[0] + "/deps " + outDir)
   for result in results:
      if len(result) == 0:
         continue

      if debug:
         print "Add result: " + result['target']['ip']
	 
      # Display initial request 
      init = result['init']
      target = result['target']
      if target['hostname'] == '':
         targetURL = "%s://%s:%s/" % (target['protocol'], target['ip'], target['port'])
      else:
         targetURL = "%s://%s[%s]:%s/" % (target['protocol'], target['hostname'], target['ip'], target['port'])

      print >> fd, """
      <tr>
         <td>%s</td>
         <td>%s</td>
         <td>%s</td>
         <td>%s</td>
         <td>/</td>
         <td>%d</td>
         <td>%s</td>
         <td>%s</td>
         <td>%s</td>
         <td>%s</td>
         <td>
         """ % (target['protocol'], target['ip'], target['hostname'], target['port'], init['status'], init['title'], init['server'], init['auth'], init['redirectURL'],)

      if init['status'] != 0 and os.path.isfile(outDir + "/images/" + result['screenshot']):
         print >> fd, '<a href = "images/%s" data-lightbox="screenies" data-title="%s">Screenshot</a>' % (result['screenshot'], targetURL)
      print >> fd, '</td> </tr>'

      # Display top urls
      topURLs = result['topURLs']
      for path in topURLs:
         print >> fd, """
         <tr>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%d</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td></td>
         </tr>
         """ % (target['protocol'], target['ip'], target['hostname'], target['port'], path, topURLs[path]['status'], topURLs[path]['title'], topURLs[path]['server'], topURLs[path]['auth'], topURLs[path]['redirectURL'])
   print >> fd, """
         </tbody>
      </table>
   </body>
</html>
"""

def generateScreenies(results, outDir, debug):
   # Create screenshots.html output
   fd = open(outDir + '/screenshots.html','w')
   print >> fd, '''
   <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
      <title>webDisco Screenshots</title>
      <script src="deps/js/jquery-1.11.0.min.js"></script>
      <script src="deps/js/lightbox.min.js"></script>
      <link href="deps/css/lightbox.css" rel="stylesheet" />
      <link rel="stylesheet" href="deps/css/style.css" type="text/css" id="" media="print, projection, screen" />
<html>
   <body>
   <table id="rowspan" cellspacing="0">
   '''

   count = 0
   for result in results:         
      if len(result) == 0:
         continue

      if debug:
         print "Add result: " + result['target']['ip']

      # Display initial target
      target = result['target']
      if target['hostname'] == '':
         targetURL = "%s://%s:%s/" % (target['protocol'], target['ip'], target['port'])
      else:
         targetURL = "%s://%s[%s]:%s/" % (target['protocol'], target['hostname'], target['ip'], target['port'])
   
      if result['screenshot'] == '':
         continue

      if count == 0:
         print >> fd, "<tr>"

      print >> fd, "<td>"
      if result['init']['status'] != 0 and os.path.isfile(outDir + "/images/" + result['screenshot']):
         print >> fd, "<a href = \"images/%s\" data-lightbox=\"screenies\" data-title=\"%s\"><img height=\"75%%\" width=\"75%%\" src=\"images/%s\" border=1></img></a><br>%s" % (result['screenshot'], targetURL, result['screenshot'], targetURL)
      print >> fd, "</td>"
      count+=1

      if count == 3:
         print >> fd, "</tr>"
         count = 0

   while count < 3:
      print >> fd, "<td></td>"
      count+=1

   if count == 3:
      print >> fd, "</tr>"

   print >> fd, '''
   </table>
   </body>
   </html>'''

   fd.close()

def main():
   # Get the command line arguments
   parser = argparse.ArgumentParser(description='Yet another web discovery tool')
   parser.add_argument('--targets', required=True, dest='targets', help='File containing list of targets (http|https,ip,port,hostname)')
   parser.add_argument('--wkhtmltoimage', dest='wkhtmltoimage', default='wkhtmltoimage', help='Full path to wkhtmltoimage binary (Default: wkhtmltoimage)')
   parser.add_argument('--agent', dest='agent', default='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17', help='User agent')
   parser.add_argument('--topurls', dest='topurls', default=False, action='store_true', help='Check for existance of common administrative interfaces')
   parser.add_argument('--maxprocesses', dest='maxprocesses', default=multiprocessing.cpu_count(), help='Maximum number of processes (Default: number of cores)')
   parser.add_argument('--timeout', dest='timeout', default=3, help='Javascript timeout <sec> (Default: 3)')
   parser.add_argument('--output', dest='output', default='webDisco', help='Output directory')
   parser.add_argument('--proxy', dest='proxy', help='Proxy Host:Port (ex. 127.0.0.1:8080)')
   parser.add_argument('--debug', dest='debug', default=False, action='store_true', help='Increase verbosity')
   args = parser.parse_args()
   
   # Validate existance of "deps" directory
   if not os.path.isdir(sys.path[0] + '/deps'):
      print sys.path[0] + '/deps does not exist'
      sys.exit()

   # Validate wkhtml is available
   if not is_exe(args.wkhtmltoimage):
      print args.wkhtmltoimage + ' does not exist or is not executable'
      sys.exit()
   
   # Validate target file exists
   if not os.path.isfile(args.targets):
      print args.targets + ' does not exist'
      sys.exit()

   # Get list of targets
   f = open(args.targets, 'r')
   targets = []
   for line in f.readlines():
      targets.append((line.strip(), args))
   f.close()

   # Create output directory
   if not os.path.exists(args.output):
      os.makedirs(args.output)
      os.makedirs(args.output + '/images')

   # Process each target
   pool = multiprocessing.Pool(args.maxprocesses)
   results = []
   r = pool.map_async(processTarget, targets, callback=results.append)

   # Wait on the results
   r.wait()

   # Display results
   generateReport(results[0], args.output, args.debug)
   generateScreenies(results[0], args.output, args.debug)

if __name__ == '__main__':
   main()