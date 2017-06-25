#!/usr/bin/env python3
import json
import re
import os
import nltk
import logging
from gensim.models import word2vec
from datetime import datetime
from sys import version as python_version
from cgi import parse_header, parse_multipart

if python_version.startswith('3'):
	from urllib.parse import parse_qs
	from http.server import BaseHTTPRequestHandler, HTTPServer
    #from http.server import BaseHTTPRequestHandler
else:
	from urlparse import parse_qs
	from BaseHTTPServer import BaseHTTPRequestHandler
	import SocketServer

def save2txt(data, outfile):
	res = []
	try:
		#print(type(data))
		for item in data["value"]:
			#print(item["category"])
			_item = item["name"]
			_item = re.sub(u'<b>', u'', _item)
			_item = re.sub(u'</b>', u'', _item)
			_item = re.sub(u':', u'', _item)
			_item = re.sub(u'&#39;', u'', _item)
			_item = re.sub(u'&amp;', u'', _item)
			_item = re.sub(u',', u'', _item)
			_item = re.sub(u'\.', u'', _item)
			res.append(_item.encode('utf-8'))
		f = open(outfile, 'w')
		f.writelines(res)
		f.close()
	#except json.JSONDecodeError as e:
	except KeyError:
		print('JSONDecodeError')
		res = [""]

def find_keywords(fname, res_thresh=3, word=None):
	sentences = word2vec.LineSentence(fname)
	model = word2vec.Word2Vec(sentences,
	                          sg=1,
	                          size=100,
	                          min_count=1,
	                          window=10,
	                          hs=1,
	                          negative=0)
	#model.save("model.bin")
	results = []
	if word is not None:
		try:
			results = model.most_similar(positive=[word], topn=10)
		except KeyError:
			pass
	if len(results) == 0:
  		if python_version.startswith('3'):
			text = make_string_from_vocab3(model)
		else:
			text = make_string_from_vocab2(model)

		#blob = TextBlob(text)
		#nouns = blob.noun_phrases
		is_noun = lambda pos: pos[:2] == 'NN'
		# do the nlp stuff
		tokenized = nltk.word_tokenize(text)
		nouns = [word for (word, pos) in nltk.pos_tag(tokenized) if is_noun(pos)]
		#nouns = [word for word,pos in tags if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS')]
		#print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
		#print("nouns:")
		#print(nouns)
		#print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
		_dict = {}
  		if python_version.startswith('3'):
			_dict = create_vocab_dict3(model, nouns)
		else:
			_dict = create_vocab_dict2(model, nouns)

		# find similar words from the pool
		count = 0
		for k, v in sorted(_dict.items(), key=lambda x:x[1], reverse=True):
			if count < res_thresh:
				results.append(k)
				count+=1
			else:
				break
		#print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
		#print("results:")
		#print(results)
		#print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
	return results

def create_vocab_dict3(model, nouns):
	_dict = {}
	for word, obj in model.vocab.items():
		for noun in nouns:
			if word == noun:
				_dict[word.lower()] = obj.count
	return _dict

def make_string_from_vocab3(model):
	return (' '.join(model.vocab.keys()).lower())

def create_vocab_dict2(model, nouns):
	_dict = {}
	for word, obj in model.wv.vocab.items():
		for noun in nouns:
			if word == noun:
				_dict[word.lower()] = obj.count
	return _dict

def find_most_similar_word(model, word):
	maxsim = 0
	ret = ""
	for w, obj in model.wv.vocab.items():
		sim = model.similarity(word, w)
		if sim > maxsim:
			ret = w
			maxsim = sim
	return [ret]

def make_string_from_vocab2(model):
	return (' '.join(model.wv.vocab.keys()).lower())

def find_issue(word, fname):
#try:
	sentences = word2vec.LineSentence(fname)
	#print(sentences)
	model = word2vec.Word2Vec(sentences,
	                          sg=1,
	                          size=100,
	                          min_count=1,
	                          window=10,
	                          hs=1,
	                          negative=0)
	#model.save("model.bin")
	try:
		results = model.most_similar(positive=[word], topn=10)
	except KeyError:
		try:
			results = model.most_similar(positive=[word.capitalize()], topn=10)
		except KeyError:
			#results = find_most_similar_word(model, word)
			results = []
			pass

	# find similar words from the pool
	keys = []
	for result in results:
		if result[1] > 0.5 or len(keys) == 0:
			#print(result[0], '\t', result[1])
			keys.append(result[0])
	# pick up issues from the target pool
	lines = []
	with open(fname) as f:
		for line in f:
			for key in keys:
				#print line,
				if key in line:
					lines.append(line)
	return lines

# HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
	def do_OPTIONS(self):
		self.send_response(200, "ok")
		self.send_header('Access-Control-Allow-Origin', '*')
		self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
		self.send_header("Access-Control-Allow-Headers", "X-Requested-With")

	# GET
	def do_GET(self):
		# Send response status code
		self.send_response(200)

		# Send headers
		self.send_header('Content-type','text/html')
		self.end_headers()

		# Send message back to client
		#message = "Hello world!"
		# Write content as utf-8 data
		#self.wfile.write(bytes(message, "utf8"))
		return

	# POST
	def do_POST(self):
		# Send response status code
		self.send_response(200)
		# Send headers
		self.send_header('Content-type','text/html')
		self.end_headers()

		ctype, pdict = parse_header(self.headers['Content-Type'])
		if ctype == 'multipart/form-data':
		    text = "{}"
		elif ctype == 'application/x-www-form-urlencoded':
		    length = int(self.headers['content-length'])
		    text = self.rfile.read(length).decode('utf-8')
		else:
		    text = "{}"

		# convert to json
		try:
			obj = json.loads(text, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
			obj = json.loads(obj)
		except KeyError:
			obj = None

		# Send message back to client
		if obj is not None:
			keywords = run_keyword_engine(obj)
			if keywords:
				alg = choose_algorithm()
				issues = run_issue_engine(keywords)
			else:
				issues = []
				alg = "None"
		else:
			keywords = []
			issues = []
			alg = "None"
		save_for_backup(alg, keywords, issues)
		#message = "Hello world!"
		# Write content as utf-8 data
		#self.wfile.write(bytes(message).encode("utf8"))
		return

def run_keyword_engine(data):
	tmpfile ='/tmp/' + datetime.now().strftime('%s')
	save2txt(data, tmpfile)
	keywords = find_keywords(tmpfile)
	#print(keywords)
	return keywords

def save_for_backup(alg, keywords, issues):
	_dict = {"algorithm": alg, "keyword": keywords, "issue": issues}
	f = open('data/sample.json', 'w')
	json.dump(_dict, f)
	f.close()

def choose_algorithm():
	return "word2vec (gensim)" # TODO extend for other algorithms

def run_issue_engine(keywords):
	dirname = "data/issues/"
	issues = []
	for fname in os.listdir(dirname):
		for word in keywords:
			ret = find_issue(word, dirname+fname)
			issues.extend(ret)
	return issues

def run():
  print('starting server...')

  #logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
  # Server settings
  # Choose port 8080, for port 80, which is normally used for a http server, you need root access
  server_address = ('127.0.0.1', 8010)
  if python_version.startswith('3'):
	httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
  else:
	SocketServer.TCPServer.allow_reuse_address = True
	httpd = SocketServer.TCPServer(server_address, testHTTPServer_RequestHandler)
  print('running server...')
  httpd.serve_forever()


run()
