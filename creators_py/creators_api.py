#!/usr/bin/python

"""
Creators GET API interface
Copyright (C) 2014 Creators.com
@author Brandon Telle <btelle@creators.com>
"""

import subprocess, shlex, re, urllib, os.path
try:
	import json
except ImportError:
	try:
		import simplejson as json
	except ImportError:
		raise ImportError("A JSON library is required to use Creators_API")

# User's API Key
api_key = ""

# API url
api_url = "http://get.creators.com/"

# Make an API request
# @param endpoint string API url
# @param parse_json bool if True, parse the result as JSOn and return the parsed object
# @throws ApiError if an error code is returned by the API
# @return parsed JSON object, or raw return string
def __api_request(endpoint, parse_json=True):
	if api_key == "":
		raise ApiError('API key must be set')
	
	cmd = 'curl --silent -L --header "X_API_KEY: '+api_key+'" '+api_url+endpoint
	ret = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE).stdout.read()
	
	# Check for HTTP error messages
	err = re.search('Error ([0-9]+): (.*)', ret)
	if err != None:
		raise ApiError(err.group(2), err.group(1))
	
	# Parse JSON if required
	if parse_json:
		try:
			ret = json.loads(ret)
		except:
			pass
		
	# Check for API-generated error messages, throw exception
	try:
		if type(ret) is dict and ret['error'] > 0:
			raise ApiError(ret['message'], ret['error'])
	
	except KeyError:
		pass
	
	return ret

# SYN the server
# @return string "ack"
def syn():
	return __api_request('api/etc/syn')
	
# Get a list of available features
# @param limit int number of results to return
# @return list of features
def get_features(limit=1000):
	return __api_request('api/features/get_list/json/NULL/'+str(limit)+'/0')

# Get details on a feature
# @param filecode string unique filecode for the feature
# @return dict feature info
def get_feature_details(filecode):
	return __api_request('api/features/details/json/'+str(filecode))
	
# Get a list of releases for a feature
# @param filecode string unique filecode for a feature
# @param offset int offset, default 0
# @param limit int limit, default 10
# @param start_date string start date: YYYY-MM-DD, default none
# @param end_date string end_date: YYYY-MM-DD, default none
# @return list of releases
def get_releases(filecode, offset=0, limit=10, start_date='', end_date=''):
	return __api_request('api/features/get_list/json/'+str(filecode)+"/"+str(limit)+"/"+str(offset)+"?start_date="+str(start_date)+"&end_date="+str(end_date))
	
# Download a file
# @param url string URL string provided in the files section of a release result
# @param destination string path to the location the file should be saved to
# @throws ApiError if destination is not a writable file location or url is unavailable
# @return bool True if file is downloaded successfully
def download_file(url, destination):
	if not os.path.isdir(destination):
		try:
			f = open(destination, 'w')
			
			contents = __api_request(url, parse_json=False)
			
			if contents[0] == '{': 					# Poor man's JSON check
				contents = json.loads(contents)
				try:
					if type(contents) is dict and contents['error'] > 0:
						raise ApiError(contents['message'], contents['error'])
				
				except:
					raise ApiError("Unexpected content type: JSON")
			
			f.write(contents)
			f.close()
			return True
		except IOError:
			raise ApiError("Destination is unavailable or unwriteable")
		except ApiError:
			raise
	else:
		raise ApiError("Destination is a directory")
	
# API Exception class
class ApiError(Exception):
	def __init__(self, value, errno=0):
		self.value = value
		self.errno = errno
		
	def __str__(self):
		val = ''
		if self.errno > 0:
			val += '[Errno '+str(self.errno)+'] '
		val += self.value
		return repr(val)