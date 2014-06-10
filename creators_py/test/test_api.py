import unittest, sys, os, hashlib
from creators_py import creators_api

# This is a demo user key. These tests are written specifically 
# for this user. They will fail if the API key is changed.
creators_api.api_key = 'B8C31227882C3C10D954BD11A67DF138125C895B'

class TestAPI(unittest.TestCase):
	
	def setUp(self):
		pass
		
	def test_auth(self):
		tmp_key = creators_api.api_key
		creators_api.api_key = 'thisisnotanapikey'
		self.assertRaises(creators_api.ApiError, creators_api.syn) #401
		
		creators_api.api_key = tmp_key
		self.assert_(creators_api.syn() == 'ack')
	
	def test_features(self):
		features = creators_api.get_features()
		
		self.assert_(type(features) is list)
		self.assert_(len(features) == 4)
	
	def test_feature_details(self):
		self.assertRaises(TypeError, creators_api.get_feature_details) # TypeError: argument required
		self.assertRaises(creators_api.ApiError, creators_api.get_feature_details, 'zzzz') 	# 404
		self.assertRaises(creators_api.ApiError, creators_api.get_feature_details, 'wiz')   # 403
		
		feature = creators_api.get_feature_details('bc')
		self.assert_(type(feature) is dict)
		
		for i in ['file_code', 'title', 'category', 'type']:
			self.assert_(type(feature[i]) is str)
			
		self.assert_(type(feature['authors']) is list)
		self.assert_(len(feature['authors']) == 2)
		
	def test_releases(self):
		self.assertRaises(TypeError, creators_api.get_releases) # TypeError: argument required
		self.assertRaises(creators_api.ApiError, creators_api.get_releases, 'zzzz') # 404
		self.assertRaises(creators_api.ApiError, creators_api.get_releases, 'wiz')  # 403
		
		releases = creators_api.get_releases('tma', limit=1)
		self.assert_(type(releases) is list)
		self.assert_(len(releases) == 1)
		self.assert_(type(releases[0]) is dict)
		
		for i in ['id', 'title', 'file_code', 'release_date']:
			self.assert_(releases[0][i] != None)
			
		self.assert_(type(releases[0]['files']) is list)
		self.assert_(type(releases[0]['notes']) is list)
		self.assert_(len(releases[0]['files']) > 0)
		
	def test_files(self):
		dest = "test_api_file"
		self.assertRaises(TypeError, creators_api.download_file) # TypeError: argument required
		self.assertRaises(TypeError, creators_api.download_file, '/api/files/download/-1') # TypeError
		self.assertRaises(creators_api.ApiError, creators_api.download_file, '/api/files/download/-1', dest) # 404
		
		file = creators_api.get_releases('mrz', limit=1)[0]['files'][0]
		
		self.assert_(creators_api.download_file(file['url'], dest))
		
		f = open(dest, 'rb')
		hash = hashlib.sha1(f.read()).hexdigest()
		f.close()
		
		self.assert_(hash == file['sha1'])
		os.remove(dest)
		return
			
if __name__ == '__main__':
    unittest.main()