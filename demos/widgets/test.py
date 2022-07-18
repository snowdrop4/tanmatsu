# Let demo import from root directory
import sys, os, fcntl
sys.path.insert(1, os.path.normpath(os.path.join(sys.path[0], '../..')))

from tanmatsu import Tanmatsu
from tanmatsu.widgets import List, Button, TextLog


def exhaust_file_descriptor(fd):
	buff = b''
	
	while True:
		try:
			buff += os.read(fd, 1)
		except BlockingIOError:
			return buff

sys.stdin  = open("/dev/stdin",  "r")
sys.stdout = open("/dev/stdout", "w")

print(sys.stdin.fileno())
print(sys.stdout.fileno())

# Set up blocking and non-blocking bitmasks for stdin:
stdin_fcntl_initial     = fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)
stdin_fcntl_nonblocking = stdin_fcntl_initial |  os.O_NONBLOCK
stdin_fcntl_blocking    = stdin_fcntl_initial & ~os.O_NONBLOCK
# ... and do the same for stdout:
stdout_fcntl_initial     = fcntl.fcntl(sys.stdout.fileno(), fcntl.F_GETFL)
stdout_fcntl_nonblocking = stdout_fcntl_initial |  os.O_NONBLOCK
stdout_fcntl_blocking    = stdout_fcntl_initial & ~os.O_NONBLOCK

print(f"setting stdin to {stdin_fcntl_nonblocking}, and stdout to {stdout_fcntl_blocking}")

fcntl.fcntl(sys.stdin.fileno(),  fcntl.F_SETFL, stdin_fcntl_nonblocking)
fcntl.fcntl(sys.stdout.fileno(), fcntl.F_SETFL, stdout_fcntl_blocking)

print("stdin:")
print(f"initial {stdin_fcntl_initial}")
print(f"nonblocking {stdin_fcntl_nonblocking}")
print(f"blocking {stdin_fcntl_blocking}")
print(f"actual {fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)}")
print("")
print("stdout:")
print(f"initial {stdout_fcntl_initial}")
print(f"nonblocking {stdout_fcntl_nonblocking}")
print(f"blocking {stdout_fcntl_blocking}")
print(f"actual {fcntl.fcntl(sys.stdout.fileno(), fcntl.F_GETFL)}")
