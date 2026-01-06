import os
import json


def process_csv_add_columns(csv_path):
    import csv

    def trace_ancestry(pid, ppid_map):
        visited = set()
        path = [pid]
        current = pid
        while current in ppid_map and ppid_map[current] != "0" and ppid_map[current] != current:
            parent = ppid_map[current]
            if parent in visited:
                break
            visited.add(parent)
            path.append(parent)
            current = parent
        path = list(reversed(path))
        root_pid = path[0]
        level = len(path) - 1
        return root_pid, level, " > ".join(path)

    try:
        with open(csv_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            processes = list(reader)
            header = reader.fieldnames or []

        if not processes:
            return

        # Build PID to PPID map
        ppid_map = {
            proc['PID']: proc['PPID']
            for proc in processes
            if proc.get('PID') and proc.get('PPID')
        }

        # Enrich each process
        for proc in processes:
            pid = proc.get('PID')
            if pid:
                root_pid, level, chain = trace_ancestry(pid, ppid_map)
                proc['root_pid'] = root_pid
                proc['level'] = str(level)
                proc['process_chain'] = chain

        # Update header if necessary
        for new_field in ['root_pid', 'level', 'process_chain']:
            if new_field not in header:
                header.append(new_field)

        # Write updated CSV
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=header, quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            for proc in processes:
                writer.writerow(proc)

        print(f"Enhanced process tree written to: {csv_path}")

    except Exception as e:
        print("process_csv_add_columns: exception: " + str(e))


def process_sysinfo(path_sysinfo):
    import re
    import os
    import json
    with open(path_sysinfo, "r", encoding="utf-8") as file:
        input_text = file.read()
    write_path = os.path.join(os.path.dirname(path_sysinfo), "sysinfo.json")
    system_info = {
        "WindowsInformation": {},
        "HardwareInformation": {},
        "Users": [],
        "ProcessInformation": {},
        "NetworkInterfaces": [],
        "MemProcFSInformation": {}
    }

    current_section = None
    current_iface = None

    for line in input_text.splitlines():
        line = line.strip()
        if not line:
            continue

        # Sections
        if re.match(r"^Windows Information:$", line):
            current_section = "WindowsInformation"
            continue
        elif re.match(r"^Hardware Information:$", line):
            current_section = "HardwareInformation"
            continue
        elif re.match(r"^Process Information:$", line):
            current_section = "ProcessInformation"
            continue
        elif re.match(r"^Network Interfaces:$", line):
            current_section = "NetworkInterfaces"
            continue
        elif re.match(r"^MemProcFS Information:$", line):
            current_section = "MemProcFSInformation"
            continue
        elif re.match(r"^Users:$", line):
            current_section = "Users"
            continue

        if current_section == "NetworkInterfaces" and re.match(r"^Interface #\d+:", line):
            current_iface = {}
            system_info["NetworkInterfaces"].append(current_iface)
            continue

        if current_section == "Users":
            match = re.match(r"(\S+)\s+\(([^)]+)\)", line)
            if match:
                system_info["Users"].append({
                    "Username": match.group(1),
                    "SID": match.group(2)
                })
            continue

        if ":" in line and current_section in system_info:
            key, value = map(str.strip, line.split(":", 1))
            if current_section == "NetworkInterfaces" and current_iface is not None:
                current_iface[key] = value
            elif isinstance(system_info[current_section], dict):
                system_info[current_section][key] = value

    with open(write_path, "w", encoding="utf-8") as f:
        for section, content in system_info.items():
            if isinstance(content, dict):
                for key, value in content.items():
                    json.dump({
                        "section": section,
                        "key": key,
                        "value": value
                    }, f)
                    f.write("\n")
            elif isinstance(content, list):
                for entry in content:
                    entry_line = entry.copy()
                    entry_line["section"] = section
                    json.dump(entry_line, f)
                    f.write("\n")

    print("systeminformations.jsonl processed and written to: " + write_path)


def copy_vfs_files(vmm, output_dir, vfs_path):
    import os
    vfs_files = vmm.vfs.list(vfs_path)
    for vfs_file in vfs_files:
        if not vfs_files[vfs_file]['f_isdir']:
            offset = 0
            dst_path = os.path.join(output_dir, vfs_file)
            full_vfs_path = os.path.join(vfs_path, vfs_file).replace('\\', '/')
            # print("copy file '%s' to '%s'" % (full_vfs_path, dst_path))
            with open(dst_path, "wb") as file:
                while offset < vfs_files[vfs_file]['size']:
                    chunk = vmm.vfs.read(full_vfs_path, 0x00100000, offset)
                    offset += len(chunk)
                    file.write(chunk)


def copy_vfs_all(vmm, dst_path_base, vfs_path):
    import os
    stack = [(vfs_path, dst_path_base)]
    
    while stack:
        vfs_dir, local_dir = stack.pop()
        vfs_files = vmm.vfs.list(vfs_dir)
        try:
            os.makedirs(local_dir, exist_ok=True)
        except Exception as e:
            print(f"Error while creating dir {local_dir}. Error : {str(e)}")
            continue

        for vfs_file, entry in vfs_files.items():
            vfs_full_path = os.path.join(vfs_dir, vfs_file)
            dst_full_path = os.path.join(local_dir, vfs_file)

            if entry['f_isdir']:
                stack.append((vfs_full_path, dst_full_path))
            else:
                offset = 0
                # print("copy file '%s' to '%s'" % (vfs_full_path, dst_full_path))
                try:
                    with open(dst_full_path, "wb") as file:
                        while offset < entry['size']:
                            chunk = vmm.vfs.read(vfs_full_path, 0x00100000, offset)
                            offset += len(chunk)
                            file.write(chunk)
                except Exception as e:
                    print(f"Error while copying file. Error : {str(e)}")


def build_pid_to_name_map_from_csv(process_csv_path: str) -> dict:
    """
    Reads process.csv and returns { "1234": "explorer.exe", ... }.

    This tries multiple likely column names so it works even if the CSV schema differs.
    """
    import os
    import csv

    if not os.path.isfile(process_csv_path):
        print(f"build_pid_to_name_map_from_csv: '{process_csv_path}' not found")
        return {}

    # Common column candidates seen in process listings
    name_keys = [
        "ImageFileName", "ImageName", "ProcessName", "Name",
        "process_name", "image", "comm", "Executable", "ExeFile", "Path"
    ]

    pid_to_name = {}
    try:
        with open(process_csv_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pid = (row.get("PID") or "").strip()
                if not pid:
                    continue

                proc_name = ""
                for k in name_keys:
                    v = row.get(k)
                    if v and str(v).strip():
                        proc_name = str(v).strip()
                        break

                # If we got a full path, keep only basename (nice dir names)
                if proc_name and ("/" in proc_name or "\\" in proc_name):
                    proc_name = os.path.basename(proc_name)

                pid_to_name[pid] = proc_name or "unknown"

    except Exception as e:
        print(f"build_pid_to_name_map_from_csv: exception: {str(e)}")
        return {}

    return pid_to_name


def copy_pe_modules_per_process(vmm, dst_path_base: str, pid_to_name: dict,
                                vfs_pid_root: str = "/pid",
                                dst_subdir: str = "pe_files_extracted"):
    """
    For each process directory in /pid/<pid>/files/modules, copy module files into:
      <dst_path_base>/<dst_subdir>/<pid>-<process_name>/
    """
    import os 
    
    def _sanitize_for_dirname(name: str) -> str:
        bad = '<>:"/\\|?*\n\r\t'
        out = "".join("_" if c in bad else c for c in (name or "").strip())
        out = out.strip(" .")
        return out or "unknown"

    out_root = os.path.join(dst_path_base, dst_subdir)
    os.makedirs(out_root, exist_ok=True)

    try:
        pid_entries = vmm.vfs.list(vfs_pid_root)
    except Exception as e:
        print(f"copy_pe_modules_per_process: cannot list '{vfs_pid_root}': {str(e)}")
        return

    for pid_str, entry in pid_entries.items():
        if not entry.get("f_isdir"):
            continue
        if not str(pid_str).isdigit():
            continue

        proc_name = _sanitize_for_dirname(pid_to_name.get(str(pid_str), "unknown"))
        dst_dir = os.path.join(out_root, f"{proc_name}-{pid_str}")

        modules_vfs_dir = f"{vfs_pid_root}/{pid_str}/files/modules"
        try:
            modules_entries = vmm.vfs.list(modules_vfs_dir)
        except Exception as e:
            # Not all PIDs will have modules or may be inaccessible; just skip
            print(f"copy_pe_modules_per_process: cannot list '{modules_vfs_dir}': {str(e)}")
            continue

        try:
            os.makedirs(dst_dir, exist_ok=True)
        except Exception as e:
            print(f"copy_pe_modules_per_process: cannot create '{dst_dir}': {str(e)}")
            continue
            
        for filename, finfo in modules_entries.items():
            if finfo.get("f_isdir"):
                continue

            src_vfs_path = f"{modules_vfs_dir}/{filename}"
            dst_path = os.path.join(dst_dir, filename)

            offset = 0
            size = int(finfo.get("size", 0) or 0)
            # print(f"copy module '{src_vfs_path}' -> '{dst_path}'")

            try:
                with open(dst_path, "wb") as out_f:
                    while offset < size:
                        chunk = vmm.vfs.read(src_vfs_path, 0x00100000, offset)
                        if not chunk:
                            break
                        offset += len(chunk)
                        out_f.write(chunk)
            except Exception as e:
                print(f"copy_pe_modules_per_process: error copying '{src_vfs_path}': {str(e)}")


def copy_minidumps_per_process(vmm, dst_path_base: str, pid_to_name: dict,
                               vfs_pid_root: str = "/pid",
                               dst_subdir: str = "minidumps",
                               minidump_filename: str = "minidump.dmp"):
    """
    For each process directory in /pid/<pid>/minidump, copy minidump.dmp into:
      <dst_path_base>/<dst_subdir>/<process_name>-<pid>/minidump.dmp
    """
    import os

    def _sanitize_for_dirname(name: str) -> str:
        bad = '<>:"/\\|?*\n\r\t'
        out = "".join("_" if c in bad else c for c in (name or "").strip())
        out = out.strip(" .")
        return out or "unknown"

    out_root = os.path.join(dst_path_base, dst_subdir)
    os.makedirs(out_root, exist_ok=True)

    try:
        pid_entries = vmm.vfs.list(vfs_pid_root)
    except Exception as e:
        print(f"copy_minidumps_per_process: cannot list '{vfs_pid_root}': {str(e)}")
        return

    for pid_str, entry in pid_entries.items():
        if not entry.get("f_isdir"):
            continue
        if not str(pid_str).isdigit():
            continue

        proc_name = _sanitize_for_dirname(pid_to_name.get(str(pid_str), "unknown"))
        dst_dir = os.path.join(out_root, f"{proc_name}-{pid_str}")

        minidump_vfs_dir = f"{vfs_pid_root}/{pid_str}/minidump"
        src_vfs_path = f"{minidump_vfs_dir}/{minidump_filename}"

        # Ensure the minidump directory exists and contains the file
        try:
            md_entries = vmm.vfs.list(minidump_vfs_dir)
        except Exception:
            # No minidump dir for this PID
            continue

        finfo = md_entries.get(minidump_filename)
        if not finfo or finfo.get("f_isdir"):
            continue

        try:
            os.makedirs(dst_dir, exist_ok=True)
        except Exception as e:
            print(f"copy_minidumps_per_process: cannot create '{dst_dir}': {str(e)}")
            continue

        size = int(finfo.get("size", 0) or 0)
        offset = 0
        dst_path = os.path.join(dst_dir, minidump_filename)

        try:
            with open(dst_path, "wb") as out_f:
                while offset < size:
                    chunk = vmm.vfs.read(src_vfs_path, 0x00100000, offset)
                    if not chunk:
                        break
                    offset += len(chunk)
                    out_f.write(chunk)
        except Exception as e:
            print(f"copy_minidumps_per_process: error copying '{src_vfs_path}': {str(e)}")


try:
    print("")
    print("Copy CSV files from forensic mode (if enabled)")
    print("-------------------------------------------------")
    dst_path_base = '{output_dir}' 

    print(f"copying file from /forensic/csv to {dst_path_base}")
    copy_vfs_files(vmm, dst_path_base, "/forensic/csv/")

    print(f"copying file from /forensic/json to {dst_path_base}")
    copy_vfs_files(vmm, dst_path_base, "/forensic/json/")

    print(f"copying file from /sys/sysinfo to {dst_path_base}")
    copy_vfs_files(vmm, dst_path_base, "/sys/sysinfo/")

    print(f"copying file from /forensic/files to {dst_path_base}/restore_fs-ram")
    copy_vfs_all(vmm, os.path.join(dst_path_base, "restore_fs-ram"), "/forensic/files/")

    process_csv_path = None
    for file in os.listdir(dst_path_base):
        if file == 'process.csv':
            process_csv_path = os.path.join(dst_path_base, file)
            print("process file '%s'" % file)
            process_csv_add_columns(process_csv_path)
        elif file == 'sysinfo.txt':
            print("systeminfo file '%s'" % file)
            process_sysinfo(os.path.join(dst_path_base, file))
            os.remove(os.path.join(dst_path_base, file))

    if process_csv_path:
        pid_to_name = build_pid_to_name_map_from_csv(process_csv_path)
    else:
        pid_to_name = {}

    print(f"copying file from /pid/<pid>/files/modules to {dst_path_base}/pe_files_extracted")
    copy_pe_modules_per_process(vmm, dst_path_base, pid_to_name)
    
    print(f"copying minidumps from /pid/<pid>/minidump/minidump.dmp to {dst_path_base}/minidumps")
    copy_minidumps_per_process(vmm, dst_path_base, pid_to_name)

except Exception as e:
    print("memprocfs_pythonexec_example.py: exception: " + str(e))