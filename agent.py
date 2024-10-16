import fcntl
import os
import sys
import SystemEvent

file_dir = os.path.dirname(os.path.abspath(__file__))
lock_file = file_dir + '/lockfile.lck'
print(lock_file)
class Locker:
    def __enter__ (self):
        os.makedirs(os.path.dirname(lock_file), exist_ok=True)
        self.fp = open(lock_file)
        fcntl.flock(self.fp.fileno(), fcntl.LOCK_EX)

    def __exit__ (self, _type, value, tb):
        fcntl.flock(self.fp.fileno(), fcntl.LOCK_UN)
        self.fp.close()

def main():
    argc = len(sys.argv)
    if argc != 2:
        print("agent.py: Incorrect arguments")
        exit(-1)
    with Locker():
        cam = 'cam' + sys.argv[1]
        agent = 'agent' + sys.argv[1]
        invocation = SystemEvent.SystemEvent('invoke')
        event_cam = SystemEvent.SystemEvent(cam)
        event_agent = SystemEvent.SystemEvent(agent)
        event_cam.set()
        invocation.set()
        event_agent.wait()
        event_agent.clear()

if __name__ == "__main__":
    main()
