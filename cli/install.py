from pkg import consts
from pkg import package
import time


def install(argv):
    pkgs = []
    
    for pkgname in argv[1:]:
        pkg = consts.REPOS.resolve(pkgname)
        
        if not pkg:
            print('edel: no such package %s found' % pkgname)
            return

        pkg_installed = pkg.get_installed()
        if pkg_installed and not pkg.is_more_recent_than(pkg_installed):
            print('edel: package %s marked as explicit' % pkgname)
            pkg_installed.mark_explicit()
            continue

        pkgs.append(pkg)

    plan = package.Package.make_collective_build_plan(pkgs)

    for pkg in plan:
        print('edel: start build of %s...' % pkg.name)

        begin = time.time()

        pkg_installed = pkg.build()
        if pkg in pkgs:
            pkg_installed.mark_explicit()

        end = time.time()
        
        minutes, seconds = divmod(end - begin, 60)
        
        print('edel: finished build of %s in %d:%d' % (pkg.name, minutes, seconds))
