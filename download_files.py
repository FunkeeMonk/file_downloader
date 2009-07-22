#!/usr/local/bin/python3.1
#TODO Add support for resumption of broken downloads
import urllib.request, urllib.error, re, os, shutil, time
from html.parser import HTMLParser
from string import Template

URL = "http://url.to/some_directory/"
DEST = "/full/path/to/directory/to/save/to/on/your/computer/"

download_schedule = [(300, 630), (1430, 1630)] # Specify in a list, tuples indicating the start and end times for downloading in 24-hour format.  E.g., 300 for 3 a.m., 1630 for 4:30 p.m.
skip_links = 5 # Number of "header" links to skip
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

if not URL.endswith('/'):
	URL = URL + '/'

if not DEST.endswith('/'):
	DEST = DEST + '/'

#get list of files from server
f = urllib.request.urlopen(URL)
p = MyHTMLParser()
p.feed(repr(f.readall()))

files_to_download = server_files - set(os.listdir(DEST))

def modify_24h_time(time, minutes_to_decrement):
	time = time - ((minutes_to_decrement // 60) * 100)
	minutes_to_decrement = minutes_to_decrement - (minutes_to_decrement // 60)
	minutes = time % 100
	if minutes > minutes_to_decrement:
		time = time - minutes_to_decrement
	else:
		minutes_left = minutes_to_decrement - minutes
		time = time - minutes
		time = time - 100
		time = time + (60 - minutes_left)
	return time

average_time_to_download_file = 0

while len(files_to_download) != 0:
	current_time = time.localtime().tm_hour * 100 + time.localtime().tm_min

	for s in download_schedule:
		if current_time >= modify_24h_time(s[0], average_time_to_download_file) and current_time < modify_24h_time(s[1], average_time_to_download_file):
			break
	else:
		time.sleep(60)
		continue

	destination = download = files_to_download.pop()
	download = re.compile(' ').sub('%20', download)
	#download = re.compile('\'').sub('\\\\\'', download)
	#download = download[:-4]
	print("Downloading: ", URL + download)
	start_time = time.time()
	try:
		urllib.request.urlretrieve(URL + download, DEST + destination + ".download")
	except urllib.error.URLError as ex:
		print("Oops, can't download: ", destination)
		print("Error: ", ex.reason)
		break
	else:
		end_time = time.time()
		shutil.move(DEST + destination + ".download", DEST + destination)
		print("Download of ", destination, " complete.")

	if average_time_to_download_file == 0:
		average_time_to_download_file = (end_time - start_time) // 60
	else:
		average_time_to_download_file = (average_time_to_download_file + ((end_time - start_time) // 60)) // 2

	if average_time_to_download_file > 60:
		average_time_to_download_file = 60
