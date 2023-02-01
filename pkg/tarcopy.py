from pathlib import Path
import tarfile

def copy(src, dst):
    src = Path(src).resolve()
    dst = Path(dst).resolve()

    # Open the tarfile and get a list of members
    tar = tarfile.open(src, 'r:*')
    members = tar.getmembers()

    # Strip the first component of the path for each member
    for member in members:
        member.name = member.name.split('/', 1)[-1]

        if member.linkname:
            member.linkname = member.linkname.split('/', 1)[-1]

    dst.mkdir(parents=True, exist_ok=True)

    # Extract the tarball to the current directory
    tar.extractall(path=dst, members=members[1:])
    tar.close()
