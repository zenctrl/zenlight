#!/usr/bin/env python

import sys, time, requests, json
from nuimo import NuimoController
from daemon import Daemon 
 
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
