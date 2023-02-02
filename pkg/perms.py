import os
from pwd import getpwnam

# Get the BLD_USER from configuration
BLD_USER = getpwnam(os.environ.get('EDEL_BLD_USER', 'bld'))
BLD_ENV = {
    'USER': BLD_USER.pw_name,
    'HOME': BLD_USER.pw_dir
}

# Define the current user
PREV_ENV = {}
PREV_UID = os.getuid()
PREV_GID = os.getgid()

# Set the initial elevation level
ELEVATED = 1 if PREV_UID == 0 else 0

def elevate():
    """Make the environment and priviledge level root-like,
       meaning that we can for example start interacting
       with system files"""

    global ELEVATED, PREV_UID, PREV_GID, BLD_ENV, PREV_ENV

    # Ignore permission system if running as non-root
    if PREV_UID != 0:
        return

    # Saturate elevation level
    ELEVATED += 1
    
    # If already elevated, do nothing
    if ELEVATED > 1:
        return

    # Set euid and egid to the root ones
    os.seteuid(PREV_UID)
    os.setegid(PREV_GID)

    # Rebuild previous environment
    for key in BLD_ENV.keys():
        os.environ[key] = PREV_ENV[key]
        del PREV_ENV[key]

def drop(force=False):
    """Drop the effective priviledge to the level of the
       BLD_USER in a way that is reversible by elevate()"""

    global ELEVATED, PREV_UID, PREV_GID, BLD_ENV, PREV_ENV

    # Ignore permission system if running as non-root
    if PREV_UID != 0:
        return
    
    # If already dropped, don't do anything
    if ELEVATED == 0:
        return

    # Desaturate elevation level
    ELEVATED -= 1

    # If still greater than 0, do nothing
    if not force and ELEVATED > 0:
        return

    # Preserve previous environment and swap to unpriviledged environment
    for key, value in BLD_ENV.items():
        PREV_ENV[key] = os.environ[key]
        os.environ[key] = value

    # Set euid and egid to unpriviledged ones
    os.setegid(BLD_USER.pw_gid)
    os.seteuid(BLD_USER.pw_uid)

def drop_totally():
    """Irreversably and really drops priviledges to match
       the ones of the BLD_USER, this is very important to
       do when handling build scripts"""

    global ELEVATED, PREV_UID, PREV_GID, BLD_ENV, PREV_ENV

    # Ignore permission system if running as non-root
    if PREV_UID != 0:
        return

    # If elevated, then drop
    if ELEVATED > 0:
        drop(force=True)

    # Reset euid and egid to be able to set uid and gid
    os.seteuid(PREV_UID)
    os.setegid(PREV_GID)

    # Set real uid and gid to user, this is irreversible
    os.setgid(BLD_USER.pw_gid)
    os.setuid(BLD_USER.pw_uid)
