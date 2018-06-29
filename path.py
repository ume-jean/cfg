#!/usr/bin/python

import sys, os
import logging
import platform
from pprint import pprint as pp
from pprint import pformat as pf
import resolve



#KomodoIDE Remote Debugging
remote_brk = lambda: sys.stdout.write("remote break")
if os.environ.get("_REMOTE_DEBUG_",'False') == 'True':
    try:
        from dbgp.client import brk
        remote_brk = lambda: brk(host=os.environ.get("REMOTE_DEBUG_HOST","127.0.0.1"),
                                 port=int(os.environ.get("REMOTE_DEBUG_PORT",'9000')))
    except:
        pass
    
if __name__ == '__main__':
    
    #if not os.environ.get('GT_ROOT',None):
    resolve.environment()
        
    project = "default"
    
    pkgs = []
    if len(sys.argv) > 2:
        project = sys.argv[1]
        for i in range(2, len(sys.argv)):
            pkgs.append(sys.argv[i])
    #remote_brk()        
    pkg_list = resolve.packages(project=project,packages=pkgs)
    
    paths = [p.path for p in pkg_list]
    if len(paths)>1:
        path_str = os.pathsep.join(paths)
    else:
        path_str = paths[0]
    sys.stdout.write(path_str)

