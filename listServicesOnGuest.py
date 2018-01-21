#!/usr/bin/env python
import sys
import os
import csv
import socket
import signal
try:
  from setproctitle import setproctitle
except:
  errMsg = "please install setproctitle see http://goo.gl/GNmtIX :C"
  print >> sys.stderr, errMsg
  sys.exit(2)

 
#from pprint import pprint

try:
   from pysphere import VIServer,VIException,VIApiException
   from pysphere.resources import VimService_services as  VI
except ImportError, e:
  errMsg ="please install pysphere see http://goo.gl/c7HGGi :C"
  print >> sys.stderr,errMsg
  sys.exit(2)

if (len(sys.argv) != 5) :
  errMsg = ("%s %s %s")%("usage",sys.argv[0],"[vcenter/esxi host] [login] [password] [outputfile] IN THAT ORDER!! :@")
  print >> sys.stderr,errMsg
  sys.exit(3)

#TODO functions to catch args parameters as named args
host = str(sys.argv[1])
usr = str(sys.argv[2])
psw = str(sys.argv[3])
procname = ("%s %s %s %s") % (sys.argv[0], host, usr, "xxxxx")
setproctitle(procname)

outPutFile = str(sys.argv[4])
#TODO
def validateIfOutPutFileExists(_outputfile):
  pass
  return None

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

def getDiskPerServer(s):
  properties = s._retrieve_properties_traversal(property_names=["name","storage.perDatastoreUsage"], obj_type="VirtualMachine")
  vms = {}
  for p in properties:
      name = ""
      committed = 0
      for prop in p.PropSet:
          if prop.Name == "name":
              name = prop.Val
              continue
          if prop.Name == "storage.perDatastoreUsage":
              for data in getattr(prop.Val,
  "VirtualMachineUsageOnDatastore", []):
                  committed += getattr(data , "Committed", 0)
  vms[name] = committed
  return vms[name]
def usageDiskPerVm(_vm): 
  disksSizesOnGbs=[]
  for i in range(0,len(_vm._disks)):
    if  ((_vm._disks[i]['device']['type']) == 'VirtualDisk'):
        disksSizesOnGbs.append((((_vm._disks[i]['device']['capacityInKB']) / 1024) / 1024))
  disksSizesOnGbs=set(disksSizesOnGbs)
  return disksSizesOnGbs

def listServices(_vm,_server):
   apiVersion=_server.get_api_version().replace(".","")
   try :
     apiVersion=int(apiVersion)
   except ValueError:
     apiVersion=0
   vmName=str(_vm.get_property('name',from_cache=False))
   vmStatus = _vm.get_status().replace(" ","-")
   vmwareToolsStatus = _vm.get_tools_status().replace(" ","-")
   if not (vmStatus == "POWERED-OFF") and not (vmwareToolsStatus == "NOT-RUNNING") and ( apiVersion >= 50): 
     try :
       _vm.login_in_guest("root", "WeiPh1ah")
       print _vm.list_processes()
     except VIApiException, e:
      errMsg = "bad guest credentials :C"
      print >> sys.stderr,errMsg
#main
try:
  serverHandle = openServerConnection(host,usr,psw)
  vmlist = serverHandle.get_registered_vms()
  ofile = open(outPutFile,"a+")
  writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL,lineterminator='\n',skipinitialspace=True)
  #
  headings = ['Virtualization Host','PowerStatus','VmWareToolsVersion','VmWareToolsStatus','NumCpus','MemoryInMb','DiskSizesInGbs','Uuid','Name','Hostname','Ip','Guest_id','Guest_full_name','Pool']
  writer.writerow(headings)
  
  for vm in vmlist:
    vm = serverHandle.get_vm_by_path(vm)
    vmStatus = vm.get_status().replace(" ","-")
    vmwareToolsVersion = getVmwareToolsVersion(vm)
    vmwareToolsStatus = vm.get_tools_status()
    vmCpus = str(vm.properties.config.hardware.numCPU)
    vmMem  = str(vm.properties.config.hardware.memoryMB)
    vmUuid = str(vm.properties.config.uuid)
    vmDisksSizesInGbs = str(usageDiskPerVm(vm))\
        .replace("set","")\
        .replace("(","").replace("[","")\
        .replace(")","").replace("]","")
    vmName = str(vm.get_property('name',from_cache=False))
    vmHostName = str(vm.get_property('hostname',from_cache=False))
    vmIp = str(vm.get_property('ip_address',from_cache=False))
    vmGuestId = str(vm.get_property('guest_id',from_cache=False))
    vmGuestFullName = str(vm.get_property('guest_full_name',from_cache=False))
    vmPool = str(vm.get_resource_pool_name())
    listServices(vm,serverHandle)
    #
    row = []
    row.append(host.strip().encode("utf-8"))
    row.append(vmStatus.strip().encode("utf-8"))
    row.append(vmwareToolsVersion.strip().encode("utf-8"))
    row.append(vmwareToolsStatus.strip().encode("utf-8"))
    row.append(vmCpus.strip().encode("utf-8"))
    row.append(vmMem.strip().encode("utf-8"))
    row.append(vmDisksSizesInGbs.strip().encode("utf-8"))
    row.append(vmUuid.strip().encode("utf-8"))
    row.append(vmName.strip().encode("utf-8"))
    row.append(vmHostName.strip().encode("utf-8"))
    row.append(vmIp.strip().encode("utf-8"))
    row.append(vmGuestId.strip().encode("utf-8"))
    row.append(vmGuestFullName.strip().encode("utf-8"))
    row.append(vmPool.strip().encode("utf-8"))
    writer.writerow(row)
    usageDiskPerVm(vm)
  #
  ofile.close
  closeServerConnection(serverHandle)
except KeyboardInterrupt:
  errMsg ="\nctrl + c pressed..aborting"
  print >> sys.stderr,errMsg
  sys.exit(0)
