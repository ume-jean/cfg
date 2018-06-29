
import os
import re
import inspect
import posixpath
import platform
import inspect
import pprint
import resolve

class BasePkgEnvError(BaseException):
    pass

class BasePkgInitError(BaseException):
    pass

class BasePkgVersionError(BaseException):
    pass

class BasePkg(object):
    '''
    Class to manage deployment packages
    name=<package_name>
    '''
    _platform_map= { "windows":"win",
                     "nt":"win",
                     "linux2":"linux",
                     "darwin":"osx"}
    _required_env = (
                    "GT_APP_ROOT",
                     "GT_PACKAGE_ROOT",
                     "GT_DEV_ROOT",
                     "GT_CONFIG_ROOT",
                     "GT_BUILD_ROOT")
    _root_map = {
        'app':'GT_APP_ROOT',
        'prod':'GT_PACKAGE_ROOT',
        'dev':'GT_DEV_ROOT',
        'cfg':'GT_CONFIG_ROOT',
        'bld':'GT_BUILD_ROOT'
                 }
    _valid_version = re.compile(r"(\d+\.\d+\.\d+|dev)")
    _config_fields = ['name','root','version','platform','type']
    _valid_build = re.compile(r"^rc(\d+?)")
    _buildlog = "buildlog.json"
    _release_notes = "release_notes.json"
    
    def __init__(self, **kw):
        self.name = None
        self.platform = []
        self.root = u"prod"
        self.type = u"module"
        self._refresh = False
        if kw.get("name", None):
            self.__dict__ .update(kw.copy())
        else:
            raise BasePkgInitError("Insufficient Arguments!!")
        
        if kw.get('version', None):
            self.__dict__.pop('version')
        self._version = kw.get('version',u"0.0.0")
        self._root_path = None
        self._deploy_root = None
        self._path = None
        
        
        #allow root to be an abs path
        if not os.path.exists(os.path.abspath(self.root)):
            try:
                evar = BasePkg._root_map[self.root]
            except Exception as err:
                raise BasePkgInitError("Unknown package type: [{}] !!".format(self.root))
    
        self._init_env()
    
    def _init_env(self):
        
        resolve.environment()
        for evar in self._required_env:
            try:
                os.environ[evar]
            except Exception as err:
                raise BasePkgEnvError("Required environment variable [{}] not found!!".format(evar))
                
    def __str__(self):
        data = "{}(".format(self.__class__.__name__)
        for i in inspect.getmembers(self):
            if not i[0].startswith('_'):
                if not inspect.ismethod(i[1]):
                    data += "{}={}, ".format(i[0],i[1])
        return "{})".format(data)
    
    def refresh(self):
        '''
        re-cache ineternal data
        '''
        self._refresh = True
        for i in inspect.getmembers(self):
            if not i[0].startswith('_'):
                if not inspect.ismethod(i[1]):
                    eval("self.{}, ".format(i[0]))
        self._refresh = False
     
    def dump(self):
        '''
        dump object as json
        '''
        data = self.__dict__.copy()
        data['version'] = data.pop("_version")
        if not data['platform']:
            data.pop('platform')
        if self._config_fields:
            _skip = set(data.keys()) - set(self._config_fields)
            for attr in _skip:
                data.pop(attr)
        
        return data
    
    @property
    def version(self):
        '''
        package version
        '''
        if not self._version:
            self._version = "0.0.0"
        return self._version
    
    @version.setter
    def version(self,value):
        '''
        package version setter
        '''
        if self._version != value:
            if not self._valid_version.match(value):
                raise BasePkgVersionError("Invalid version format [{}]".format(value))
            self._version = value
    
    @property
    def path(self):
        '''
        package path
        '''
        if not self._path or self._refresh:
            #use raw path
            if os.path.exists(os.path.abspath(self.root)) and "/" in self.root:
                self._path  = os.path.abspath(self.root)
                
            #package based resolve
            else:
                
                #use dev root
                if self.version == 'dev':
                    self._path  = os.path.join(os.environ.get(self._root_map.get('dev')), self.name)
                #use build root
                elif 'rc' in self.version:
                    self._path  = os.path.join(os.environ.get(self._root_map.get('bld')), self.name)  
                else:
                    self._path  = os.path.join(self.root_path)
                    #add name and version identifier
                    if self.root not in ('cfg') and not os.path.exists(self.root):
                        self._path  = os.path.join(self._path, self.name, self.version) 
                
                #add platform if needed
                current_platform = self._platform_map.get(platform.system().lower(),platform.system().lower())
                if self.platform and current_platform in self.platform:
                    self._path  = os.path.join(self._path , current_platform)
            self._path = os.path.normpath(self._path)
        return self._path
    
    @property
    def root_path(self):
        '''
        package root path
        '''
        if not self._root_path or self._refresh:
            self._root_path = os.environ.get(self._root_map.get(self.root))
        return self._root_path
    
    @property
    def deploy_root(self):
        '''
        package deploy path
        '''
        if not self._deploy_root or self._refresh:
            self._deploy_root = self.root_path
            if self.root == 'cfg':
                self._deploy_root = os.path.join(self._deploy_root,'staging')
            self._deploy_root = os.path.join(self._deploy_root, self.name)
            self._deploy_root = os.path.normpath(self._deploy_root)
        
        return self._deploy_root
    
    @property
    def build_root(self):
        pkg_path = os.environ.get("GT_BUILD_ROOT")
        if self.root == 'dev':
            pkg_path = posixpath.join(self._root_map.get(self.root), 'builds')
        pkg_path = posixpath.join(pkg_path, self.name)
        if self.platform:
            pkg_path = posixpath.join(pkg_path, platform.system().lower())
        return os.path.normpath(pkg_path)

    @property
    def dev_root(self):
        current = self.version
        self.version='dev'
        dev_root = self.path
        self.version = current
        return dev_root


if __name__ == '__main__':
    from pprint import pprint as pp
    _BasePkg = BasePkg(name="test")
    print inspect.getmembers(_BasePkg)
    print _BasePkg
    _BasePkg.version = "1.0.0"
    print _BasePkg
    pp(_BasePkg.dump())