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
   * - 
     - prefetch_orc.yml
     - 
     - 
     - 1.0
     - 
     - net6/PECmd.exe
   * - 
     - sample_c.yml
     - 
     - 
     - 1.0
     - 
     - 
   * - all
     - thor.yml
     - Scan of collected file using Thor (requires Forensic license).
     - 
     - 1.0
     - external
     - thor/thor-linux-64
   * - all
     - thor_lite.yml
     - Scan of collected file using Thor Lite.
     - 
     - 1.0
     - external
     - thor-lite/thor-lite-linux-64
   * - linux
     - uac_indexation.yml
     - Splunk ingestion of parsed artifacts
     - 
     - 1.0
     - external
     - python
   * - module_os
     - sample.yml
     - module_description
     - author_name
     - 1.0
     - module_processor_type
     - module_tool_name
   * - network
     - zeek.yml
     - SParsing of pcap files using zeek
     - 
     - 1.0
     - external
     - docker
   * - unix
     - arp.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command arp or arp -a
     - 
     - 1.0
     - external
     - cat
   * - unix
     - audit.yml
     - Parsing logs from '/var/log/audit'
     - 
     - 1.0
     - internal
     - 
   * - unix
     - auth.yml
     - Parsing logs from '/var/log/auth.log'
     - 
     - 1.0
     - internal
     - 
   * - unix
     - blkid.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command blkid
     - 
     - 1.0
     - external
     - cat
   * - unix
     - bodyfile.yml
     - Parsing logs from '/bodyfile' in UAC collect
     - 
     - 1.0
     - internal
     - 
   * - unix
     - boot.yml
     - Parsing logs from '/var/log/boot'
     - 
     - 1.0
     - internal
     - 
   * - unix
     - cron.yml
     - Parsing logs from '/var/log/cron'
     - 
     - 1.0
     - internal
     - 
   * - unix
     - debug.yml
     - Parsing logs from '/var/log/debug'
     - 
     - 1.0
     - internal
     - 
   * - unix
     - df.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command df and df -h
     - 
     - 1.0
     - external
     - cat
   * - unix
     - dmidecode.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command dmidecode
     - 
     - 1.0
     - external
     - cat
   * - unix
     - dpkg-l.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command dpkg -l
     - Kelly Brazil
     - 1.0
     - external
     - cat
   * - unix
     - dpkg.yml
     - Parsing logs from '/var/log/dpkg'
     - 
     - 1.0
     - internal
     - 
   * - unix
     - env.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command env
     - 
     - 1.0
     - external
     - cat
   * - unix
     - extract_uac.yml
     - 
     - 
     - 1.0
     - internal
     - tar
   * - unix
     - findmnt.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command findmnt
     - 
     - 1.0
     - external
     - cat
   * - unix
     - free.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command free
     - 
     - 1.0
     - external
     - cat
   * - unix
     - ip_route.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command ip route
     - 
     - 1.0
     - external
     - cat
   * - unix
     - iptables.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command iptables
     - 
     - 1.0
     - external
     - cat
   * - unix
     - journal.yml
     - Parsing logs from '/var/log/journal/'
     - 
     - 1.1
     - external
     - journalctl
   * - unix
     - kernel.yml
     - Parsing logs from '/var/log/kernel'
     - 
     - 1.0
     - internal
     - 
   * - unix
     - last.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command last and lastb
     - 
     - 1.0
     - external
     - cat
   * - unix
     - lastlog.yml
     - Parsing logs from '/var/log/lastlog'
     - 
     - 1.0
     - internal
     - 
   * - unix
     - lsblk.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command lsblk
     - 
     - 1.0
     - external
     - cat
   * - unix
     - lsmod.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command lsmod
     - 
     - 1.0
     - external
     - cat
   * - unix
     - lsusb.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command lsusb
     - 
     - 1.0
     - external
     - cat
   * - unix
     - mail.yml
     - Parsing logs from '/var/log/mail'
     - 
     - 1.0
     - internal
     - 
   * - unix
     - message.yml
     - Parsing logs from '/var/log/message'
     - 
     - 1.0
     - internal
     - 
   * - unix
     - mount.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command mount
     - 
     - 1.0
     - external
     - cat
   * - unix
     - netstat.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command netstat
     - 
     - 1.0
     - external
     - cat
   * - unix
     - postgresql.yml
     - Parsing logs from '/var/log/postgresql'
     - 
     - 1.0
     - internal
     - 
   * - unix
     - ps.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command ps and ps -ef
     - 
     - 1.0
     - external
     - cat
   * - unix
     - sysctl.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command sysctl -a
     - 
     - 1.0
     - external
     - cat
   * - unix
     - syslog.yml
     - Parsing logs from '/var/log/syslog'
     - 
     - 1.0
     - internal
     - 
   * - unix
     - systemctl_luf.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command systemctl list-unit-files
     - 
     - 1.0
     - external
     - cat
   * - unix
     - top.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command top and top -b
     - 
     - 1.0
     - external
     - cat
   * - unix
     - utmp.yml
     - Parsing logs from '/var/log/utmp btmp wtmp'
     - 
     - 1.0
     - internal
     - 
   * - unix
     - vmstat.yml
     - Kelly Brazil - JsonConverter - Parsing the output of the command vmstat
     - 
     - 1.0
     - external
     - cat
   * - unix
     - yum.yml
     - Parsing logs from '/var/log/yum'
     - 
     - 1.0
     - internal
     - 
   * - windows
     - amcache.yml
     - Parsing of amcache artifact.
     - 
     - 1.0
     - external
     - net6/AmcacheParser.exe
   * - windows
     - browsers.yml
     - Parsing of browsers artifact.
     - 
     - 1.0
     - external
     - python
   * - windows
     - chromium.yml
     - Parsing of chromium artifact.
     - 
     - 1.0
     - external
     - python
   * - windows
     - dummy_external.yml
     - Dummy module to test WSL / Powershell connexion
     - 
     - 1.0
     - external
     - net6/AmcacheParser.exe
   * - windows
     - evtx_orc.yml
     - Parsing of EVTX collected by DFIR ORC
     - 
     - 1.0
     - external
     - evtx_dump
   * - windows
     - extract_orc.yml
     - 
     - 
     - 1.0
     - internal, external
     - 7zz
   * - windows
     - firefox.yml
     - Parsing of firefox artifact.
     - 
     - 1.0
     - external
     - python
   * - windows
     - hayabusa.yml
     - Hayabusa scan of evtx files
     - maxspl
     - 1.0
     - external
     - hayabusa/hayabusa-3.0.1-lin-x64-gnu
   * - windows
     - hives_hkcu.yml
     - Parsing of registry hives artifact.
     - 
     - 1.0
     - external
     - net6/RECmd/RECmd.exe
   * - windows
     - hives_hklm.yml
     - Parsing of registry hives artifact.
     - 
     - 1.0
     - external
     - net6/RECmd/RECmd.exe
   * - windows
     - jump_list.yml
     - Parsing of jump list artifact.
     - 
     - 1.0
     - external
     - net6/JLECmd.exe
   * - windows
     - lnk.yml
     - Parsing of lnk artifact.
     - 
     - 1.0
     - external
     - net6/LECmd.exe
   * - windows
     - log2timeline_plaso.yml
     - run log2timeline to create a Plaso storage file
     - 
     - 1.0
     - external
     - docker
   * - windows
     - orc_indexation.yml
     - Splunk ingestion of parsed artifacts
     - 
     - 1.0
     - external
     - python
   * - windows
     - orc_offline.yml
     - 
     - maxspl
     - 1.0
     - external
     - python.exe
   * - windows
     - prefetch.yml
     - 
     - 
     - 1.0
     - external
     - net6/PECmd.exe
   * - windows
     - recycle_bin.yml
     - Parsing of recycle bin artifact.
     - 
     - 1.0
     - external
     - net6/RBCmd.exe
   * - windows
     - restore_fs.yml
     - Restore original filesystem structure from DFIR ORC triage
     - 
     - 1.0
     - external
     - Restore_FS
   * - windows
     - shell_bags.yml
     - Parsing of shell bags artifact.
     - 
     - 1.0
     - external
     - net6/SBECmd.exe
   * - windows
     - shimcache.yml
     - Parsing of ShimCache artifact.
     - 
     - 1.0
     - external
     - net6/AppCompatCacheParser.exe
   * - windows
     - srum.yml
     - Parsing of SRUM artifact.
     - 
     - 1.0
     - external
     - artemis
   * - windows
     - test_process_dir.yml
     - 
     - 
     - 1.0
     - external
     - process_dir
   * - windows
     - test_process_dir_multiple_output.yml
     - 
     - 
     - 1.0
     - external
     - process_dir_multiple_output
   * - windows
     - win_memory.yml
     - 
     - 
     - 1.0
     - internal, external
     - memprocfs/memprocfs
   * - windows
     - win_timeline.yml
     - Parsing of Windows Timeline (ActivitiesCache.db) artifact.
     - 
     - 1.0
     - external
     - net6/WxTCmd.exe