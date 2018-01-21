#!/usr/bin/env python
import sys
import os
import os.path
import csv
import socket
import signal
#from pprint import pprint

try:
   from pysphere import VIServer,VIException,VIApiException
   from pysphere.resources import VimService_services as  VI
except ImportError, e:
  errMsg ="please install pysphere see http://goo.gl/c7HGGi"
  print >> sys.stderr,errMsg
  sys.exit(2)

if (len(sys.argv) != 4) :
  errMsg = ("%s %s %s")%("usage",sys.argv[0],"[vcenter/esxi host] [login] [password] IN THAT ORDER!! :@")
  print >> sys.stderr,errMsg
  sys.exit(3)

#TODO functions to catch args parameters as named args
host = str(sys.argv[1])
usr = str(sys.argv[2])
psw = str(sys.argv[3])

#TODO
def isHostVmwareAvailable(_host):
  try :
     s = socket.getaddrinfo(_host, None)
  except socket.error, e:
     errMsg = "bad hostname or ip :C"
     print >> sys.stderr,errMsg
     sys.exit(4)
      
def openServerConnection(_host="localhost",_usr="root",_psw="toor",_sock_timeout=30) :
    _server = None
    try: 
      _server = VIServer()
      isHostVmwareAvailable(_host)
      _server.connect(host,usr,psw,sock_timeout=_sock_timeout)
    except VIApiException, e:
      errMsg = "bad credentials :C"
      print >> sys.stderr,errMsg
      sys.exit(5)
    return _server

def closeServerConnection(server):
  server.disconnect()

#main
try:
  serverHandle = openServerConnection(host,usr,psw)
  vmlist = serverHandle.get_registered_vms(resource_pool='/Resources/somePool', status='poweredOn')
  for vm in vmlist:
    vm=serverHandle.get_vm_by_path(vm)
    vmName=(vm.get_property('name'))
    try: 
      guestPowerOff = vm.shutdown_guest()
      print vmName,"powering off softly"
    except:
      print vmName," hasn't guest VMware tools"
      try :
         hyperVisorPowerOff = vm.power_off(sync_run=False)
         print vmName,"powering off hardly"
      except:
        print vmName," stuck on power off check hypervisor ", host
  closeServerConnection(serverHandle)
except KeyboardInterrupt:
  errMsg ="ctrl + c pressed"
  print >> sys.stderr,errMsg
  sys.exit(0)
