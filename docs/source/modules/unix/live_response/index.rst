Unix / Live Response
====================

Available modules for Unix / Live Response.

.. raw:: html

   <div class="module-cards">
   <a class="module-card" href="containers/docker_images.html"><span class="module-card-title">Docker Images</span><span class="module-card-desc">Docker images present on the host</span></a>
   <a class="module-card" href="containers/docker_ps.html"><span class="module-card-title">Docker Ps</span><span class="module-card-desc">Docker containers, running and stopped</span></a>
   <a class="module-card" href="hardware/dmidecode.html"><span class="module-card-title">Dmidecode</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command dmidecode</span></a>
   <a class="module-card" href="hardware/lscpu.html"><span class="module-card-title">Lscpu</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command lscpu</span></a>
   <a class="module-card" href="hardware/lsusb.html"><span class="module-card-title">Lsusb</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command lsusb</span></a>
   <a class="module-card" href="integrity/hash_executables.html"><span class="module-card-title">Hash Executables</span><span class="module-card-desc">Hashes of every executable collected by UAC, for IOC matching</span></a>
   <a class="module-card" href="integrity/hash_processes.html"><span class="module-card-title">Hash Processes</span><span class="module-card-desc">Hashes of the binaries backing running processes, for IOC matching</span></a>
   <a class="module-card" href="network/arp.html"><span class="module-card-title">Arp</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command arp or arp -a</span></a>
   <a class="module-card" href="network/ip_route.html"><span class="module-card-title">Ip Route</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command ip route</span></a>
   <a class="module-card" href="network/iptables.html"><span class="module-card-title">Iptables</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command iptables</span></a>
   <a class="module-card" href="network/netstat.html"><span class="module-card-title">Netstat</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command netstat</span></a>
   <a class="module-card" href="network/nmcli.html"><span class="module-card-title">Nmcli</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command nmcli</span></a>
   <a class="module-card" href="network/proc_net_tcp.html"><span class="module-card-title">Proc Net Tcp</span><span class="module-card-desc">TCP sockets read from /proc/net/tcp, complements ss</span></a>
   <a class="module-card" href="network/ss.html"><span class="module-card-title">Ss</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command ss. UAC collects ss rather than netstat on modern distributions.</span></a>
   <a class="module-card" href="packages/dpkg_l.html"><span class="module-card-title">Dpkg L</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command dpkg -l</span></a>
   <a class="module-card" href="packages/snap.html"><span class="module-card-title">Snap</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command snap</span></a>
   <a class="module-card" href="process/ps.html"><span class="module-card-title">Ps</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command ps and ps -ef</span></a>
   <a class="module-card" href="process/top.html"><span class="module-card-title">Top</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command top and top -b</span></a>
   <a class="module-card" href="storage/blkid.html"><span class="module-card-title">Blkid</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command blkid</span></a>
   <a class="module-card" href="storage/df.html"><span class="module-card-title">Df</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command df and df -h</span></a>
   <a class="module-card" href="storage/lsblk.html"><span class="module-card-title">Lsblk</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command lsblk</span></a>
   <a class="module-card" href="storage/mount.html"><span class="module-card-title">Mount</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command mount</span></a>
   <a class="module-card" href="system/env.html"><span class="module-card-title">Env</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command env</span></a>
   <a class="module-card" href="system/findmnt.html"><span class="module-card-title">Findmnt</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command findmnt</span></a>
   <a class="module-card" href="system/free.html"><span class="module-card-title">Free</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command free</span></a>
   <a class="module-card" href="system/journal_boots.html"><span class="module-card-title">Journal Boots</span><span class="module-card-desc">Boot sessions recorded by the systemd journal</span></a>
   <a class="module-card" href="system/last.html"><span class="module-card-title">Last</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command last and lastb</span></a>
   <a class="module-card" href="system/lsmod.html"><span class="module-card-title">Lsmod</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command lsmod</span></a>
   <a class="module-card" href="system/sysctl.html"><span class="module-card-title">Sysctl</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command sysctl -a</span></a>
   <a class="module-card" href="system/systemctl_lu.html"><span class="module-card-title">Systemctl Lu</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command systemctl list-units</span></a>
   <a class="module-card" href="system/systemctl_luf.html"><span class="module-card-title">Systemctl Luf</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command systemctl list-unit-files</span></a>
   <a class="module-card" href="system/systemctl_timers.html"><span class="module-card-title">Systemctl Timers</span><span class="module-card-desc">systemd timers, a persistence location</span></a>
   <a class="module-card" href="system/uname.html"><span class="module-card-title">Uname</span><span class="module-card-desc">Kernel and platform identification from uname -a</span></a>
   <a class="module-card" href="system/vmstat.html"><span class="module-card-title">Vmstat</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command vmstat</span></a>
   <a class="module-card" href="system/who.html"><span class="module-card-title">Who</span><span class="module-card-desc">Kelly Brazil - JsonConverter - Parsing the output of the command who. UAC collects who rather than last on modern distributions.</span></a>
   </div>

.. toctree::
   :hidden:

   containers/docker_images
   containers/docker_ps
   hardware/dmidecode
   hardware/lscpu
   hardware/lsusb
   integrity/hash_executables
   integrity/hash_processes
   network/arp
   network/ip_route
   network/iptables
   network/netstat
   network/nmcli
   network/proc_net_tcp
   network/ss
   packages/dpkg_l
   packages/snap
   process/ps
   process/top
   storage/blkid
   storage/df
   storage/lsblk
   storage/mount
   system/env
   system/findmnt
   system/free
   system/journal_boots
   system/last
   system/lsmod
   system/sysctl
   system/systemctl_lu
   system/systemctl_luf
   system/systemctl_timers
   system/uname
   system/vmstat
   system/who
