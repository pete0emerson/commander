#!/usr/bin/env python

import redis
import json
import zmq
import pprint
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--verbose', dest='verbose', action='store_true', help='Turn on verbose mode')
args = parser.parse_args()

r = redis.Redis("localhost")

while True:
	if args.verbose:
		print 'Waiting for something in the job_queue'
	(queue, job_id) = r.blpop('job_queue')
	if args.verbose:
		print 'Got job_id ' + str(job_id) + ' off the job_queue'
	key = 'job:' + str(job_id)
	if args.verbose:
	 	print "Getting the job from key '" + key + "'"
	job = r.get(key)
	data = json.loads(job)
	for host in data['hosts']:
		hostdata = {}
		hostdata['id'] = data['id']
		if 'command' in data:
			hostdata['command'] = data['command']
		if 'code' in data:
			hostdata['code'] = data['code']
		hostdata['receiver'] = data['receiver']
		hostdata['host'] = host
		text = json.dumps(hostdata)
		if args.verbose:
			print 'Sending to ' + host + ': ' + text

		context = zmq.Context()
		socket = context.socket(zmq.PUSH)
		socket.connect("tcp://" + host + ":8888")
		socket.send(text)
		socket.close()
