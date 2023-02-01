from pkg import consts

def remove(argv):
    pkgs = []

    for pkgname in argv[1:]:
        pkg = consts.INSTALLED.resolve(pkgname)
        if not pkg:
            print('edel: no such package %s installed' % pkgname)
            return
        
        rdepends = consts.INSTALLED.rdepends(pkg)
        if rdepends:
            print('edel: package %s unmarked as explicit' % pkgname)
            pkg.unmark_explicit()
            continue

        pkgs.append(pkg)

    for pkg in pkgs:
        print('edel: removing %s' % pkg.name)
        pkg.uninstall()
