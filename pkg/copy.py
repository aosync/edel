from pathlib import Path
import shutil

def nature(path):
    path = Path(path)

    if path.is_symlink():
        return 'symlink'

    if not path.exists():
        return None

    if path.is_dir():
        return 'dir'

    return 'file'

def copy(item, ditem, force=False, aux=[], dry=False):
    item = Path(item)
    ditem = Path(ditem)

    if nature(ditem):
        if nature(item) != nature(ditem):
            aux.append((item, ditem))
        elif nature(item) == 'dir':
            copytree(item, ditem, force=force, aux=aux, dry=dry)
        elif force and not dry:
            shutil.copy2(item, ditem, follow_symlinks=False)
        else:
            aux.append((item, ditem))
    elif not dry:
        if nature(item) == 'dir':
            ditem.mkdir(parents=True)
            copytree(item, ditem, force=force, aux=aux, dry=dry)
        else:
            shutil.copy2(item, ditem, follow_symlinks=False)

def copytree(src, dst, force=False, aux=[], dry=False):
    src = Path(src)
    dst = Path(dst)

    for item in src.iterdir():
        ditem = dst / item.relative_to(src)
        copy(item, ditem, force=force, aux=aux, dry=dry)

def remove(dst):
    dst = Path(dst)
    
    if dst.is_dir():
        try:
            dst.rmdir()
        except:
            dst.unlink(missing_ok=True)
    else:
        dst.unlink(missing_ok=True)
