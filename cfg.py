import os
import re


class BaseCfg(object):
    _code = 'base'
    _context = 'root'
    _default_key = None
    _default_value = None
    _config_fields = {}
    def __init__(self,cfg={}):
        self.collection=[]
        self.parent_id = -1
        self.code = self._code
        self.type = None
        self.id = -1
        self.__dict__ .update(cfg.copy())
        self.type = self._code

    def __str__(self):
        return pp.pformat(self.__dict__)
    
    def unicode2ascii(self, arg):
        '''
        recusrisevly replaces unicode with ascii
        '''
        if isinstance(arg, dict):
            return dict((self.unicode2ascii(key), self.unicode2ascii(value))
                        for key, value in arg.items())
        elif isinstance(arg, (list, tuple)):
            return [self.unicode2ascii(element) for element in arg]
        elif isinstance(arg, unicode):
            return arg.encode('utf-8')
        else:
            return arg

    def merge(self, cfg, merge_key=None, merge_collection=False, **kw):
        '''
        merge incoming cfg with current cfg
        '''
        if not merge_key:
            merge_key = self._default_key
        if not self.collection:
            self.collection = cfg.collection
        else:
            for cfg_m in cfg.collection:
                found = False
                for i, m in enumerate(self.collection):
                    if m.get(merge_key,None) and cfg_m.get(merge_key,None):
                        if m[merge_key] == cfg_m[merge_key]:
                            if merge_collection:
                                self.collection[i].update(cfg_m)
                            else:
                                self.collection[i] = cfg_m
                            found = True
                            break
                    else:
                        self.collection[i].update(cfg_m)
                        found = True
                        break
                if not found:
                    self.collection.append(cfg_m)

    def find(self, key=None, value=None, limit=None):
        '''
        find member(s) in collection by key and value
        '''
        if not key:
            key = self._default_key
        if not value and self._default_value:
            value = [self._default_value]   
        results = []
        
        if value:
            for m in self.collection:
                if m.get(key, None) in value:
                    results.append(m)
                if limit and len(results) >= limit:
                    break
        else:
            if limit:
                results = self.collection[0:limit-1]
            else:
                results = self.collection
                
        return self.transform(results)
    
    def find_one(self, key=None, value=None):
        results = None
        try:
            results = self.find(key, value, limit=1)[0]
        except:
            pass
        return results
    
    def update(self, data, key=None):
        '''
        update member in collection
        searching by key
        '''
        if not key:
            key = self._default_key
        if not data.get(key, None):
            return False

        for idx, m in enumerate(self.collection):
            if m.get(key, None) == data[key]:
                self.collection[idx].update(data)
                return True
     
    def upsert(self, data, key=None):
        '''
        update member and append if not found in collection
        '''
        if not key:
            key = self._default_key
        if not data.get(key, None):
            return False
        
        if not self.update(data,key):
            self.collection.append(data)
        
        return True
    
    def dump(self):
        data = self.__dict__.copy()
        if self._config_fields:
            _skip = set(data.keys()) - set(self._config_fields)
            for attr in _skip:
                data.pop(attr)
        
        return data


    
    def transform(self, m):
        return m


class EnvCfg(BaseCfg):
    '''
    Class to manipulate an EnvCfg
    '''
    _code = 'env'
    _default_key = "GT_CONFIG_VER"
    _default_value = os.environ.get("GT_CONFIG_VER","1.0.0")
    def __init__(self, cfg={}):
        super(EnvCfg, self).__init__(cfg)

    def _expand(self, environ={}):
        envvars = environ.keys()
        re_dict = {}
        for evar in envvars:
            match = True
            while match:
                match = False
                for re_var in envvars:
                    re_var = re_var.strip()
                    re_var = re_var.rstrip()
                    if re_var != evar:
                        re_str = r"\$\{" + re_var + "\}"
                        regex = re.compile(re_str)
                        replace_str = environ[re_var].replace("\\", "/")
                        search_str = environ[evar].replace("\\", "/")
                        (new_str, found_match) = regex.subn(
                            replace_str, search_str)
                        if found_match > 0:
                            environ[evar] = new_str
                            match = True
        return environ
    
    def transform(self, data):
        for m in data:
            m = self._expand(m)
        return self.unicode2ascii(data)


class PkgCfg(BaseCfg):
    _code = 'pkg'
    _default_key = 'name'
    def __init__(self, cfg={}):
        super(PkgCfg, self).__init__(cfg)

    
class CfgChain(object):
    '''
    Class representing a list of cfg objects
    '''
    _default_key = "code"
    _default_value = "default"
    def __init__(self, cfg_type='base', cfg_list=[], context=None):
        setattr(self, 'CfgClass', resolve_cfg_class(cfg_type))
        setattr(self, 'context', context)
        
        self.chain = []
        self._init_chain(cfg_list)

    def _init_chain(self, cfg_list):
        for cfg in cfg_list:
            self.upsert(cfg)

    def insert(self, idx, cfg):
        """
            removes duplicate
        """
        if isinstance(cfg, self.CfgClass):
            match_cfg_idx = [idx for idx, _cfg in enumerate(self.chain) if _cfg.id == cfg.id]
            if match_cfg_idx:
                self.chain.pop(match_cfg_idx[0])
        if len(self.chain) > idx:
            self.chain.insert(idx,cfg)
        else:
            self.chain.append(cfg)
            
    def append(self, cfg):
        if isinstance(cfg, self.CfgClass):
            match_cfg_idx = [idx for idx, _cfg in enumerate(self.chain) if _cfg.id == cfg.id]
            if match_cfg_idx:
                self.chain.pop(match_cfg_idx[0])
        self.chain.append(cfg)
        
    def upsert(self, cfg):
        if isinstance(cfg,self.CfgClass):
            match_cfg_idx = [idx for idx,_cfg in enumerate(self.chain) if _cfg.id == cfg.id]
            if match_cfg_idx:
                self.chain[match_cfg_idx[0]] = cfg
            else:
                self.chain.append(cfg)
        return cfg
    
    def update(self, cfg, key='id'):
        if key not in self.CfgClass().__dict__:
            return
        if isinstance(cfg,self.CfgClass):
            match_cfg_idx = [idx for idx,_cfg in enumerate(self.chain) if _cfg.__dict__[key] == cfg.__dict__[key]]
            if match_cfg_idx:
                self.chain[match_cfg_idx[0]] = cfg
    
    def find_one(self, key=None, value=None):
        results = None
        try:
            results = self.find(key, value, limit=1)[0]
        except:
            pass
        return results
                
    def find(self, key=None, value=None, limit=None):
        """
        value is treated as a filter
        """
        if not key:
            key = self._default_key
        results = []
        if key not in self.CfgClass().__dict__:
            return results
        
        if not isinstance(value, (list,tuple)):
            value = [value]
        if value:
            for m in self.chain:
                if m.__dict__[key] in value:
                    results.append(m)
                if limit and len(results) >= limit:
                    break
            
        return results
    
    def resolve(self, **kw):
        """
        sel = None > all membere
        sel = list() > idx of members
        sel = dict() > key, val
        """
        result = self.CfgClass()
        filter_cfgs = []
        for v in kw.get('value',[self._default_value]):
            filter_cfgs.extend(self.find(value=[v],limit=1))
        for cfg in filter_cfgs:
            result.merge(cfg,**kw)
        return result


def init_cfg(cfg):
    _CfgClass = resolve_cfg_class(cfg.get('type','base'))
    return _CfgClass(cfg)


def resolve_cfg_class(code):
    result = BaseCfg
    for cfgClass in BaseCfg.__subclasses__():
        if cfgClass._code == code:
            result = cfgClass
            break
    return result



def unittest():
    '''
    TODO: make real unittest :)
    '''
    from pprint import pprint as pp
    import pkg
    import client

    
    _cfg_type = "pkg"
    _cfg_list = [init_cfg(c) for c in client.get_configs(_cfg_type)] 
    _CfgChain = CfgChain( _cfg_type, _cfg_list )
    _PkgCfg = _CfgChain.resolve()
    _Pkg = pkg.BasePkg(name="gtbubba")
    _Pkg.version = "3.1.0"
    print _Pkg
    
    _PkgCfg.upsert(_Pkg.dump())
    _pkg = _PkgCfg.find_one(value=_Pkg.name)
    _NewPkg = pkg.BasePkg(**_pkg)
    print _NewPkg
    
    
    

if __name__ == '__main__':
    unittest()

