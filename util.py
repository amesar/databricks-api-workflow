
import sys, time

def log_print(*args):
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
    sys.stderr.write("{} ".format(now))
    for x in args:
        sys.stderr.write("{}".format(x))
    #sys.stderr.write("\n")
