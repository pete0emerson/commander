#!/usr/bin/env python

import redis
import json
import sys
import argparse
import os

parser = argparse.ArgumentParser(description='Execute a command asynchronously on multiple hosts')
parser.add_argument('--host', dest='host', action='append', required=True, help='The target host(s) (multiple --host flags may be specified)')
parser.add_argument('--receiver', dest='receiver', required=True, help='The receiver to send results to')
parser.add_argument('--verbose', dest='verbose', action='store_true', help='Turn on verbose mode')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--command', dest='command', help='The command to be run')
group.add_argument('--code', dest='code', help='File to be injected and run')
args = parser.parse_args()

r = redis.Redis("localhost")

def createJob(r, hosts, command, code, receiver):
	job_id = r.incr('job_id')

	data = {}
	data['id'] = job_id
	data['hosts'] = hosts
	if command is not None:
		data['command'] = command
	if code is not None:
		try:
			f = open(code, 'r')
			data['code'] = f.read()
			f.close()
		except:
			print 'Unable to read file: ' + code
			sys.exit(1)
	data['receiver'] = receiver
	return (job_id, data)

def storeJob(r, job_id, data):
	text = json.dumps(data)
	key = 'job:' + str(job_id)
	if args.verbose is True:
		print "Storing in key '" + key + "': " + text
	r.set(key, text)
	if args.verbose is True:
		print 'Pushing job id ' + str(job_id) + ' onto job_queue'
	r.rpush('job_queue', job_id)

def waitForResults(r, job_id, hosts):
        key = 'job_done:' + str(job_id)
	if args.verbose is True:
		print 'Waiting for results in queue ' + key
	for host in hosts:
		(queue, h) = r.blpop(key)
		if args.verbose is True:
			print 'Got results from ' + h

def printResults(r, job_id, hosts):
	hosts.sort()
	for host in hosts:
		text = r.get('job_result:' + str(job_id) + ':' + host)
		data = json.loads(text)
		output = data['results'].rstrip()
		print host + ' => ' + output

(job_id, data) = createJob(r, args.host, args.command, args.code, args.receiver)
storeJob(r, job_id, data)
waitForResults(r, job_id, data['hosts'])
printResults(r, job_id, data['hosts'])
