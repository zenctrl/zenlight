#!/usr/bin/env python

import sys, os, time, atexit
import requests
import json
from nuimo import NuimoController
from signal import SIGTERM

class Daemon:
        """
        A generic daemon class.

        Usage: subclass the Daemon class and override the run() method
        """
        def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
                self.stdin = stdin
                self.stdout = stdout
                self.stderr = stderr
                self.pidfile = pidfile

        def daemonize(self):
                """
                do the UNIX double-fork magic, see Stevens' "Advanced
                Programming in the UNIX Environment" for details (ISBN 0201563177)
                http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
                """
                try:
                        pid = os.fork()
                        if pid > 0:
                                # exit first parent
                                sys.exit(0)
                except OSError, e:
                        sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
                        sys.exit(1)

                # decouple from parent environment
                os.chdir("/")
                os.setsid()
                os.umask(0)

                # do second fork
                try:
                        pid = os.fork()
                        if pid > 0:
                                # exit from second parent
                                sys.exit(0)
                except OSError, e:
                        sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
                        sys.exit(1)

                # redirect standard file descriptors
                sys.stdout.flush()
                sys.stderr.flush()
                si = file(self.stdin, 'r')
                so = file(self.stdout, 'a+')
                se = file(self.stderr, 'a+', 0)
                os.dup2(si.fileno(), sys.stdin.fileno())
                os.dup2(so.fileno(), sys.stdout.fileno())
                os.dup2(se.fileno(), sys.stderr.fileno())

                # write pidfile
                atexit.register(self.delpid)
                pid = str(os.getpid())
                file(self.pidfile,'w+').write("%s\n" % pid)

        def delpid(self):
                os.remove(self.pidfile)

        def start(self):
                """
                Start the daemon
                """
                # Check for a pidfile to see if the daemon already runs
                try:
                        pf = file(self.pidfile,'r')
                        pid = int(pf.read().strip())
                        pf.close()
                except IOError:
                        pid = None

                if pid:
                        message = "pidfile %s already exist. Daemon already running?\n"
                        sys.stderr.write(message % self.pidfile)
                        sys.exit(1)

                # Start the daemon
                self.daemonize()
                self.run()

        def stop(self):
                """
                Stop the daemon
                """
                # Get the pid from the pidfile
                try:
                        pf = file(self.pidfile,'r')
                        pid = int(pf.read().strip())
                        pf.close()
                except IOError:
                        pid = None

                if not pid:
                        message = "pidfile %s does not exist. Daemon not running?\n"
                        sys.stderr.write(message % self.pidfile)
                        return # not an error in a restart

                # Try killing the daemon process       
                try:
                        while 1:
                                os.kill(pid, SIGTERM)
                                time.sleep(0.1)
                except OSError, err:
                        err = str(err)
                        if err.find("No such process") > 0:
                                if os.path.exists(self.pidfile):
                                        os.remove(self.pidfile)
                        else:
                                print str(err)
                                sys.exit(1)

        def restart(self):
                """
                Restart the daemon
                """
                self.stop()
                self.start()

        def run(self):
                """
                You should override this method when you subclass Daemon. It will be called after the process has been
                daemonized by start() or restart().
                """
 
 
#class zenlight:#(Daemon):
   #def run(self):
def main():
      # Discover Nuimo Controllers
      nuimo = NuimoController('CE:D8:42:A7:9A:78')

      #adapter = 'hci0'  # Typical bluetooth adapter name
      #nuimo_manager = NuimoDiscoveryManager(bluetooth_adapter=adapter, delegate=DiscoveryLogger())
      #nuimo_manager.start_discovery()

      # Were any Nuimos found?
      #if len(nuimo_manager.nuimos) == 0:
      #    print('No Nuimos detected')
      #    sys.exit(0)

      # Take the first Nuimo found.
      #nuimo = nuimo_manager.nuimos[0]

      # Set up handling of Nuimo events.
      # In this case just log each incoming event.
      # NuimoLogger is defined below.
      nuimo_event_delegate = NuimoLightController()
      nuimo.set_delegate(nuimo_event_delegate)

      # Attach to the Nuimo.
      nuimo.connect()

      # Display an icon for 2 seconds
      interval = 2.0

      MATRIX_LIGHTBULB = (
         "         " +
         "   ...   " +
         "  .   .  " +
         "  .   .  " +
         "  .   .  " +
         "   ...   " +
         "   ...   " +
         "   ...   " +
         "    .    ")

      nuimo.write_matrix(MATRIX_LIGHTBULB, interval)

      # Nuimo events are dispatched in the background
      while (True):
         time.sleep(1)
      nuimo.disconnect()
 
#if __name__ == "__main__":
#   daemon = zenlight('/tmp/zenlight.pid')
#   if len(sys.argv) == 2:
#      if 'start' == sys.argv[1]:
#         daemon.start()
#      elif 'stop' == sys.argv[1]:
#        daemon.stop()
#      elif 'restart' == sys.argv[1]:
#         daemon.restart()
#      else:
#         print "Unknown command"
#         sys.exit(2)
#      sys.exit(0)
#   else:
#      print "usage: %s start|stop|restart" % sys.argv[0]
#      sys.exit(2)

class NuimoLightController:
   def connection_state_changed(self, state, error=None):
        print (state)
        self.connect()
   def received_gesture_event(self, event):
        state = requests.get('http://192.168.178.26:8080/api/593401F6D7/groups/3/')
        state = state.json()
        #print(json.dumps(state))
        state_light_on = state["action"]["on"]
        state_bri = state["action"]["bri"]


        if (event.gesture == 1): # BUTTON_PRESS
           if (state_light_on):
              on = 'false'
           else:
              on = 'true' 
           requests.put('http://192.168.178.26:8080/api/593401F6D7/groups/3/action', data='{"on": '+on+'}')
        elif (event.gesture == 3) and (event.value > 0): # ROTATE_RIGHT
           if (state_bri <= 255):
              resp = requests.put('http://192.168.178.26:8080/api/593401F6D7/groups/3/action', data='{"bri": '+str(state_bri+10)+'}')
        elif (event.gesture == 3) and (event.value < 0): #ROTATE_LEFT
              resp = requests.put('http://192.168.178.26:8080/api/593401F6D7/groups/3/action', data='{"bri": '+str(state_bri-10)+'}')

        #print("received event: name={}, gesture_id={}, value={}".format(event.name, event.gesture ))

if __name__ == '__main__':
    main()
