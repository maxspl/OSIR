Windows / Live Response
=======================

Available modules for Windows / Live Response.

.. raw:: html

   <div class="module-cards">
   <a class="module-card" href="win_arp_cache.html"><span class="module-card-title">Win Arp Cache</span><span class="module-card-desc">Parse arp_cache.txt from DFIR ORC (arp -a command)</span></a>
   <a class="module-card" href="win_bits.html"><span class="module-card-title">Win Bits</span><span class="module-card-desc">Parse BITS_jobs.txt from DFIR ORC (bitsadmin.exe /list /allusers /verbose command)</span></a>
   <a class="module-card" href="win_dns_cache.html"><span class="module-card-title">Win Dns Cache</span><span class="module-card-desc">Parse dns_cache.txt from DFIR ORC (ipconfig.exe /displaydns command). Output fields lang depends on the system lang</span></a>
   <a class="module-card" href="win_dns_records.html"><span class="module-card-title">Win Dns Records</span><span class="module-card-desc">Parse DNS_records.txt from DFIR ORC (custom ps1 command)</span></a>
   <a class="module-card" href="win_enumlocs.html"><span class="module-card-title">Win Enumlocs</span><span class="module-card-desc">Parse Enumlocs.txt from DFIR ORC</span></a>
   <a class="module-card" href="win_handle.html"><span class="module-card-title">Win Handle</span><span class="module-card-desc">Parse handle from DFIR ORC (handle.exe /a command)</span></a>
   <a class="module-card" href="win_listdlls.html"><span class="module-card-title">Win Listdlls</span><span class="module-card-desc">Parse Listdlls.txt from DFIR ORC (Listdlls.exe command)</span></a>
   <a class="module-card" href="win_netstat.html"><span class="module-card-title">Win Netstat</span><span class="module-card-desc">Parse netstat.txt from DFIR ORC (netstat.exe -a -n -o command)</span></a>
   <a class="module-card" href="win_routes.html"><span class="module-card-title">Win Routes</span><span class="module-card-desc">Parse routes.txt from DFIR ORC (route.exe PRINT command)</span></a>
   <a class="module-card" href="win_tcpvcon.html"><span class="module-card-title">Win Tcpvcon</span><span class="module-card-desc">Parse routes.txt from DFIR ORC (Tcpvcon.exe -a -n -c command)</span></a>
   <a class="module-card" href="win_wmi_eventconsumer.html"><span class="module-card-title">Win Wmi Eventconsumer</span><span class="module-card-desc">Parse EventConsumer.txt from DFIR ORC (powershell.exe Get-WMIObject -Namespace root\Subscription -Class __EventConsumer command)</span></a>
   </div>

.. toctree::
   :hidden:

   win_arp_cache
   win_bits
   win_dns_cache
   win_dns_records
   win_enumlocs
   win_handle
   win_listdlls
   win_netstat
   win_routes
   win_tcpvcon
   win_wmi_eventconsumer
