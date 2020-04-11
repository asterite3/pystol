import sys

try:
    basestring
except NameError:
    basestring = (str, bytes)

def pipe_function(file_from, file_to, buffering, debug=False):
    if isinstance(file_from, basestring):
        if debug:
            print('from: will open', file_from)
        with open(file_from, buffering=buffering) as file_from_opened:
            if debug:
                print('opened', file_from)
            return pipe_function(file_from_opened, file_to, buffering)
    if isinstance(file_to, basestring):
        if debug:
            print('to: will open', file_to)
        with open(file_to, 'w', buffering=buffering) as file_to_opened:
            if debug:
                print('opened', file_to)
            return pipe_function(file_from, file_to_opened, buffering)
    while True:
        if buffering == 0:
            buffering = 1
        data = file_from.read(buffering)
        #print 'piping', data
        if not data:
            break
        file_to.write(data)
        file_to.flush()

def main():
    file_from = sys.argv[1]
    file_to = sys.argv[2]

    pipe_function(file_from, file_to)

    return 0

if __name__ == '__main__':
    exit(main())