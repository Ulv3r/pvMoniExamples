#!/usr/bin/env python
import sys
import socket
import time
#from pprint import pprint

try:
   from pysphere import VIServer,VIException,VIApiException
   from pysphere.resources import VimService_services as  VI
except ImportError, e:
  errMsg ="please install pysphere see http://goo.gl/c7HGGi :C"
  print >> sys.stderr,errMsg
  sys.exit(2)

if (len(sys.argv) != 4) :
  errMsg = ("%s %s %s")%("usage",sys.argv[0],"[vcenter/esxi host] [login] [password] [outputfile] IN THAT ORDER!! :@")
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
def getVmwareToolsVersion(_vm):
  version = "None"
  for config in vm.properties.config.extraConfig:
    if (config.key == 'vmware.tools.internalversion' ) :
      #print config.key, "=>", config.value
      version=config.value
  return version

def createSnap(vm,snapName,snapDesc,snapRun) :
    try:
        vm.create_snapshot(snapName,description=snapDesc,sync_run=snapRun)
    except VIApiException, e:
      errMsg = "error taking snap :C"
      print >> sys.stderr,errMsg
      sys.exit(6)

def deleteAllSnap(vm,snapRun) :
    vmSnapList = vm.get_snapshots()
    for snap in vmSnapList :
       snapName=snap.get_name()
       deleteNamedSnap(vm,snapName,True,True)

def deleteNamedSnap(vm,snapName, snapRun, children) :
    try:
       print "vm.delete_named_snapshot(snapName,snapRun,True)"
       #vm.delete_snapshot(snapname,description=snapdesc,sync_run=snaprun)
    except VIApiException, e:
      errMsg = "error deleting snap :C"
      print >> sys.stderr,errMsg
      sys.exit(7)

#main
try:
  serverHandle = openServerConnection(host,usr,psw)
  vmlist = serverHandle.get_registered_vms()
  
  for vm in vmlist:
    vm = serverHandle.get_vm_by_path(vm)
    vmStatus = vm.get_status().replace(" ","-")
    today = time.strftime("%Y-%m-%d")
    vmName = str(vm.get_property('name',from_cache=False))
    if ( vmStatus == "POWERED-ON" ) :
      vmSnapSize = len(vm.get_snapshots())
      if ( vmSnapSize <= 0 ) :
          snapName=vmName + " snapshotFor " + today
          snapDesc=snapName
          print "createSnap(vmName,snapName,snapDesc,True)"
          print "snapshot create for " + vmName
      else:
          deleteAllSnap(vm,True)
          print "delete all snaps on " + vmName

  closeServerConnection(serverHandle)
except KeyboardInterrupt:
  errMsg ="ctrl + c pressed..aborting"
  print >> sys.stderr,errMsg
  sys.exit(0)
