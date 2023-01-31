from pkg import consts

def autoremove(argv):
    orphaned = consts.INSTALLED.orphaned()

    if len(orphaned) == 0:
        print('edel: nothing to do')
        return

    print('edel: the following packages will be removed:')
    for pkg in orphaned:
        print('\t%s' % pkg.name)
    print('edel: proceed? [y/N] ', end='')
    
    response = input().lower()
    
    if response != 'y':
        return

    for pkg in orphaned:
        print('edel: removing %s' % pkg.name)
        pkg.uninstall()

    
