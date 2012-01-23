#!/usr/bin/env python

import redis
import zmq
import json
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--verbose', dest='verbose', action='store_true', help='Turn on verbose mode')
args = parser.parse_args()

try:
	r = redis.Redis("localhost")
	r.get('connected')
except:
	print "Not connected to the redis server."
	sys.exit(1)

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind("tcp://*:9999")
while True:
	if args.verbose:
		print "Waiting for a job result"
	message = socket.recv()
	if args.verbose:
		print 'Got job result: ' + message
	data = json.loads(message)
	job_id = data['id']
	host = data['host']
	key = 'job_result:' + str(job_id) + ':' + host
	if args.verbose:
		print 'Storing key ' + key + ' ==> ' + message
	r.set(key, message)
	if args.verbose:
		print 'Appending "' + host + '" to "job_done:' + str(job_id) + '"'
	key = 'job_done:' + str(job_id)
	r.rpush(key, host)
