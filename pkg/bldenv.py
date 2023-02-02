from . import consts

from pathlib import Path
import shutil
import os

class Bldenv:
    def __init__(self):
        self.path = consts.CACHE / ('bldenv-%s-%s' % (consts.PID, consts.bldid()))

        self.proto = self.path / 'proto'
        self.build = self.path / 'build'
        self.manifest_path = self.path / 'manifest'

        self._manifest = None

        self.proto.mkdir(parents=True, exist_ok=True)
        self.build.mkdir(parents=True, exist_ok=True)

    def manifest(self):
        if self._manifest:
            return self._manifest
        
        result = []
        
        for dir_path, dir_names, file_names in os.walk(self.proto):
            dir_path = Path('/') / Path(dir_path).relative_to(self.proto)
            
            for dir_name in dir_names:
                result.append(dir_path / dir_name)

            for file_name in file_names:
                result.append(dir_path / file_name)
        
        self._manifest = result

        return self._manifest

    def remove(self):
        shutil.rmtree(self.path)
