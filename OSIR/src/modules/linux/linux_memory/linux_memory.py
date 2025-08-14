import sys
import os
from multiprocessing import Pool
import json
import subprocess
import argparse
from collections import Counter
FILE_PATH = os.path.dirname(__file__)
LIB_PATH = os.path.join(FILE_PATH, '..', 'lib')
DEFAULT_TOOLS_PATH = os.path.join(FILE_PATH, '..', 'tools')
if LIB_PATH not in sys.path:
    sys.path.insert(0, LIB_PATH)

all_volatility3_plugins = ["linux.pagecache.RecoverFs", "linux.bash.Bash","linux.envars.Envars", "linux.boottime.Boottime", "linux.capabilities.Capabilities", "linux.check_afinfo.Check_afinfo", "linux.check_creds.Check_creds", "linux.check_idt.Check_idt", "linux.check_modules.Check_modules", "linux.check_syscall.Check_syscall", "linux.ebpf.EBPF", "linux.elfs.Elfs", "linux.graphics.fbdev.Fbdev", "linux.hidden_modules.Hidden_modules", "linux.iomem.IOMem", "linux.ip.Addr", "linux.ip.Link", "linux.keyboard_notifiers.Keyboard_notifiers", "linux.kmsg.Kmsg", "linux.kthreads.Kthreads", "linux.library_list.LibraryList", "linux.lsmod.Lsmod", "linux.lsof.Lsof", "linux.malfind.Malfind", "linux.modxview.Modxview", "linux.mountinfo.MountInfo", "linux.netfilter.Netfilter", "linux.pagecache.Files", "linux.pagecache.InodePages", "linux.pidhashtable.PIDHashTable", "linux.proc.Maps", "linux.psaux.PsAux", "linux.pscallstack.PsCallStack", "linux.pslist.PsList", "linux.psscan.PsScan", "linux.pstree.PsTree", "linux.ptrace.Ptrace", "linux.sockstat.Sockstat", "linux.tracing.ftrace.CheckFtrace", "linux.tracing.perf_events.PerfEvents", "linux.tracing.tracepoints.CheckTracepoints", "linux.tty_check.tty_check", "linux.vmcoreinfo.VMCoreInfo"]


def argparse_setup():
    parser = argparse.ArgumentParser(
        description="Run Volatility3 plugins on a Linux memory dump.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-f", "--file", type=str, required=True,
        help="Path to the memory dump file"
    )
    parser.add_argument(
        "-o", "--output", type=str, default="output",
    help="Directory to save the results"
    )
    parser.add_argument(
        "-p", "--plugins", nargs='+', default=all_volatility3_plugins,
        help="List of plugins to run"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--list-plugins", action="store_true",
        help="List available Volatility3 plugins and exit"
    )
    parser.add_argument(
        "-t", "--tools", type=str, default=DEFAULT_TOOLS_PATH,
        help="Path to the tools directory containing volatility3 and dwarf2json"
    )
    parser.add_argument(
        "--auto-symbol", action="store_true",
        help="Automatically download and generate symbols for the memory dump"
    )
    parser.add_argument(
        "-s", "--symbols", type=str,
        help="Directory to save the downloaded symbols"
    )
    parser.add_argument(
        "-d", "--module-dir", type=str, default=f"{os.path.join(FILE_PATH)}",
        help="Path to the module directory of the script"
    )
    parser.add_argument(
        "--threads", type=int, default=4,
        help="Number of maximum processes to use for running plugins in a Pool (default: 4)"
    )
    parser.add_argument(
        "-b", "--banner-dir", type=str, default=DEFAULT_TOOLS_PATH,
        help="Path to the banners directory containing banners available and url to download symbols"
    )
    parser.add_argument(
        "--force-build", action="store_true",
        default=False,
        help="Force the building of symbols even if present in the json symbol table files"
    )

    args = parser.parse_args()

    if args.auto_symbol and not args.symbols:
        args.symbols = os.path.join(args.tools, "volatility3", "volatility3", "symbols", "linux")

    if args.list_plugins:
        print("Available plugins:")
        for plugin in all_volatility3_plugins:
            print(f"  - {plugin}")
        sys.exit(0)


    return args

args = argparse_setup()
# Allow shortened plugin names
plugins_shortened = [".".join(p.split('.')[-3:-1]) for p in all_volatility3_plugins]
counts = Counter(plugins_shortened)
plugins_shortened_unique = [p for p in plugins_shortened if counts[p] == 1]

invalid_plugins = [p for p in args.plugins if (p not in all_volatility3_plugins and p not in plugins_shortened_unique)]
if invalid_plugins:
    print(f"ERROR: Invalid plugin(s): {', '.join(invalid_plugins)}")
    sys.exit(1)

dump_file = args.file
output_dir = args.output
volatility3_plugins = args.plugins
tools_path = args.tools
symbols_path = args.symbols

os.makedirs(output_dir, exist_ok=True)





def run_plugin(plugin_name_and_dump):
    plugin_name, dump_file = plugin_name_and_dump
    try:
        if not os.path.exists(dump_file):
            raise FileNotFoundError(f"Dump file {dump_file} does not exist.")
        if not plugin_name:
            raise ValueError("Plugin name cannot be empty.")
        
        # Check if plugin has been run before
        output_path = os.path.join(output_dir, f"{plugin_name}.json")
        if os.path.exists(output_path):
            return {"plugin": plugin_name, "results": [], "error": "Plugin already run"}
        print(f"[INFO] Running plugin: {plugin_name} on dump file: {dump_file}")
        if plugin_name == "linux.pagecache.RecoverFs":
            print("[WARNING] RecoverFs plugin is known to be slow, it may take a while to complete.")
            # Check if the output directory exists, if not create it
            if not os.path.exists(os.path.join(output_dir, "RecoverFs")):
                os.makedirs(os.path.join(output_dir, "RecoverFs"))
            # Run the plugin using Volatility3
            result = subprocess.run(
            [
                sys.executable,
                f"{tools_path}/volatility3/vol.py",
                "-f", dump_file,
                "-r", "json",
                "-o", os.path.join(output_dir, "RecoverFs"),
                plugin_name
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=600  # Timeout after 10 minutes
        )
        else:
            result = subprocess.run(
                [
                    sys.executable,
                    f"{tools_path}/volatility3/vol.py",
                    "-f", dump_file,
                    "-r", "json",
                    plugin_name
                ],
                capture_output=True,
                text=True,
                check=True,
                timeout=600  # Timeout after 10 minutes
            )
        if not result.stdout.strip():
            raise ValueError("Empty stdout")

        parsed_output = json.loads(result.stdout)
        return {"plugin": plugin_name, "results": parsed_output}
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Plugin {plugin_name} timed out.")
        return {"plugin": plugin_name, "results": [], "error": "timeout"}
    except Exception as e:
        return {"plugin": plugin_name, "results": [], "error": str(e)}

def flatten_pstree(node, root_pid=None, level=0, path=""):
    if root_pid is None:
        root_pid = node["PID"]
        path = str(root_pid)

    # Current process info
    flat_node = {
        "PID": node["PID"],
        "PPID": node["PPID"],
        "TID": node.get("TID", None),
        "COMM": node["COMM"],
        "OFFSET (V)": node.get("OFFSET (V)", None),
        "root_pid": root_pid,
        "level": level,
        "path": path
    }

    # Start output list with current node
    output = [flat_node]

    # Recurse into children
    for child in node.get("__children", []):
        child_path = path + " > " + str(child["PID"])
        output.extend(flatten_pstree(child, root_pid=root_pid, level=level+1, path=child_path))

    return output




def save_result_callback(result):
    plugin = result["plugin"]
    if result.get("error"):
        print(f"[ERROR] {plugin}: {result['error']}")
        return

    if not result["results"]:
        print(f"[WARNING] No results for {plugin}")
        return
    else:
        print(f"[INFO] Saving results for {plugin}")
    path = os.path.join(output_dir, f"{plugin}.json")
    with open(path, "w") as f:
        if "pstree" in plugin:
            for root in result["results"]:
                flat_entries = flatten_pstree(root)
                for entry in flat_entries:
                    json.dump(entry, f)
                    f.write("\n")
        else:

            for entry in result["results"]:
                json.dump(entry, f)
                f.write("\n")
    print(f"[INFO] Results saved to {path}")


def main():
    tasks = [(plugin, dump_file) for plugin in volatility3_plugins]
    print(f"[INFO] Starting to process {len(tasks)} plugins...")
    
    if args.auto_symbol:
        cmd = [
            sys.executable,
            f"{args.module_dir}/auto_symbol.py",
            "-f", dump_file,
            "-t", args.tools,
            "-o", args.symbols,
            "-d", args.module_dir
        ]

        if args.force_build:
            cmd.append("--force-build")

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to download and generate symbols: {e}")
            sys.exit(1)

    with Pool(processes=min(len(tasks), args.threads)) as pool:
        results = []
        for plugin_task in tasks:
            result = pool.apply_async(run_plugin, args=(plugin_task,), callback=save_result_callback)
            results.append(result)
        
        pool.close()
        pool.join()
        
        # Wait for all results
        for result in results:
            result.get()  # This will raise any exception that occurred
    
    print(f"[INFO] Completed processing all plugins.")

if __name__ == "__main__":
    main()
