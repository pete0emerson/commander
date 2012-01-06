#!/usr/bin/env python

import subprocess
import re

proc = subprocess.Popen(['uname', '-a'], stdout=subprocess.PIPE)
stdout, stderr = proc.communicate('')
stdout = re.sub(r'^(\S+).*$', r'\1', stdout)
print stdout.rstrip()
