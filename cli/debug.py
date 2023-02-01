from pkg import consts

def debug(argv):
    print('EDEL_ROOT=%s' % consts.ROOT)
    print('EDEL_REPOS=%s' % ':'.join(consts.REPOS_PATHS))
    print('EDEL_INSTALLED=%s' % consts.INSTALLED_PATH)
    print('EDEL_PKG_COUNT=%s' % consts.REPOS.count())
    print('EDEL_INSTALLED_PKG_COUNT=%s' % consts.INSTALLED.count())
    print(consts.REPOS.packages())
