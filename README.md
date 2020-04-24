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

### Commands in interactive mode

In addition to `threads` and `console`, interactive mode has the following commands:

* `thread` and `greenlet` allow to select current thread or greenlet
* `bt` (also `backtrace`) prints backtrace of selected thread/greenlet
* `up`/`down` allow walking up/down call stack of selected thread/greenlet, selecting particular frame
* `locals`/`globals`/`closure` print corresponding set of variables in selected frame
* `x` (also `p`, `print`, `examine`) print value of variable in selected frame

## Features

Pystol supports attaching to both python2 and python3, getting interative python shell, dumping stack traces of threads and greenlets and examining variable values. There is some code for stopping the process and stepping, but it is rather unstable.
Only CPython is supported.