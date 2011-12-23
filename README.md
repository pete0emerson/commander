This set of scripts uses Redis as its storage engine and in particular
uses Redis's blocking pop off of lists to avoid polling the database for command
status. It also uses zeromq for all interprocess transportation.

Diagram about how the data flows:
http://www.asciiflow.com/#868081871833843538

Install zeromq from source:
http://www.zeromq.org/intro:get-the-software

Install redis from source:
http://redis.io/download

Fire up:
```shell
./transmitter.py &
./multiprocessor.py &
./receiver.py &
```

Run the commander:

```shell
./commander.py --host=localhost --receiver=tcp://localhost:9999 --command=date
```
```shell
$ ./commander.py --help
usage: commander.py [-h] --host HOST --receiver RECEIVER [--verbose]
                    (--command COMMAND | --code CODE)

Execute a command asynchronously on multiple hosts

optional arguments:
  -h, --help           show this help message and exit
  --host HOST          The target host(s) (multiple --host flags may be
                       specified)
  --receiver RECEIVER  The receiver to send results to
  --verbose            Turn on verbose mode
  --command COMMAND    The command to be run
  --code CODE          File to be injected and run
```

You can even inject and run code:

```shell
$ ./commander.py --host=localhost --receiver=tcp://localhost:9999 --code=./inject.py
localhost => Darwin
```
