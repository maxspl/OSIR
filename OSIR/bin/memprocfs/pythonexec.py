try:
    print("")
    print("3. Copy CSV files from forensic mode (if enabled)")
    print("-------------------------------------------------")
    import os
    dst_path_base = '/tmp/' if os.sep == '/' else 'C:\\Temp\\'
    vfs_files = vmm.vfs.list("/forensic/csv/")
    for vfs_file in vfs_files:
        if not vfs_files[vfs_file]['f_isdir']:
            offset = 0
            vfs_path = "/forensic/csv/" + vfs_file
            dst_path = dst_path_base + 'memprocfs_pythonexec_example_' + vfs_file
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
            dst_path = dst_path_base + 'memprocfs_pythonexec_example_' + vfs_file
            print("copy file '%s' to '%s'" % (vfs_path, dst_path))
            with open(dst_path, "wb") as file:
                while offset < vfs_files[vfs_file]['size']:
                    chunk = vmm.vfs.read(vfs_path, 0x00100000, offset)
                    offset += len(chunk)
                    file.write(chunk)
    import sys
    for i, arg in enumerate(sys.argv):
        print(f"Argument {i}: {arg}")
except Exception as e:
    print("memprocfs_pythonexec_example.py: exception: " + str(e))
