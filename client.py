
import os
import re
import json

#config server stub
def get_configs(cfg_type=None):
    """
    TODO: make this look more like a query
    with filter
    """
    results = []
    _cfg_root = os.environ.get("GT_CONFIG_SERVER",os.path.join(os.path.dirname(__file__),"..","cfg-db"))
    for _cfg_path in [f for f in os.listdir(_cfg_root) if re.match(r'.*\.json$', f)]:
        with open(os.path.join(_cfg_root,_cfg_path)) as _cfg_file:
            try:
                _cfg_data = json.load(_cfg_file)
                if _cfg_data['type'] == cfg_type or not cfg_type:
                    results.append(_cfg_data)
            except Exception as err:
                print("{}".format(err))
                pass
    return results

def put_configs(cfg_list, **kw):
    """
    TODO: make this look more like a query
    with filter
    """
    
    path = os.path.join(os.environ.get("GT_CONFIG_ROOT"),"staging","cfg-db")
    cfg_db_path = os.path.join(os.environ.get("GT_CONFIG_ROOT"),"cfg-db").replace('\\','/')
    #if kw.get('repo', False):
    #    os.chdir(path)
    #    message = kw.get('notes') or 'auto-commit'
    #    proc = subprocess.Popen('git fetch --all'.format(message),
    #                          shell=True,
    #                          stderr=subprocess.PIPE,
    #                          stdout=subprocess.PIPE)
    #    out, err = proc.communicate()
    #    msg = out + err
    #    exit_status = proc.returncode
    #    proc = subprocess.Popen('git reset --hard origin/master'.format(message),
    #                          shell=True,
    #                          stderr=subprocess.PIPE,
    #                          stdout=subprocess.PIPE)
    #    out, err = proc.communicate()
    #    msg = out + err
    #    exit_status = proc.returncode
        
    for cfg in cfg_list:
        path = os.path.normpath(os.path.join(cfg_db_path, "{}.json".format(cfg.code)))
        with open(path, 'w') as config_file:
            json.dump(cfg.dump(), config_file, indent=4, sort_keys=True)
    #if kw.get('repo', False):
    #    proc = subprocess.Popen('git add -A && git commit -m \"{}\"'.format(message),
    #                              shell=True,
    #                              stderr=subprocess.PIPE,
    #                              stdout=subprocess.PIPE)
    #    out, err = proc.communicate()
    #    msg = out + err
    #    exit_status = proc.returncode
    #    if exit_status:
    #        if "git push" in msg or "up-to-date" in msg or "nothing to commit" in msg:
    #            pass
    #        else:
    #            raise Exception(msg)
    #    #push
    #    proc = subprocess.Popen("git push",
    #                          shell=True,
    #                          stderr=subprocess.PIPE,
    #                          stdout=subprocess.PIPE)
    #    err, out = proc.communicate()
    #    exit_status = proc.returncode
    #    #LOG.info(out)
    #    #LOG.error(err)
    #    if exit_status:
    #        raise Exception("out:{}\nerr:{}".format(out,err))
    #        
    #    proc = subprocess.Popen("git push",
    #                          shell=True,
    #                          stderr=subprocess.PIPE,
    #                          stdout=subprocess.PIPE)
    #    err, out = proc.communicate()
    #    exit_status = proc.returncode
    #    
    return cfg_db_path

def publish_configs(**kw):
    '''
    publish to productions
    '''
    
    src = os.path.join(os.environ.get("GT_CONFIG_ROOT"),"staging","cfg-db").replace('\\','/')
    dst = os.path.join(os.environ.get("GT_CONFIG_ROOT"),"cfg-db").replace('\\','/')
    
    if not kw.get("repo", False):
        dir_util.copy_tree(src, dst, update=True)
    else:
        #commit
        message = kw.get('notes') or 'auto-commit'
        os.chdir(src)
        proc = subprocess.Popen('git add -A && git commit -m \"{}\"'.format(message),
                              shell=True,
                              stderr=subprocess.PIPE,
                              stdout=subprocess.PIPE)
        out, err = proc.communicate()
        msg = out + err
        exit_status = proc.returncode
        if exit_status:
            if "git push" in msg or "up-to-date" in msg or "nothing to commit" in msg:
                pass
            else:
                raise Exception(msg)
        #push
        proc = subprocess.Popen("git push",
                              shell=True,
                              stderr=subprocess.PIPE,
                              stdout=subprocess.PIPE)
        err, out = proc.communicate()
        exit_status = proc.returncode
        #LOG.info(out)
        #LOG.error(err)
        if exit_status:
            raise Exception("out:{}\nerr:{}".format(out,err))
        
        #fetch changes
        os.chdir(dst)
        proc = subprocess.Popen('git fetch --all'.format(message),
                              shell=True,
                              stderr=subprocess.PIPE,
                              stdout=subprocess.PIPE)
        out, err = proc.communicate()
        msg = out + err
        exit_status = proc.returncode
        proc = subprocess.Popen('git reset --hard origin/master'.format(message),
                              shell=True,
                              stderr=subprocess.PIPE,
                              stdout=subprocess.PIPE)
        out, err = proc.communicate()
        msg = out + err
        exit_status = proc.returncode
        
        
        #proc = subprocess.Popen("git pull --ff-only",
        #                  shell=True,
        #                  stderr=subprocess.PIPE,
        #                  stdout=subprocess.PIPE)
        #err, out = proc.communicate()
        #exit_status = proc.returncode
        
        if exit_status:
            raise Exception("out:{}\nerr:{}".format(out,err))
        
        #proc = subprocess.Popen("git reset --hard origin/master",
        #                  shell=True,
        #                  stderr=subprocess.PIPE,
        #                  stdout=subprocess.PIPE)
        #err, out = proc.communicate()
        #exit_status = proc.returncode
        #
        #if exit_status:
        #    raise Exception("out:{}\nerr:{}".format(out,err))
        #
        #