from . import package

from pathlib import Path

class Repository:
    def __init__(self, repos):
        self.cache = {}
        self.repos = [Path(repo).resolve() for repo in repos]
    
    def resolve(self, pkgname):
        if pkgname in self.cache:
            return self.cache[pkgname]

        if pkgname.startswith('.'):
            pkg = pkgname.resolve()
            if pkg.exists():
                return package.Package(pkg, repo=self)
        
        for repo in self.repos:
            pkg = repo / pkgname
            if pkg.exists():
                return package.Package(pkg, repo=self)

        return None

    def create(self, pkgname):
        """Creates a package in the first repository
           of the overlay, useful for the installation
           procedure"""

        pkg = self.repos[0] / pkgname
        pkg.mkdir(parents=True, exist_ok=True)
        
        return package.Package(pkg, repo=self)

    def lookup(self, path):
        """Finds the package that provides a file"""

        path = Path(path)

        for repo in self.repos:
            for pkgname in repo.iterdir():
                pkg = package.Package(pkgname)
                if not pkg.installed():
                    continue

                if not Path(path) in pkg.manifest():
                    continue

                return pkg
    
    def packages(self):
        """Returns all the packages in a repository"""

        pkgs = []
        for repo in self.repos:
            for pkgname in repo.iterdir():
                if pkgname.name in self.cache:
                    pkgs.append(self.cache[pkgname.name])
                
                pkgs.append(package.Package(pkgname, repo=self))

        return pkgs
    
    def count(self):
        """Returns the count of packages in a repository"""
        
        return len(self.packages())

    def orphaned(self):
        """Returns a list of orphaned packages: packages
           that are not explicitly installed and dependencies
           of no other package"""

        # Get all the installed packages
        pkgs = self.packages()

        # Get the explicitly installed packages
        explicits = [e for e in pkgs if e.explicit()]

        # Create the collective plan of all the explicits packages
        plan = package.Package.make_collective_build_plan(explicits)

        # Get orphaned packages as the packages not part of the plan
        orphaned = [o for o in pkgs if not o in plan]

        return orphaned

    def rdepends(self, pkg):
        """Returns all the packages that depend on given package"""
        
        # Get all the installed packages
        pkgs = self.packages()
        
        # Filter out given package in package list
        pkgs = [p for p in pkgs if p != pkg]

        # Find packages that depend on pkg
        rdepends = [p for p in pkgs if p.depends() and pkg.name in p.depends()]

        return rdepends
        
        
