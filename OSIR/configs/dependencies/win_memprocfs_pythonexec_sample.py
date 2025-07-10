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
    import json
    import os
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

try:
    print("")
    print("3. Copy CSV files from forensic mode (if enabled)")
    print("-------------------------------------------------")
    dst_path_base = '{output_dir}' 
    vfs_files = vmm.vfs.list("/forensic/csv/")
    for vfs_file in vfs_files:
        if not vfs_files[vfs_file]['f_isdir']:
            offset = 0
            vfs_path = "/forensic/csv/" + vfs_file
            dst_path = os.path.join(dst_path_base, vfs_file)
            print("copy file '%s' to '%s'" % (vfs_path, dst_path))
            with open(dst_path, "wb") as file:
                while offset < vfs_files[vfs_file]['size']:
                    chunk = vmm.vfs.read(vfs_path, 0x00100000, offset)
                    offset += len(chunk)
                    file.write(chunk)

    vfs_files = vmm.vfs.list("/forensic/json/")
    for vfs_file in vfs_files:
        if not vfs_files[vfs_file]['f_isdir']:
            offset = 0
            vfs_path = "/forensic/json/" + vfs_file
            dst_path = os.path.join(dst_path_base, vfs_file)
            print("copy file '%s' to '%s'" % (vfs_path, dst_path))
            with open(dst_path, "wb") as file:
                while offset < vfs_files[vfs_file]['size']:
                    chunk = vmm.vfs.read(vfs_path, 0x00100000, offset)
                    offset += len(chunk)
                    file.write(chunk)

    vfs_files = vmm.vfs.list("/sys/sysinfo/")
    for vfs_file in vfs_files:
        if vfs_files[vfs_file]['f_isdir']:
            continue
        offset = 0
        vfs_path = "/sys/sysinfo/" + vfs_file
        dst_path = os.path.join(dst_path_base, vfs_file)
        print("copy file '%s' to '%s'" % (vfs_path, dst_path))
        with open(dst_path, "wb") as file:
            while offset < vfs_files[vfs_file]['size']:
                chunk = vmm.vfs.read(vfs_path, 0x00100000, offset)
                offset += len(chunk)
                file.write(chunk)
    


    for file in os.listdir(dst_path_base):
        if file == 'process.csv':
            print("process file '%s'" % file)
            process_csv_add_columns(os.path.join(dst_path_base, file))
        elif file == 'sysinfo.txt':
            print("systeminfo file '%s'" % file)
            process_sysinfo(os.path.join(dst_path_base, file))
            os.remove(os.path.join(dst_path_base, file))


except Exception as e:
    print("memprocfs_pythonexec_example.py: exception: " + str(e))
