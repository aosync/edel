import os
from pwd import getpwnam

ELEVATED = True

BLD_USER = getpwnam('bld')
BLD_ENV = {
    'USER': 'bld',
    'HOME': BLD_USER.pw_dir
}
PREV_ENV = {}
PREV_UID = os.getuid()
PREV_GID = os.getgid()

def elevate():
    global ELEVATED, PREV_UID, PREV_GID, BLD_ENV, PREV_ENV

    if PREV_UID != 0 or ELEVATED:
        return

    os.seteuid(PREV_UID)
    os.setegid(PREV_GID)

    for key in BLD_ENV.keys():
        os.environ[key] = PREV_ENV[key]
        del PREV_ENV[key]

    ELEVATED = True

def drop():
    global ELEVATED, PREV_UID, PREV_GID, BLD_ENV, PREV_ENV

    if PREV_UID != 0 or not ELEVATED:
        return
    
    for key, value in BLD_ENV.items():
        PREV_ENV[key] = os.environ[key]
        os.environ[key] = value

    os.setegid(BLD_USER.pw_gid)
    os.seteuid(BLD_USER.pw_uid)

    ELEVATED = False

def drop_totally():
    global ELEVATED, PREV_UID, PREV_GID, BLD_ENV, PREV_ENV

    if PREV_UID != 0:
        return

    if ELEVATED:
        drop()

    os.seteuid(PREV_UID)
    os.setegid(PREV_GID)

    os.setgid(BLD_USER.pw_gid)
    os.setuid(BLD_USER.pw_uid)
