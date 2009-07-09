#!/usr/local/bin/python3.1
#TODO Add resume
import urllib.request, urllib.error, re, os, shutil, time
from html.parser import HTMLParser
from string import Template                      

URL = "http://url.to/some_directory/"
DEST = "directory/to/save/to/on/your/computer"
MINUTES_TO_DOWNLOAD_FILE = 30
skip_links = 5
server_files = set()

class MyHTMLParser(HTMLParser):
	def handle_starttag(self, tag, attrs):
		global skip_links
		if tag == 'a':
			if skip_links == 0:
				filename = re.compile('%20').sub(' ', attrs[0][1])
				filename = re.compile("\\\\").sub('', filename)
				#filename = filename + ".mp4"
				server_files.add(filename)
			else:
				skip_links = skip_links - 1
				print("Skipping over link: ", attrs[0][1])

#get list of files from server
f = urllib.request.urlopen(URL)
p = MyHTMLParser()
p.feed(repr(f.readall()))

files_to_download = server_files - set(os.listdir(DEST))

while len(files_to_download) != 0:
	hour = time.localtime().tm_hour
	minute = time.localtime().tm_min
	# time limits on when file downloads should occur.  In this case, 4-8am, 12-8pm, localtime.
	if not((hour >= 4 and hour <= 7) or (hour >= 12 and hour <= 19)):
		if (hour == 7 or hour == 19) and (minutes >= 60 - MINUTES_TO_DOWNLOAD_FILE):
			time.sleep(60)
			continue
	destination = download = files_to_download.pop()
	download = re.compile(' ').sub('%20', download)
	#download = re.compile('\'').sub('\\\\\'', download)
	#download = download[:-4]
	print("Downloading: ", URL + download)
	try:
		urllib.request.urlretrieve(URL + download, DEST + destination + ".download")
	except urllib.error.URLError as ex:
		print("Oops, can't download: ", destination)
		print("Error: ", ex.reason)
		break
	else:
		shutil.move(DEST + destination + ".download", DEST + destination)