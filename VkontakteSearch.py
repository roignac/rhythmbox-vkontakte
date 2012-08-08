# - encoding: utf8 - 
#
# Copyright © 2010 Alexey Grunichev
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import rb
import urllib2
import hashlib
import codecs

from xml.dom import minidom
from gi.repository import RB
from html_decode import decode_htmlentities

from VkontakteResult import VkontakteResult

APP_ID = 1850196
SECRET_KEY = 'nk0n6I6vjQ'
USER_ID = 76347967

def utf8ise(s):
	return codecs.utf_8_encode(s)[0]

class VkontakteSearch:
	def __init__(self, search_term, db, entry_type):
		print "search_term ='%s'" % search_term
		self.search_term = search_term
		self.db = db
		self.entry_type = entry_type
		self.search_complete = False
		self.entries_hashes = []
		self.query_model = RB.RhythmDBQueryModel.new_empty(db)

	def make_sig(self, method, query):
		str = "%sapi_id=%scount=300method=%sq=%stest_mode=1v=2.0%s" % (USER_ID, APP_ID, method, query, SECRET_KEY)
		return hashlib.md5(str).hexdigest()
		
	def is_complete(self):
		print "complete = %s" % self.search_complete
		return self.search_complete
	
	def add_entry(self, result):
		entry = self.db.entry_lookup_by_location(result.url)
		# add only distinct songs (unique by title+artist+duration) to prevent duplicates
		hash = ('%s%s%s' % (result.title, result.artist, result.duration)).lower()
		if hash in self.entries_hashes:
			return
		self.entries_hashes.append(hash)
		if entry is None:
			entry = RB.RhythmDBEntry.new(self.db, self.entry_type, result.url)
			if result.title:
				self.db.entry_set(entry, RB.RhythmDBPropType.TITLE, utf8ise(decode_htmlentities(result.title)))
			if result.duration:
				self.db.entry_set(entry, RB.RhythmDBPropType.DURATION, result.duration)
			if result.artist:
				self.db.entry_set(entry, RB.RhythmDBPropType.ARTIST, utf8ise(decode_htmlentities(result.artist)))
		self.query_model.add_entry(entry, -1)
		self.db.commit()

	def on_search_results_recieved(self, data):
		# vkontakte sometimes returns invalid XML with empty first line
		print "got data\n" + str(data)
		data = data.lstrip()
		# remove invalid symbol that occured in titles/artist
		#data = data.replace(u'\uffff', '')
		xmldoc = minidom.parseString(data)
		audios = xmldoc.getElementsByTagName("audio")
		for audio in audios:
			self.add_entry(VkontakteResult(audio))
		self.search_complete = True

	# Starts searching
	def start(self):
		print "start"
		sig = self.make_sig('audio.search', self.search_term)
		path = "http://api.vk.com/api.php?api_id=%s&count=300&v=2.0&method=audio.search&sig=%s&test_mode=1&q=%s" % (APP_ID, sig, urllib2.quote(self.search_term))
		print "path='%s'" % path
		loader = rb.Loader()
		loader.get_url(path, self.on_search_results_recieved)
