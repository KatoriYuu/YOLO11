import fcntl
import os
import sys

import SystemEvent

file_dir = os.path.dirname(os.path.abspath(__file__))
lock_file = file_dir + "/lockfile.lck"
print(lock_file)


class Locker:
    def __enter__(self):
        self.fp = open(lock_file, "w")
        fcntl.flock(self.fp.fileno(), fcntl.LOCK_EX)

    def __exit__(self, _type, value, tb):
        fcntl.flock(self.fp.fileno(), fcntl.LOCK_UN)
        self.fp.close()


def main():
    argc = len(sys.argv)
    if argc != 2:
        print("agent.py: Incorrect arguments")
        exit(-1)
    with Locker():
        target = sys.argv[1]
        agent = "agent-" + target
        invocation = SystemEvent.SystemEvent("invoke")
        event_target = SystemEvent.SystemEvent(target)
        event_agent = SystemEvent.SystemEvent(agent)
        event_target.set()
        invocation.set()
        event_agent.wait()  # timeout here
        event_agent.clear()


if __name__ == "__main__":
    main()
