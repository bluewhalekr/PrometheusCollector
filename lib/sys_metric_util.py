import os


def get_folder_count(pid: str) -> int:
    path = f"/proc/{pid}/fd"
    folder_count = sum([len(folder) for r, d, folder in os.walk(path)])
    return folder_count


def get_fd_cnt_by_ps():
    import subprocess
    cmd = "/usr/bin/ps -adef|/usr/bin/grep -Ewv 'grep|ps '|/usr/bin/awk '{print $2}'"
    pids_str = subprocess.check_output(cmd, shell=True, text=True)
    pids = pids_str.split("\n")
    folder_num = 0
    for pid in pids:
        if len(pid) > 0 and pid.isdecimal():
            folder_num += get_folder_count(pid)
    
    return folder_num


def get_fd_cnt_by_lsof():
    import subprocess
    return subprocess.check_output("/usr/bin/lsof|/usr/bin/grep -Ewv 'grep|lsof'|/usr/bin/wc -l", shell=True, text=True)
