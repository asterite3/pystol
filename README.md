# pystol

Pystol is a tool for debugging live python processes. It attaches to python process given it's PID.

**Warning**: this is experimental and a work in progress. Use at your own risk.

## Installation

**GDB** is required as Pystol uses it to attach to process.

Also, Pystol uses [PyDev.Debugger](https://github.com/fabioz/PyDev.Debugger) as a wrapper around GDB for attaching, install it with:

```
pip install -r requirements.txt
```

## Usage

Attach and enter interactive mode:

```
python pystol.py PID
```

Get python interactive shell inside process:

```
python pystol.py PID console
```

Dump stacks of all threads (and greenlets, if any):

```
python pystol.py PID threads --stacks
```

## What is it for

Pystol is most useful when you have a python process on a server which is stuck and not responding or is otherwise misbehaving (say, eating up more and more memory) and you don't understand what's happening inside it and you **can't afford to restart it and add a debug print** - because the bug simply won't reproduce (or will reproduce only after a lot of time). In such case it may be desired to attach to that process right from server's command line and debug it.

If you can afford using and IDE (python process is running on your laptop or you are confortable with forwarding ports to the server for remote debugging), probably a better option would be to use [
PyDev.Debugger](https://github.com/fabioz/PyDev.Debugger) with PyCharm/VSCode/PyDev or some similar one.

If you need to **profile** a live process, [py-spy](https://github.com/benfred/py-spy) will be a better option.

## Commands in interactive mode

In addition to `threads` and `console`, interactive mode has the following commands:

* `thread` and `greenlet` allow to select current thread or greenlet
* `bt` (also `backtrace`) prints backtrace of selected thread/greenlet
* `up`/`down` allow walking up/down call stack of selected thread/greenlet, selecting particular frame
* `locals`/`globals`/`closure` print corresponding set of variables in selected frame
* `x` (also `p`, `print`, `examine`) print value of variable in selected frame

## Features

Pystol supports attaching to both python2 and python3, getting interative python shell, dumping stack traces of threads and greenlets and examining variable values. There is some code for stopping the process and stepping, but it is rather unstable.
Only CPython is supported.