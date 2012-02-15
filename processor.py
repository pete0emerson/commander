#!/usr/bin/env python

import zmq
import json
import subprocess
from multiprocessing import Process
from time import sleep
import os
from tempfile import mkstemp
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--verbose', dest='verbose', action='store_true', help='Turn on verbose mode')
args = parser.parse_args()

def getJob(socket):
	if args.verbose:
		print "Waiting for a job to process"
	message = socket.recv()
	if args.verbose:
		print 'Got a job: ' + message
	return json.loads(message)

def processCommand(data):
	if 'code' in data:
		(fd, file) = mkstemp(prefix='code_', dir='/tmp')
		f = os.fdopen(fd, "w")
		f.write(data['code'])
		f.close()
		os.chmod(file, 0755)
		data['command'] = file
	proc = subprocess.Popen(data['command'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
	stdout_value, stderr_value = proc.communicate('')
	data['exit_code'] = proc.returncode
	data['results'] = str(stdout_value)
	if 'code' in data:
		os.remove(file)
	text = json.dumps(data)
	if args.verbose:
		print 'Sending to ' + data['receiver'] + ': ' + text
	context = zmq.Context()
	rep = context.socket(zmq.PUSH)
	rep.connect(data['receiver'])
	rep.send(text)
	rep.close()

def cleanupProcesses(procs):
	for p in procs:
		if not p.is_alive():
			p.join()
			procs.remove(p)
	return procs

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind("tcp://*:8888")
procs = []
while True:
	data = getJob(socket)
	p = Process(target=processCommand, args=(data,))
	p.start()
	procs.append(p)
	procs = cleanupProcesses(procs)
