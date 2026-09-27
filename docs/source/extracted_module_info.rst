Supported Modules
=================

.. list-table:: Extracted Module Information
   :header-rows: 1

   * - OS
     - Filename
     - Description
     - Author
     - Version
     - Processor Type
     - Tool Path
   * - generic
     - age\_decrypt.yml
     - Used to decrypt age files. Don't forget to put the key in /OSIR/OSIR/configs/dependencies/encryption/key.age.
     - maxspl
     - 2.0
     - external
     - age
   * - generic
     - indexer\_file\_csv.yml
     - Splunk logs ingestion (DFIR ORC and UAC) using module-specific json2splunk-rs configuration.
     - typ
     - 1.0
     - internal
     - json2splunk-rs
   * - generic
     - indexer\_ng.yml
     - Splunk logs ingestion (DFIR ORC and UAC) using module-specific json2splunk-rs configuration.
     - maxspl
     - 2.0
     - internal
     - json2splunk-rs
   * - generic
     - loki\_orc.yml
     - YARA/IOC scan of the filesystem rebuilt from a DFIR ORC collection (output of the restore\_fs module) using Loki-RS.
     - maxspl
     - 1.0
     - external
     - loki-rs/loki\_scan.sh
   * - generic
     - loki\_uac.yml
     - YARA/IOC scan of the files collected by UAC (output of the extract\_uac module) using Loki-RS.
     - maxspl
     - 1.0
     - external
     - loki-rs/loki\_scan.sh
   * - generic
     - mongodb.yml
     - Splunk logs ingestion of Mongodb logs.
     - Typ
     - 2.0
     - external
     - json2splunk-rs
   * - generic
     - thor\_lite\_orc.yml
     - Scan of collected file using Thor Lite.
     - maxspl
     - 1.0
     - external
     - thor-lite/thor-lite-linux-64
   * - generic
     - thor\_lite\_uac.yml
     - Scan of collected file using Thor Lite.
     - maxspl
     - 1.0
     - external
     - thor-lite/thor-lite-linux-64
   * - generic
     - thor\_orc.yml
     - Scan of collected DFIR ORC (output of restore\_fs module) file using Thor (requires Forensic license).
     - maxspl
     - 2.0
     - external
     - thor/thor-linux-64
   * - generic
     - thor\_orc\_ram.yml
     - Scan of RAM restored file system from MemProcFS using Thor (requires Forensic license).
     - maxspl
     - 2.0
     - external
     - thor/thor-linux-64
   * - generic
     - thor\_uac.yml
     - Scan of collected UAC (output of extract\_uac module) files using Thor (requires Forensic license).
     - Typ
     - 2.0
     - external
     - thor/thor-linux-64
   * - generic
     - thor\_update.yml
     - Update Thor signature files using thor-util.
     - maxspl
     - 2.0
     - external
     - thor/thor-util
   * - network
     - zeek.yml
     - Parsing of pcap files using zeek
     - maxspl
     - 2.0
     - external
     - docker
   * - unix
     - apt\_history.yml
     - Package install/remove history from /var/log/apt/history.log
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - apt\_sources.yml
     - Configured apt repositories
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - arp.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command arp or arp -a
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - at\_acl.yml
     - at.allow and at.deny access control
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - at\_jobs.yml
     - Pending at jobs
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - audit.yml
     - Parsing logs from '/var/log/audit'
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - auth.yml
     - Parsing logs from '/var/log/auth.log'
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - authlog.yml
     - Parse auth log from UAC [root] using Dissect plugin
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - bash\_history.yml
     - Parse bash history from UAC [root] using Dissect plugin
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - blkid.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command blkid
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - boot.yml
     - Parsing logs from '/var/log/boot'
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - collect\_info\_uac.yml
     - Hash of DFIR UAC collected file
     - maxspl
     - 2.0
     - external
     - /usr/bin/find
   * - unix
     - command\_history.yml
     - Parse .$SHELL\_history from UAC [root] using Dissect plugin
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - cron.yml
     - Parsing logs from '/var/log/cron'
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - cronjobs.yml
     - Parse cronjobs using dissect plugin
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - crontab.yml
     - System and user crontabs
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - debug.yml
     - Parsing logs from '/var/log/debug'
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - df.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command df and df -h
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - dmidecode.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command dmidecode
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - docker\_images.yml
     - Docker images present on the host
     - maxspl
     - 1.0
     - external
     - cat
   * - unix
     - docker\_ps.yml
     - Docker containers, running and stopped
     - maxspl
     - 1.0
     - external
     - cat
   * - unix
     - dpkg.yml
     - Parsing logs from '/var/log/dpkg'
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - dpkg\_l.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command dpkg -l
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - dpkg\_status.yml
     - Installed packages from the dpkg status database
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - env.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command env
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - extract\_uac.yml
     - Used to execute internal pre-processing for Unix Artefact Collector Capture
     - Typ,maxspl
     - 3.0
     - internal
     - 7zz
   * - unix
     - findmnt.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command findmnt
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - free.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command free
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - fstab.yml
     - Filesystem mounts from /etc/fstab
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - generic.yml
     - Parsing Generic Log File linux into JSONL
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - group.yml
     - Local groups from /etc/group
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - hash\_executables.yml
     - Hashes of every executable collected by UAC, for IOC matching
     - maxspl
     - 1.0
     - external
     - cat
   * - unix
     - hash\_processes.yml
     - Hashes of the binaries backing running processes, for IOC matching
     - maxspl
     - 1.0
     - external
     - cat
   * - unix
     - hosts.yml
     - Static name resolution from /etc/hosts
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - ip\_route.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command ip route
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - iptables.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command iptables
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - journal.yml
     - Parsing logs from '/var/log/journal/'
     - Typ
     - 2.0
     - external
     - journalctl
   * - unix
     - journal\_auth.yml
     - Authentication events from the systemd journal (replaces auth.log on systemd-only hosts)
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - journal\_boots.yml
     - Boot sessions recorded by the systemd journal
     - maxspl
     - 1.0
     - external
     - cat
   * - unix
     - journal\_cron.yml
     - Cron events from the systemd journal
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - journal\_ftp.yml
     - FTP events from the systemd journal
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - kernel.yml
     - Parsing logs from '/var/log/kernel'
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - last.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command last and lastb
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - lastlog.yml
     - Parsing logs from '/var/log/lastlog'
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - logrotate.yml
     - logrotate configuration
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - lsblk.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command lsblk
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - lscpu.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command lscpu
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - lsmod.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command lsmod
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - lsusb.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command lsusb
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - mactime.yml
     - Parsing logs from '/bodyfile' in UAC collect
     - Typ
     - 2.0
     - external
     - TurboLP
   * - unix
     - mail.yml
     - Parsing logs from '/var/log/mail'
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - mount.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command mount
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - netstat.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command netstat
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - nmcli.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command nmcli
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - openssh.yml
     - Parse openssh authorized\_keys,known\_hosts,private\_keys,public\_keys from UAC [root] using Dissect plugin
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - osinfo.yml
     - Parse osinfo from UAC [root] using Dissect plugin
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - postgresql.yml
     - Parsing logs from '/var/log/postgresql'
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - proc\_net\_tcp.yml
     - TCP sockets read from /proc/net/tcp, complements ss
     - maxspl
     - 1.0
     - external
     - cat
   * - unix
     - ps.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command ps and ps -ef
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - resolv.yml
     - DNS resolvers from resolv.conf
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - securelog.yml
     - Parse auth/secure log from UAC [root] using Dissect plugin
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - shadow.yml
     - Password ageing metadata from /etc/shadow
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - snap.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command snap
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - sqlite.yml
     - Parsing SQLite3 Database into JSONL
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - ss.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command ss. UAC collects ss rather than netstat on modern distributions.
     - maxspl
     - 1.0
     - external
     - cat
   * - unix
     - ssh.yml
     - Parse ssh authorized\_keys,known\_hosts,private\_keys,public\_keys,config,session from UAC [root] using Dissect plugin
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - ssh\_pub\_key.yml
     - SSH public keys found on disk
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - sysctl.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command sysctl -a
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - syslog.yml
     - Parsing logs from '/var/log/syslog'
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - systemctl\_lu.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command systemctl list-units
     - maxspl
     - 1.0
     - external
     - cat
   * - unix
     - systemctl\_luf.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command systemctl list-unit-files
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - systemctl\_timers.yml
     - systemd timers, a persistence location
     - maxspl
     - 1.0
     - external
     - cat
   * - unix
     - systemd\_service.yml
     - systemd service unit definitions
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - systemd\_timer.yml
     - systemd timer unit definitions
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - top.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command top and top -b
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - uac\_indexer.yml
     - Splunk logs ingestion (UAC) using json2splunk configuration from dependencies/uac\_indexer\_patterns.yml
     - Typ
     - 2.0
     - external
     - python
   * - unix
     - uac\_log.yml
     - Parse the UAC acquisition log (uac-\\*.log) and execution log (uac.log)
     - maxspl
     - 1.0
     - external
     - python
   * - unix
     - udev\_rules.yml
     - udev rules, a known persistence location
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - uname.yml
     - Kernel and platform identification from uname -a
     - maxspl
     - 1.0
     - external
     - cat
   * - unix
     - usbguard\_device.yml
     - usbguard device events
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - usbguard\_policy.yml
     - usbguard policy events
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - user\_details.yml
     - Parse user infos from UAC [root] using Dissect plugin
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - utmp.yml
     - Parsing logs from '/var/log/utmp btmp wtmp'
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - vhdx.yml
     - Used to mount vhdx file system.
     - Typ
     - 2.0
     - external
     - target-mount
   * - unix
     - vmstat.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command vmstat
     - Kelly Brazil
     - 2.0
     - external
     - cat
   * - unix
     - web\_access.yml
     - Parsing web access logs
     - maxspl
     - 3.0
     - external
     - TurboLP
   * - unix
     - who.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command who. UAC collects who rather than last on modern distributions.
     - maxspl
     - 1.0
     - external
     - cat
   * - unix
     - wtmp\_utmp.yml
     - Login records from binary utmp/wtmp/btmp using the CERT-EDF plasma dissector
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - wtmpdb.yml
     - Parsing login sessions from '/var/log/wtmp.db' (wtmpdb, Debian 13+/openSUSE/Fedora 42+)
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - xdg\_autostart.yml
     - XDG autostart entries, a known persistence location
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - yum.yml
     - Parsing logs from '/var/log/yum'
     - Typ
     - 2.0
     - internal
     - 
   * - unix
     - yum\_history.yml
     - Package history from the yum/dnf log
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - yum\_sources.yml
     - Configured yum/dnf repositories
     - maxspl
     - 1.0
     - internal
     - 
   * - unix
     - zeek\_log.yml
     - Parsing logs from Zeek
     - Typ
     - 2.0
     - internal
     - 
   * - windows
     - IIS.yml
     - Parse IIS from DFIR ORC restore\_fs using Dissect plugin
     - maxspl
     - 2.0
     - internal
     - 
   * - windows
     - activities\_cache.yml
     - Parse ActivitiesCache.db from DFIR ORC restore\_fs using Dissect plugin
     - maxspl
     - 2.0
     - internal
     - 
   * - windows
     - amcache.yml
     - Parsing of amcache artifact.
     - maxspl
     - 2.0
     - external
     - net9/AmcacheParser.exe
   * - windows
     - anssi\_decode.yml
     - ANSSI tool designed for detecting anomalous Portable Executable (PE) files among the NTFSInfo data collected by DFIR-ORC
     - maxspl
     - 2.0
     - internal
     - machine\_analysis
   * - windows
     - browsers.yml
     - Parsing of browsers artifact.
     - maxspl
     - 2.0
     - external
     - python
   * - windows
     - collect\_info\_orc.yml
     - Hash of DFIR ORC collected file
     - maxspl
     - 2.0
     - external
     - /usr/bin/find
   * - windows
     - dfir\_orc\_decrypt.yml
     - Used to decrypt age files. Don't forget to put the key in /OSIR/OSIR/configs/dependencies/encryption/DFIRORC\_key.pem.
     - maxspl
     - 3.0
     - external
     - orc-decrypt-rs
   * - windows
     - dummy\_external.yml
     - Dummy module to test WSL / Powershell connexion
     - maxspl
     - 2.0
     - external
     - net9/AmcacheParser.exe
   * - windows
     - evtx.yml
     - Parsing of EVTX collected by DFIR ORC or in the filesystem
     - maxspl
     - 2.0
     - external
     - evtx\_dump
   * - windows
     - extract\_orc.yml
     - Used to execute internal pre-processing for DFIR-ORC capture
     - maxspl
     - 3.0
     - internal, external
     - 7zz
   * - windows
     - hayabusa.yml
     - Hayabusa scan of evtx files
     - maxspl
     - 2.0
     - external
     - hayabusa/hayabusa-3.0.1-lin-x64-gnu
   * - windows
     - hives\_hkcu.yml
     - Parsing of registry hives artifact.
     - maxspl
     - 2.0
     - external
     - net9/RECmd/RECmd.exe
   * - windows
     - hives\_hklm.yml
     - Parsing of registry hives artifact.
     - maxspl
     - 2.0
     - external
     - net9/RECmd/RECmd.exe
   * - windows
     - indexer.yml
     - Splunk logs ingestion (DFIR ORC and UAC) using module-specific json2splunk configuration instead of dependencies/\\*\_indexer\_patterns.yml
     - maxspl
     - 2.0
     - internal
     - python
   * - windows
     - jump\_list.yml
     - Parsing of jump list artifact.
     - maxspl
     - 2.0
     - external
     - net9/JLECmd.exe
   * - windows
     - lnk.yml
     - Parsing of lnk artifact.
     - maxspl
     - 2.0
     - external
     - net9/LECmd.exe
   * - windows
     - log2timeline\_plaso.yml
     - run log2timeline to create a Plaso storage file
     - maxspl
     - 2.0
     - external
     - docker
   * - windows
     - mft.yml
     - Parsing of $MFT artifact.
     - Typ
     - 2.0
     - external
     - net9/MFTECmd.exe
   * - windows
     - ogre-activity-cache.yml
     - Parsing of activity\_cache - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-autoruns.yml
     - Parsing of autoruns - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-chrome-download-history.yml
     - Parsing of browser\_download\_history - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-chrome-extension.yml
     - Parsing of chrome\_extension - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-chrome-history.yml
     - Parsing of browser\_history - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-evt.yml
     - Parsing of evt - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-evtx.yml
     - Parsing of EVTX collected by DFIR ORC or in the filesystem - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-firefox-download-history.yml
     - Parsing of browser\_download\_history - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-firefox-extension.yml
     - Parsing of firefox\_extension - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-firefox-history.yml
     - Parsing of browser\_history - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-hive-amcache-hve.yml
     - Parsing of reg\_keys - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-hive-bcd-template.yml
     - Parsing of reg\_keys - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-hive-components.yml
     - Parsing of reg\_keys - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-hive-default.yml
     - Parsing of reg\_keys - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-hive-elam.yml
     - Parsing of reg\_keys - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-hive-ntuser-dat.yml
     - Parsing of reg\_keys - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-hive-sam.yml
     - Parsing of reg\_keys - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-hive-software.yml
     - Parsing of reg\_keys - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-hive-system.yml
     - Parsing of reg\_keys - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-hive-usrclass-dat.yml
     - Parsing of reg\_keys - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-list-dll.yml
     - Parsing of listdlls - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-lnk-batched.yml
     - Parsing of lnk - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-pca-app-launch.yml
     - Parsing of pca\_app\_launch - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-pca-general-record.yml
     - Parsing of pca\_general\_record - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-prefetch.yml
     - Parsing of prefetch - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-recycle-bin.yml
     - Parsing of recycle\_bin - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-acmru.yml
     - Parsing of acmru - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-amcache-driver.yml
     - Parsing of amcache\_driver - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-amcache-files.yml
     - Parsing of amcache\_file - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-amcache-program.yml
     - Parsing of amcache\_program - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-antifishing-file.yml
     - Parsing of antifishing\_file - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-app-compat-cache.yml
     - Parsing of app\_compat\_cache - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-autoruns-software.yml
     - Parsing of reg\_autoruns - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-autoruns-system.yml
     - Parsing of autorun\_hive - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-autoruns-user.yml
     - Parsing of reg\_autoruns - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-bamdam.yml
     - Parsing of bam\_dam - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-certificates-software.yml
     - Parsing of x509\_cert - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-certificates-users.yml
     - Parsing of x509\_cert - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-clsid-software.yml
     - Parsing of clsid - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-clsid-users.yml
     - Parsing of clsid - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-mass-storage-system.yml
     - Parsing of mass\_storage - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-mui-cache.yml
     - Parsing of mui\_cache - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-network-configuration.yml
     - Parsing of network\_config - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-pending-file-rename.yml
     - Parsing of pending\_rename - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-recent-app.yml
     - Parsing of recent\_app - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-reg-system-info.yml
     - Parsing of reg\_systeminfo - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-run-mru.yml
     - Parsing of run\_mru - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-scheduled-task.yml
     - Parsing of scheduled\_tasks - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-services-control-set.yml
     - Parsing of services - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-shell-bag.yml
     - Parsing of shellbags - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-shim-database.yml
     - Parsing of shim\_db - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-snapshot-exclude.yml
     - Parsing of backup\_exclude - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-subject-interface-package.yml
     - Parsing of subject\_interface\_package - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-user-assist.yml
     - Parsing of user\_assist - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-registry-user-profile.yml
     - Parsing of user\_profile - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-srum.yml
     - Parsing of srum - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-system-info.yml
     - Parsing of systeminfo - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-tcp-connection.yml
     - Parsing of tcpvcon - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-usn-info.yml
     - Parsing of usninfo - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-volstat.yml
     - Parsing of volstats - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-vss-snapshot.yml
     - Parsing of vss\_snapshot - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - ogre-wer.yml
     - Parsing of wer - using ANSSI DFIR OGRE
     - maxspl
     - 1.0
     - external
     - /app/ogre-venv/bin/dfir-ogre
   * - windows
     - orc\_indexer.yml
     - Splunk logs ingestion (ORC) using json2splunk configuration from dependencies/orc\_indexer\_patterns.yml
     - maxspl
     - 2.0
     - external
     - python
   * - windows
     - orc\_log.yml
     - Parse the DFIR ORC execution log (DFIR-ORC\_\\*.log) for run parameters, archives, commands and their outcome
     - maxspl
     - 1.0
     - external
     - python
   * - windows
     - orc\_offline.yml
     - Used to execute DFIR ORC on dd capture
     - maxspl
     - 2.0
     - external
     - python.exe
   * - windows
     - orc\_outcome.yml
     - Process DFIR ORC outcome and outline json files.
     - maxspl
     - 1.0
     - external
     - python
   * - windows
     - powershell\_history.yml
     - Parse ConsoleHost\_history.txt
     - maxspl
     - 2.0
     - internal
     - 
   * - windows
     - prefetch.yml
     - Eric Zimmerman - PECmd.exe
     - Eric Zimmerman
     - 2.0
     - external
     - net9/PECmd.exe
   * - windows
     - prefetch\_orc.yml
     - Eric Zimmerman - PECmd.exe
     - Eric Zimmerman
     - 2.0
     - external
     - net9/PECmd.exe
   * - windows
     - pstree\_live\_response.yml
     - Parse processes1.csv to produce pstree
     - maxspl
     - 2.0
     - external
     - python
   * - windows
     - pstree\_security.yml
     - Parse output of EVTX module to build process tree from security.evtx - event ID 4688
     - maxspl
     - 2.0
     - external
     - python
   * - windows
     - pstree\_sysmon.yml
     - Parse output of EVTX module to build process tree from the Sysmon operational channel - event ID 1
     - maxspl
     - 2.0
     - external
     - python
   * - windows
     - recycle\_bin.yml
     - Parsing of recycle bin artifact.
     - maxspl
     - 2.0
     - external
     - net9/RBCmd.exe
   * - windows
     - restore\_fs.yml
     - Restore original filesystem structure from DFIR ORC triage
     - maxspl
     - 2.0
     - external
     - Restore\_FS
   * - windows
     - shell\_bags.yml
     - Parsing of shell bags artifact.
     - maxspl
     - 2.0
     - external
     - net9/SBECmd.exe
   * - windows
     - shimcache.yml
     - Parsing of ShimCache artifact.
     - maxspl
     - 2.0
     - external
     - net9/AppCompatCacheParser.exe
   * - windows
     - srum.yml
     - Parsing of SRUM artifact.
     - maxspl
     - 2.0
     - external
     - artemis
   * - windows
     - test\_process\_dir.yml
     - description
     - maxspl
     - 2.0
     - external
     - process\_dir
   * - windows
     - test\_process\_dir\_multiple\_output.yml
     - test\_process\_dir\_multiple\_output
     - maxspl
     - 2.0
     - external
     - process\_dir\_multiple\_output
   * - windows
     - webserver.yml
     - Parse webserver access,certificates,error,hosts,logs from UAC [root] using Dissect plugin
     - Typ
     - 2.0
     - internal
     - 
   * - windows
     - wer.yml
     - Parse .wer files
     - maxspl
     - 2.0
     - internal
     - 
   * - windows
     - win\_arp\_cache.yml
     - Parse arp\_cache.txt from DFIR ORC (arp -a command)
     - maxspl
     - 2.0
     - internal
     - 
   * - windows
     - win\_bits.yml
     - Parse BITS\_jobs.txt from DFIR ORC (bitsadmin.exe /list /allusers /verbose command)
     - maxspl
     - 2.0
     - internal
     - 
   * - windows
     - win\_dns\_cache.yml
     - Parse dns\_cache.txt from DFIR ORC (ipconfig.exe /displaydns command). Output fields lang depends on the system lang
     - maxspl
     - 2.0
     - internal
     - 
   * - windows
     - win\_dns\_records.yml
     - Parse DNS\_records.txt from DFIR ORC (custom ps1 command)
     - maxspl
     - 2.0
     - internal
     - 
   * - windows
     - win\_enumlocs.yml
     - Parse Enumlocs.txt from DFIR ORC
     - maxspl
     - 2.0
     - internal
     - 
   * - windows
     - win\_handle.yml
     - Parse handle from DFIR ORC (handle.exe /a command)
     - maxspl
     - 2.0
     - internal
     - 
   * - windows
     - win\_listdlls.yml
     - Parse Listdlls.txt from DFIR ORC (Listdlls.exe command)
     - maxspl
     - 2.0
     - internal
     - 
   * - windows
     - win\_memory.yml
     - Parsing of Windows memory dump.
     - maxspl
     - 2.0
     - internal, external
     - memprocfs/memprocfs
   * - windows
     - win\_netstat.yml
     - Parse netstat.txt from DFIR ORC (netstat.exe -a -n -o command)
     - maxspl
     - 2.0
     - internal
     - 
   * - windows
     - win\_routes.yml
     - Parse routes.txt from DFIR ORC (route.exe PRINT command)
     - maxspl
     - 2.0
     - internal
     - 
   * - windows
     - win\_tcpvcon.yml
     - Parse routes.txt from DFIR ORC (Tcpvcon.exe -a -n -c command)
     - maxspl
     - 2.0
     - internal
     - 
   * - windows
     - win\_timeline.yml
     - Parsing of Windows Timeline (ActivitiesCache.db) artifact. Tool from Nihith (https://github.com/bolisettynihith/ActivitiesCacheParser)
     - maxspl
     - 2.0
     - external
     - python
   * - windows
     - win\_wmi\_eventconsumer.yml
     - Parse EventConsumer.txt from DFIR ORC (powershell.exe Get-WMIObject -Namespace root\Subscription -Class \_\_EventConsumer command)
     - maxspl
     - 2.0
     - internal
     - 