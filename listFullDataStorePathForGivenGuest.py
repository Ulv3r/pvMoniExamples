#!/usr/bin/env python
from pysphere import VIServer
import sys
server = VIServer()
host = str(sys.argv[1])
usr = "root"
psw = "superSecret"
server.connect(host, usr, psw)
vm = server.get_vm_by_path(sys.argv[2])
print vm.get_property('path', from_cache=False)
