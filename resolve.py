import os
import platform

import cfg
import client


def environment(sys_platform=None, overrides=['user'], force=False):
    '''
    env configs coded by platform
    '''
    
    #simple caching mechanism
    #ToDo validate value
    if os.environ.get('GT_CONFIG_VER', None) and not force:
        return { evar:val for evar,val in os.environ.iteritems() if "GT_" in evar }
    else:
        os.environ['GT_CONFIG_VER'] = "1.0.0"
    
    results = {}
    if not sys_platform:
        sys_platform = platform.system().lower()
    
    user_overrides = []
    if isinstance(overrides,(list,tuple)):
        user_overrides = overrides
    
    
    #collect configs
    _Cfg_list = [cfg.init_cfg(cfg_data) for cfg_data in client.get_configs("env")]
    
    
    #add local environment
    #add dev root if not exists
    if not os.environ.get('GT_DEV_ROOT',None):
        home = os.environ.get("USERPROFILE",os.environ.get("HOME"))
        os.environ['GT_DEV_ROOT'] = os.path.join(home,'dev').replace('\\','/')
    
    
    #build user environment config
    if 'user' in user_overrides:
        _UserEnvCfg = cfg.EnvCfg()
        _UserEnvCfg.code = "user"
        _UserEnvCfg.name = "User-Environment"
        _UserEnvCfg.collection.append(os.environ.copy())
        _Cfg_list.append(_UserEnvCfg)
    
    #init chain
    _CfgChain = cfg.CfgChain( "env", _Cfg_list )
    
    #merge selected cfgs
    cfg_selection = ['default', sys_platform] + user_overrides
    _EnvCfg = _CfgChain.resolve(value=cfg_selection, merge_collection=True)
    
    #return collection members matching key, value
    results = _EnvCfg.find_one(key="GT_CONFIG_VER", value=[os.environ["GT_CONFIG_VER"]])
    #update runtime environment
    os.environ.update(results)
    
    return results


def packages(project="default", packages=[], overrides=['user']):
    """
    Return a list of BasePkg objects from PkgCfg Chain
    
    project = < Project Code > project pkg config overrides
    packages = < [pkgname,...] > If None (default) return all known packages.
    user = < True | False > If True (default) include user pkg config overrides (~/.package-cfg.json).
    """
    
    environment()
    user_overrides = []
    if isinstance(overrides,(list,tuple)):
        user_overrides = overrides
    
    results = []
    _cfg_type = "pkg"
    _Cfg_list = [cfg.init_cfg(cfg_data) for cfg_data in client.get_configs(_cfg_type)] 
    
    #add local override
    if 'user' in overrides:
        _home = os.environ.get("USERPROFILE", os.environ.get("HOME"))
        _home = os.path.normpath(_home)
        _local_cfg = os.path.join(_home,".package-cfg.json")
        
        try:
            with open(_local_cfg) as _cfg_file:
                _cfg_data = json.load(_cfg_file)
                _Cfg_list.append(cfg.init_cfg(_cfg_data))
        except:
            pass
        
    #init chain
    _CfgChain = cfg.CfgChain( _cfg_type, _Cfg_list )
    pkg_selection = ['default',project.lower()] + user_overrides
    _PkgCfg = _CfgChain.resolve(value=pkg_selection)
    _pkg_list = _PkgCfg.find(value=packages)
    if _pkg_list:
        import pkg
        for _pkg in _pkg_list: 
            results.append(pkg.BasePkg(**_pkg))
            
    return results



def unittest():
    '''
    TODO: make real unittest :)
    '''
    from pprint import pprint as pp
    
    _env = environment()
    _Pkgs = packages()
    for p in _Pkgs:
        pp(p.dump())
        print "path ",p.path
        print "deploy ", p.deploy_root
    
if __name__ == '__main__':
    unittest()