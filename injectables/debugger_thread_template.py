import sys, threading, json, functools

_respond = lambda control_out, data: control_out.write(json.dumps(data) + chr(0x0a))

def debugger_thread_func():
    sys.stdin = LocalProxy(sys.stdin, ReplacedStdin("%s"))
    out = "%s"
    sys.stdout = LocalProxy(sys.stdout, ReplacedOut(out))
    sys.stderr = LocalProxy(sys.stderr, ReplacedOut(out))

    with open("%s") as control_in, open("%s", "w", 1) as control_out:
        respond = functools.partial(_respond, control_out)
        while True:
            l = int(control_in.readline())
            control_command = control_in.read(l)
            if control_command == "ping":
                respond("pong")
                continue
            exec(control_command)

debugger_thread = threading.Thread(target=debugger_thread_func)
debugger_thread.daemon = True
debugger_thread.start()