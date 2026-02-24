import os
import subprocess
from eliot import start_action, to_file, log_message
from wit_pytools.config import readconfig


def getncroot():
    config = readconfig()
    ncdir = config['WIT PYTOOLS'].get('ncdir')
    return ncdir


def getncfilename(filename):
    return os.path.basename(filename)


# Returns the nextcloud relative file path from an absolute path without leading slash
def getncpath(abspath):
    import re
    ncpath = re.sub(r'^.*?/data', '', abspath)
    ncpath = ncpath.lstrip('/')
    return ncpath


# Returns the nextcloud relative directory path from an absolute path without leading slash
def getncdir(abspath):
    import re
    ncpath = re.sub(r'^.*?/data', '', abspath)
    ncpath = ncpath.lstrip('/')
    return os.path.dirname(ncpath)


def _occ_base():
    """
    Builds the occ base command dynamically from config
    """
    ncroot = getncroot()
    return f'php {ncroot}/occ'


def ncdelfile(ncfile):
    with start_action(action_type=f"occ delete file {ncfile}"):
        try:
            subprocess.run(
                f'{_occ_base()} files:delete "{ncfile}"',
                capture_output=True,
                shell=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            log_message(
                f"Delete warning: stdout={e.stdout}, stderr={e.stderr}",
                level="WARNING"
            )


def ncmovefile(ncfile, ncdest):
    with start_action(action_type=f"ncmovefile: moving file {ncfile} to {ncdest}", level="INFO"):

        cmd = f'{_occ_base()} files:move "{ncfile}" "{ncdest}"'
        log_message(f"ncmovefile: running command: {cmd}", level="DEBUG")

        result = subprocess.run(
            cmd,
            capture_output=True,
            shell=True,
            text=True
        )

        if result.returncode != 0:
            log_message(
                f"ncmovefile ERROR: returncode={result.returncode}, stdout={result.stdout.strip()}, stderr={result.stderr.strip()}",
                level="ERROR"
            )
            raise RuntimeError(f"Nextcloud move failed for {ncfile} -> {ncdest}")
        else:
            log_message(
                f"ncmovefile OK: returncode={result.returncode}, stdout={result.stdout.strip()}",
                level="INFO"
            )


def ncscandir(targetdir):
    scan_result = subprocess.run(
        f'{_occ_base()} files:scan --path="{targetdir}" --quiet',
        capture_output=True,
        shell=True,
        text=True
    )

    if scan_result.returncode != 0:
        log_message(f"Warning: Folder rescan failed: {scan_result.stderr}", level="WARNING")


# Assigns a tag to a file or directory in Nextcloud
# nextcloud tag access levels: public, restricted, invisible
def nctagassign(target, tagname, access="public"):
    scan_result = subprocess.run(
        f'{_occ_base()} files:tag:assign --path="{target}" --tag="{tagname}" --access="{access}"',
        capture_output=True,
        shell=True,
        text=True
    )

    if scan_result.returncode != 0:
        log_message(f"Warning: Tag assignment failed: {scan_result.stderr}", level="WARNING")


def nctagremove(target, tagname):
    scan_result = subprocess.run(
        f'{_occ_base()} files:tag:remove --path="{target}" --tag="{tagname}"',
        capture_output=True,
        shell=True,
        text=True
    )

    if scan_result.returncode != 0:
        log_message(f"Warning: Tag removal failed: {scan_result.stderr}", level="WARNING")


def nctagedit(target, tagname, newtagname):
    scan_result = subprocess.run(
        f'{_occ_base()} files:tag:edit --path="{target}" --tag="{tagname}" --new-tag="{newtagname}"',
        capture_output=True,
        shell=True,
        text=True
    )

    if scan_result.returncode != 0:
        log_message(f"Warning: Tag edit failed: {scan_result.stderr}", level="WARNING")
