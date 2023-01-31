from . import cache
from . import tarcopy
from . import bldenv
from . import consts
from . import perms

import os
import sys
from urllib.parse import urlparse
from pathlib import Path
from distutils.dir_util import copy_tree
import shutil
import subprocess

def read_file(path):
    f = open(path)
    s = f.read()
    f.close()
    return s

def write_file(path, data):
    f = open(path, 'w')
    f.write(data)
    f.close()

def is_url(url):
    r = urlparse(url)

    return r.netloc != '' and r.scheme != ''

def manifest(root_dir):
    result = []

    for dir_path, dir_names, file_names in os.walk(root_dir):
        for file_name in file_names:
            result.append(os.path.join(dir_path, file_name))
        for dir_name in dir_names:
            result.append(os.path.join(dir_path, dir_name))

    result = [Path('/') / Path(r).relative_to(root_dir) for r in result]

    return result

def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

class Source:
    """A class that defines a source. A
       source contains a src path indicating
       where the source is located (it can be
       local or an URL) and a dst indicating
       where the source should be placed within
       the temporary build directory"""

    def __init__(self, line):
        components = line.split()

        # Get the src component
        self.src = components[0]
        
        # Get the dst component
        self.dst = components[1]

    def __str__(self):
        return '%s -> %s' % (self.src, self.dst)

    def __repr__(self):
        return str(self)

    def fetch(self, dst):
        cache_name = self.src.split('/')[-1]

        path = ''
        if is_url(self.src):
            path = cache.get(self.src, cache_name)
        else:
            path = self.src

        path = Path(path).resolve()
        dst = Path(dst).resolve()
        dst.mkdir(parents=True, exist_ok=True)

        if path.is_dir():
            copy_tree(str(path), str(dst))
        else:
            tarcopy.copy(path, dst)

class Package:
    """A class that defines what a package is,
       in the case of edel, this corresponds to
       a set of files in the package directory"""

    def __init__(self, path, repo=None):
        path = Path(path).resolve()

        self.name = path.name
        self.repo = repo

        if self.repo:
            self.repo.cache[self.name] = self

        # Build up the different possible paths
        # used by the packaging system
        self.paths = {
            # Path of the package itself
            'pkg': path,

            # Path of the sources file:
            # it holds the sources of the package
            'sources': path / 'sources',

            # Path to the package build script
            'build': path / 'build',

            # Path to the version file
            'version': path / 'version',

            # Path to the depends file of the
            # package listing its different
            # dependencies
            'depends': path / 'depends',

            # Path to the manifest file, it lists
            # all the paths created by the installed
            # package. It would typically be created
            # once the package is built
            'manifest': path / 'manifest',

            # Path to the checksum file, containing the
            # checksum of the different sources if
            # applicable
            'checksum': path / 'checksum',

            # Path to a file that is present if the package
            # was explicitly installed
            'explicit': path / 'explicit'
        }

        # Sources object of the package
        self._sources = None

        # Version object of the package
        self._version = None
        
        # Depends object of the package
        self._depends = None

        # Manifest of the package
        self._manifest = None

        # The _version and _sources variables are lazily evaluated
        # for performance, respectively by the sources and version
        # methods

    def __repr__(self):
        return self.name

    def sources(self):
        """Returns the list of sources"""

        if self._sources:
            return self._sources
        
        sources = read_file(self.paths['sources']).strip()

        self._sources = [Source(line) for line in sources.splitlines()]

        return self._sources

    def version(self):
        """Returns the version"""

        if self._version:
            return self._version

        self._version = read_file(self.paths['version']).strip()

        return self._version

    def depends(self):
        """Returns the list of dependencies
           of the package in the form of a list
           of strings"""

        if self._depends:
            return self._depends

        if not self.paths['depends'].exists():
            return None

        self._depends = read_file(self.paths['depends']).splitlines()

        return self._depends

    def manifest(self):
        """Returns the list of files in the proto"""

        if self._manifest:
            return self._manifest

        if not self.paths['manifest'].exists():
            return None

        manifest = read_file(self.paths['manifest']).splitlines()
        self._manifest = [Path(man) for man in manifest]

        return self._manifest

    def timestamp(self):
        timestamp = 0

        for path in self.paths.values():
            if not path.exists():
                continue

            ts = os.path.getmtime(path)
            if ts > timestamp:
                timestamp = ts

        return timestamp

    def is_more_recent_than(self, other):
        if self.version() == other.version():
            return False

        return self.timestamp() > other.timestamp()

    def mark_explicit(self):
        """Marks the package as explicitly installed"""

        if not self.installed():
            return

        perms.elevate()

        self.paths['explicit'].touch()

        perms.drop()

    def explicit(self):
        """Returns whether the package is explicitly
           installed"""

        return self.paths['explicit'].exists()

    def unmark_explicit(self):
        """Unmarks the package as explicitly installed"""

        if not self.installed():
            return

        perms.elevate()
        
        self.paths['explicit'].unlink(missing_ok=True)

        perms.drop()

    def build(self):
        pcwd = os.getcwd()
        
        os.chdir(self.paths['pkg'])

        perms.drop()
        bld = bldenv.Bldenv()

        pid = os.fork()
        if pid == 0:
            perms.drop_totally()
        
            self.build0(bld)
            self.build1(bld)
            sys.exit(0)
        else:
            os.wait()

        pkg = self.install(bld)

        os.chdir(pcwd)

        return pkg

    def installed(self):
        """Checks whether the current package is
           an installed package"""
        
        return self.paths['manifest'].exists()

    def get_installed(self):
        """Gets the installed version of the package
           if it exists"""
        
        if self.installed():
            return self
        else:
            return consts.INSTALLED.resolve(self.name)

    def build0(self, bld):
        """Prepares the build environment, by notably
           fetching the sources"""

        for source in self.sources():
            dst = source.dst.replace('@', str(bld.proto)).replace('$', str(bld.build))
            
            source.fetch(dst)

    def build1(self, bld):
        """Completes the build environment, readying it for
           installation, by executing the build script"""

        if self.paths['build'].exists():
            subprocess.call(['sh', self.paths['build'], bld.proto], cwd=bld.build)

        man = [str(p) for p in manifest(bld.proto)]
        man = '\n'.join(man)
        write_file(bld.manifest, man)
    
    def install(self, bld):
        """Installs a package based on its completed
           build environment"""


        # Copy the package
        pkg = consts.INSTALLED.create(self.name)

        
        perms.elevate()

        copy_tree(str(self.paths['pkg']), str(pkg.paths['pkg']))

        # Add the manifest
        shutil.copy(bld.manifest, pkg.paths['manifest'])
        
        # Copy the proto into the root
        copy_tree(str(bld.proto), str(consts.ROOT))

        # FIXME: support conflicts

        perms.drop()

        return pkg


    def uninstall(self):
        """Uninstalls a package"""

        if not self.installed():
            return

        
        # Get a reversed version of the manifest
        manifest = self.manifest().copy()
        manifest.reverse()

        # List files installed in root
        manifest = [consts.ROOT / man.relative_to('/') for man in manifest]

        perms.elevate()

        # Remove files and directories
        for man in manifest:
            if man.is_dir():
                try:
                    man.rmdir()
                except:
                    pass
            else:
                man.unlink(missing_ok=True)

        shutil.rmtree(self.paths['pkg'])

        perms.drop()

    def make_collective_build_plan(pkgs, plan=[]):
        for pkg in pkgs:
            plan.extend(pkg.make_build_plan())
            plan = f7(plan)

        return plan

    def make_build_plan(self, plan=[]):
        if self in plan:
            return plan

        installed = self.get_installed()

        if not self.installed() and installed and not self.is_more_recent_than(installed):
            return plan

        if self.depends():
            for dep in self.depends():
                repo = self.repo or consts.REPOS 
                dep = repo.resolve(dep)
                dep.make_build_plan(plan=plan)

        plan.append(self)

        return plan
