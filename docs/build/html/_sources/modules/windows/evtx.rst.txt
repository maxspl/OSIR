evtx
====

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:evtx`` | name_rex: ``\.evtx.*\.jsonl$``
   * ``windows:evtx:powershell`` | name_rex: ``PowerShell\.evtx.*\.jsonl$``
   * ``windows:evtx:powershell:operational`` | name_rex: ``PowerShell.*Operational\.evtx.*\.jsonl$``
   * ``windows:evtx:security`` | name_rex: ``Security\.evtx.*\.jsonl$``
   * ``windows:evtx:sysmon`` | name_rex: ``Sysmon.*\.evtx.*\.jsonl$``
   * ``windows:evtx:system`` | name_rex: ``System\.evtx.*\.jsonl$``

Description
-----------

Parsing of EVTX collected by DFIR ORC or in the filesystem

Timeline
--------

.. list-table::
   :header-rows: 1

   * - action.id
     - Message
   * - 
     - ``Hostname: {host.name} - Source: {event.provider} - EventID: {action.id}``
   * - 
     - ``Hostname: {host.name} - {action.name}``
   * - ``4624``
     - ``{action.properties.TargetDomainName}\\{action.properties.TargetUserName} logged on to {host.name} (LogonType {action.properties.LogonType})``
   * - ``4624``
     - ``{action.properties.TargetDomainName}\\{action.properties.TargetUserName} logged on to {host.name} from IP {source.ip} (LogonType {action.properties.LogonType})``
   * - ``4625``
     - ``{action.properties.TargetDomainName}\\{action.properties.TargetUserName} failed to log on to {host.name} (LogonType {action.properties.LogonType})``
   * - ``4625``
     - ``{action.properties.TargetDomainName}\\{action.properties.TargetUserName} failed to log on to {host.name} from IP {source.ip} (LogonType {action.properties.LogonType})``
   * - ``4634``
     - ``{action.properties.TargetDomainName}\\{action.properties.TargetUserName} logged off from {host.name}``
   * - ``4648``
     - ``{action.properties.TargetDomainName}\\{action.properties.TargetUserName} attempted to log on to {action.properties.TargetServerName} using explicit credentials``
   * - ``4648``
     - ``{action.properties.TargetDomainName}\\{action.properties.TargetUserName} attempted to log on to {host.name} using explicit credentials``
   * - ``4657``
     - ``{user.domain}\\{user.name} modified the value {action.properties.ObjectValueName} of the registry key {action.properties.ObjectName} to {action.properties.NewValue} on {host.name}``
   * - ``4662``
     - ``{user.domain}\\{user.name} accessed the object {action.properties.ObjectName} on {host.name}``
   * - ``4672``
     - ``{user.domain}\\{user.name} logged on to {host.name} with special privileges``
   * - ``4688``
     - ``{user.domain}\\{user.name} executed {process.command_line} on {host.name}``
   * - ``4689``
     - ``Process {process.name} exited. It was executed by {user.domain}\\{user.name} on {host.name}``
   * - ``4720``
     - ``{user.domain}\\{user.name} created account {action.properties.TargetDomainName}\\{action.properties.TargetUserName} on {host.name}``
   * - ``4722``
     - ``{user.domain}\\{user.name} enabled account {action.properties.TargetDomainName}\\{action.properties.TargetUserName}``
   * - ``4723``
     - ``{user.domain}\\{user.name} changed their password on {host.name}``
   * - ``4723``
     - ``{user.domain}\\{user.name} failed to change their password on {host.name}``
   * - ``4725``
     - ``{user.domain}\\{user.name} disabled account {action.properties.TargetDomainName}\\{action.properties.TargetUserName}``
   * - ``4726``
     - ``{user.domain}\\{user.name} deleted account {action.properties.TargetDomainName}\\{action.properties.TargetUserName} on {host.name}``
   * - ``4727``
     - ``{user.domain}\\{user.name} created group {action.properties.TargetDomainName}\\{action.properties.TargetUserName}``
   * - ``4768``
     - ``{action.properties.TargetDomainName}\\{action.properties.TargetUserName} failed to authenticate from {source.ip} (Error Code: {action.properties.Status})``
   * - ``4768``
     - ``{action.properties.TargetDomainName}\\{action.properties.TargetUserName} successfully authenticated from {source.ip}``
   * - ``4769``
     - ``{action.properties.TargetDomainName}\\{action.properties.TargetUserName} was denied a service ticket for {action.properties.ServiceName} from {source.ip} (Error Code: {action.properties.Status})``
   * - ``4769``
     - ``{action.properties.TargetDomainName}\\{action.properties.TargetUserName} was granted a service ticket for {action.properties.ServiceName} from {source.ip}``
   * - ``4771``
     - ``{action.properties.TargetUserName} failed to authenticate from {source.ip}``
   * - ``4776``
     - ``{action.properties.TargetUserName} failed to authenticate on {action.properties.Workstation} (Reason: {action.properties.Status})``
   * - ``4776``
     - ``{action.properties.TargetUserName} successfully authenticated on {action.properties.Workstation}``
   * - ``4798``
     - ``{user.domain}\\{user.name} enumerated local groups of {action.properties.TargetDomainName}\\{action.properties.TargetUserName} on {host.name}``
   * - ``4799``
     - ``{user.domain}\\{user.name} enumerated members of local group {action.properties.TargetUserName} on {host.name}``
   * - ``4825``
     - ``Authenticated user {user.name} was denied the access to Remote Desktop to {host.name} from IP {action.properties.ClientAddress}``
   * - ``1149``
     - ``{user.domain}\\{user.name} successfully authenticated over RDP to {host.name} from IP {source.ip}``
   * - ``21``
     - ``{user.domain}\\{user.name} opened session {action.properties.SessionID} on {host.name} (source: {action.properties.Address})``
   * - ``22``
     - ``{user.domain}\\{user.name} session {action.properties.SessionID} shell started on {host.name}``
   * - ``23``
     - ``{user.domain}\\{user.name} logged off session {action.properties.SessionID} on {host.name}``
   * - ``24``
     - ``{user.domain}\\{user.name} disconnected from session {action.properties.SessionID} on {host.name} (source: {action.properties.Address})``
   * - ``25``
     - ``{user.domain}\\{user.name} reconnected to session {action.properties.SessionID} on {host.name} (source: {action.properties.Address})``
   * - ``5145``
     - ``{user.domain}\\{user.name} was granted access to {action.properties.ShareName}\\{action.properties.RelativeTargetName} from IP {source.ip}``
   * - ``5145``
     - ``{user.domain}\\{user.name} was denied access to {action.properties.ShareName}\\{action.properties.RelativeTargetName} from IP {source.ip}``
   * - ``5154``
     - ``{action.properties.Application} was allowed to listen on {source.ip}:{source.port} on {host.name}``
   * - ``5156``
     - ``{host.name} allowed a connection from {source.ip}:{source.port} to {destination.ip}:{destination.port}``
   * - ``4103``
     - ``{user.domain}\\{user.name} executed PowerShell code on {host.name}``
   * - ``4104``
     - ``{user.domain}\\{user.name} executed PowerShell code on {host.name}``
   * - ``4105``
     - ``Started invocation of PowerShell ScriptBlock on {host.name}``
   * - ``4106``
     - ``Completed invocation of PowerShell ScriptBlock on {host.name}``
   * - ``5382``
     - ``Vault credentials were read by {action.properties.SubjectUserName} on {host.name}``
   * - ``40961``
     - ``PowerShell console is starting up on {host.name}``
   * - ``40962``
     - ``PowerShell console is ready for user input on {host.name}``
   * - ``53504``
     - ``Windows PowerShell has started an IPC listening thread on {host.name}``
   * - ``1``
     - ``Process {process.executable} created by {user.name} on {host.name}``
   * - ``2``
     - ``Process {process.executable} changed the creation time of the file {file.name} on {host.name}``
   * - ``3``
     - ``Network connection from {source.ip} to {destination.ip}:{destination.port} by {process.executable} on {host.name}``
   * - ``4``
     - ``Sysmon service state changed to {action.properties.State} on {host.name}``
   * - ``5``
     - ``Process {process.executable} terminated on {host.name}``
   * - ``6``
     - ``Driver {process.executable} loaded on {host.name}``
   * - ``7``
     - ``Process {process.executable} loaded image {action.properties.ImageLoaded} on {host.name}``
   * - ``8``
     - ``Process {action.properties.SourceImage} created a thread in process {action.properties.TargetImage} on {host.name}``
   * - ``9``
     - ``Process {process.executable} read on {action.properties.Device} device on {host.name}``
   * - ``10``
     - ``{action.properties.SourceImage} was granted {action.properties.GrantedAccess} access to {action.properties.TargetImage} on {host.name}``
   * - ``11``
     - ``{file.name} created by {process.executable} on {host.name}``
   * - ``12``
     - ``Registry key {action.properties.TargetObject} created by {process.executable} on {host.name}``
   * - ``12``
     - ``Registry value {action.properties.TargetObject} created by {process.executable} on {host.name}``
   * - ``12``
     - ``Registry key {action.properties.TargetObject} deleted by {process.executable} on {host.name}``
   * - ``12``
     - ``Registry value {action.properties.TargetObject} deleted by {process.executable} on {host.name}``
   * - ``13``
     - ``Registry key {action.properties.TargetObject} set by {process.executable} on {host.name}``
   * - ``14``
     - ``Registry key {action.properties.TargetObject} renamed to {action.properties.NewName} by {process.executable} on {host.name}``
   * - ``14``
     - ``Registry value {action.properties.TargetObject} renamed to {action.properties.NewName} by {process.executable} on {host.name}``
   * - ``15``
     - ``{action.properties.Image} added a named stream to file {action.properties.TargetFilename} on {host.name}``
   * - ``16``
     - ``Sysmon configuration was updated on {host.name}``
   * - ``17``
     - ``Pipe {action.properties.PipeName} created by {process.executable} on {host.name}``
   * - ``18``
     - ``Pipe {action.properties.PipeName} connected by {process.executable} on {host.name}``
   * - ``19``
     - ``{action.properties.User} created WMI Event Filter {action.properties.Name} on {host.name}``
   * - ``20``
     - ``{action.properties.User} {action.properties.Operation} WMI Consumer {action.properties.Name} on {host.name}``
   * - ``21``
     - ``{action.properties.User} bound WMI Consumer {action.properties.Consumer} to Event Filter {action.properties.Filter} on {host.name}``
   * - ``22``
     - ``{host.name} performed a DNS query for name {dns.question.name} (status: {dns.response_code})``
   * - ``1000``
     - ``An anti-malware scan started on {host.name}``
   * - ``1001``
     - ``An anti-malware scan finished on {host.name}``
   * - ``1002``
     - ``An anti-malware scan was stopped before it finished on {host.name}``
   * - ``1150``
     - ``Microsoft Defender Antivirus client is up and running in a healthy state on {host.name}``
   * - ``26``
     - ``Windows Update successfully found updates on {host.name}``
   * - ``263``
     - ``W32time Service configuration parameters have been updated on {host.name}``
   * - ``15``
     - ``Updated Windows Defender status successfully to SECURITY_PRODUCT_STATE_ON on {host.name}``

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``.Event.System.TimeCreated."#attributes".SystemTime``
     - ``timestamp``
   * - ``Event.System``
     - ``action.system``
   * - ``Event.EventData``
     - ``action.properties``
   * - ``Event.EventData.Attributes``
     - ``action.properties.Attributes``
   * - ``Event.EventData.Requester``
     - ``action.properties.Requester``
   * - ``Event.EventData.ContextInfo``
     - ``action.properties.ContextInfo``
   * - ``Event.EventData.CallingStationID``
     - ``action.properties.CallingStationID``
   * - ``Event.EventData.bytesTotal``
     - ``action.properties.BytesTotal``
   * - ``Event.EventData.Configuration``
     - ``action.properties.ConfigurationFile``
   * - ``Event.EventData.FileVersion``
     - ``action.properties.FileVersion``
   * - ``Event.EventData.Product``
     - ``action.properties.Product``
   * - ``Event.EventData.Description``
     - ``action.properties.Description``
   * - ``Event.EventData.ThreatName``
     - ``action.properties.ThreatName``
   * - ``Event.EventData.DetectionUser``
     - ``action.properties.DetectionUser``
   * - ``Event.EventData.HealthAttestationServer``
     - ``action.properties.HealthAttestationServer``
   * - ``Event.EventData.LastASSecurityIntelligenceAge``
     - ``action.properties.LastASSecurityIntelligenceAge``
   * - ``Event.EventData.LastAVSecurityIntelligenceAge``
     - ``action.properties.LastAVSecurityIntelligenceAge``
   * - ``Event.EventData.LastFullScanAge``
     - ``action.properties.LastFullScanAge``
   * - ``Event.EventData.LastQuickScanAge``
     - ``action.properties.LastQuickScanAge``
   * - ``Event.EventData.NewValue``
     - ``action.properties.NewValue``
   * - ``Event.EventData.SentUpdateServer``
     - ``action.properties.SentUpdateServer``
   * - ``Event.EventData.ServiceFileName``
     - ``action.properties.ServiceFileName``
   * - ``Event.EventData.StatusInformation``
     - ``action.properties.StatusInformation``
   * - ``Event.EventData.Subject``
     - ``action.properties.Subject``
   * - ``Event.EventData.TransmittedServices``
     - ``action.properties.TransmittedServices``
   * - ``custom``
     - 
   * - ``Event.EventData.Image``
     - ``action.properties.Image``
   * - ``parsed_message_kv.Image``
     - ``action.properties.Image``
   * - ``Event.EventData.DestinationPort``
     - ``action.properties.DestinationPort``
   * - ``Event.EventData.DestPort``
     - ``action.properties.DestinationPort``
   * - ``Event.EventData.ErrorCode``
     - ``action.properties.ErrorCode``
   * - ``Event.EventData.ProcessName``
     - ``action.properties.ProcessName``
   * - ``to_int!(.Event.System.EventID."#text")``
     - ``event.code``
   * - ``to_int!(.Event.System.EventID)``
     - ``event.code``
   * - ``to_string!(.Event.System.EventRecordID)``
     - ``event.record``
   * - ``event.code``
     - ``event.id``
   * - ``to_string!(.Event.System.Channel)``
     - ``action.type``
   * - ``to_string!(.Event.System.Channel)``
     - ``event.dataset``
   * - ``custom``
     - 
   * - ``custom``
     - 
   * - ``Event.EventData.ImageLoaded``
     - ``dll.path``
   * - ``Event.EventData.OriginalFileName``
     - ``dll.name``
   * - ``parsed_hashes_kv.IMPHASH``
     - ``dll.pe.imphash``
   * - ``parsed_hashes_kv.MD5``
     - ``dll.hash.md5``
   * - ``parsed_hashes_kv.SHA256``
     - ``dll.hash.sha256``
   * - ``Event.EventData.LocalName``
     - ``file.path``
   * - ``replace(to_string(.Event.EventData.LocalName) ?? "", r'^.*[\\/]', "")``
     - ``file.name``
   * - ``Event.EventData.TargetFilename``
     - ``file.path``
   * - ``replace(to_string(.Event.EventData.TargetFilename) ?? "", r'^.*[\\/]', "")``
     - ``file.name``
   * - ``Event.EventData.jobOwner``
     - ``file.owner``
   * - ``to_string!(.Event.EventData.CreationUtcTime)``
     - ``file.created``
   * - ``Event.EventData.fileLength``
     - ``file.size``
   * - ``replace(to_string(.Event.EventData.name) ?? "", r'^.*[\\/]', "")``
     - ``file.name``
   * - ``Event.EventData.name``
     - ``file.path``
   * - ``replace(to_string(.Event.EventData.ObjectName) ?? "", r'^.*[\\/]', "")``
     - ``file.name``
   * - ``Event.EventData.ObjectName``
     - ``file.path``
   * - ``replace(to_string(.Event.EventData.script.name) ?? "", r'^.*[\\/]', "")``
     - ``file.name``
   * - ``Event.EventData.script.name``
     - ``file.path``
   * - ``parsed_hashes_kv.IMPHASH``
     - ``file.pe.imphash``
   * - ``parsed_hashes_kv_2.IMPHASH``
     - ``file.pe.imphash``
   * - ``parsed_hashes_kv.MD5``
     - ``file.hash.md5``
   * - ``parsed_hashes_kv_2.MD5``
     - ``file.hash.md5``
   * - ``parsed_hashes_kv.SHA256``
     - ``file.hash.sha256``
   * - ``parsed_hashes_kv_2.SHA256``
     - ``file.hash.sha256``
   * - ``split!(split!(.Event.EventData.Message, " ")[0], "\\")[-1]``
     - ``file.name``
   * - ``split!(.Event.EventData.Message, " ")[0]``
     - ``file.path``
   * - ``Event.System.Channel``
     - ``action.type``
   * - ``event.code``
     - ``action.id``
   * - ``.Event.System.Provider."#attributes".Name``
     - ``event.provider``
   * - ``Event.System.Computer``
     - ``host.name``
   * - ``split!(.Event.System.Computer, ".")[0]``
     - ``host.hostname``
   * - ``"windows"``
     - ``os.family``
   * - ``"windows"``
     - ``os.platform``
   * - ``Event.EventData.UtcTime``
     - ``event.created``
   * - ``Event.EventData.name``
     - ``file.name``
   * - ``Event.EventData.CommandLine``
     - ``process.command_line``
   * - ``Event.EventData.ParentCommandLine``
     - ``process.parent.command_line``
   * - ``Event.EventData.RecordNumber``
     - ``action.record_id``
   * - ``Event.EventData.DestinationHostname``
     - ``destination.domain``
   * - ``Event.EventData.DestAddress``
     - ``destination.ip``
   * - ``Event.EventData.DestinationIp``
     - ``destination.ip``
   * - ``Event.EventData.DestPort``
     - ``destination.port``
   * - ``Event.EventData.DestinationPort``
     - ``destination.port``
   * - ``Event.EventData.Description``
     - ``event.reason``
   * - ``Event.EventData.CreationUtcTime``
     - ``file.created``
   * - ``Event.EventData.jobOwner``
     - ``file.owner``
   * - ``Event.EventData.Severity``
     - ``log.level``
   * - ``Event.EventData.Protocol``
     - ``network.transport``
   * - ``Event.EventData.Image``
     - ``process.executable``
   * - ``Event.EventData.ParentImage``
     - ``process.parent.executable``
   * - ``Event.EventData.ParentProcessName``
     - ``process.parent.executable``
   * - ``Event.EventData.ParentProcessId``
     - ``process.ppid``
   * - ``Event.EventData.ThreadID``
     - ``process.thread.id``
   * - ``Event.EventData.CurrentDirectory``
     - ``process.working_directory``
   * - ``Event.EventData.SourceHostname``
     - ``source.domain``
   * - ``Event.EventData.SourcePort``
     - ``source.port``
   * - ``Event.EventData.url``
     - ``url.original``
   * - ``Event.EventData.RemoteName``
     - ``url.original``
   * - ``Event.EventData.SubjectUserSid``
     - ``user.id``
   * - ``Event.EventData.UserID``
     - ``user.id``
   * - ``Event.EventData.TargetUserName``
     - ``user.target.name``
   * - ``Event.EventData.TargetDomainName``
     - ``user.target.domain``
   * - ``Event.EventData.TargetUserSid``
     - ``user.target.id``
   * - ``split!(.Event.EventData.url, r'/')[0]``
     - ``url.domain``
   * - ``split!(.Event.EventData.RemoteName, r'/')[0]``
     - ``url.domain``
   * - ``split!(.Event.EventData.LmPackageName, " ")[0]``
     - ``package.name``
   * - ``"LAN Manager package"``
     - ``package.description``
   * - ``split!(.Event.EventData.LmPackageName, " ")[-1]``
     - ``package.version``
   * - ``split!(.Event.EventData.Application, "\\")[-1]``
     - ``process.name``
   * - ``Event.EventData.NewProcessName``
     - ``process.executable``
   * - ``Event.EventData.ProcessName``
     - ``process.executable``
   * - ``Event.EventData.ImageLoaded``
     - ``process.executable``
   * - ``Event.EventData.SourceImage``
     - ``process.executable``
   * - ``Event.EventData.ProcessName``
     - ``process.executable``
   * - ``downcase(to_string(.log.level) ?? "")``
     - ``log.level``
   * - ``replace(to_string(.process.command_line) ?? "", "\"", "")``
     - ``process.command_line``
   * - ``replace(to_string(.process.parent.command_line) ?? "", "\"", "")``
     - ``process.parent.command_line``
   * - ``downcase(to_string(.process.pe.imphash) ?? "")``
     - ``process.pe.imphash``
   * - ``downcase(to_string(.process.hash.md5) ?? "")``
     - ``process.hash.md5``
   * - ``downcase(to_string(.process.hash.sha1) ?? "")``
     - ``process.hash.sha1``
   * - ``downcase(to_string(.process.hash.sha256) ?? "")``
     - ``process.hash.sha256``
   * - ``downcase(to_string(.file.pe.imphash) ?? "")``
     - ``file.pe.imphash``
   * - ``downcase(to_string(.file.hash.md5) ?? "")``
     - ``file.hash.md5``
   * - ``downcase(to_string(.file.hash.sha256) ?? "")``
     - ``file.hash.sha256``
   * - ``downcase(to_string(.dll.pe.imphash) ?? "")``
     - ``dll.hash.imphash``
   * - ``downcase(to_string(.dll.pe.imphash) ?? "")``
     - ``dll.pe.imphash``
   * - ``downcase(to_string(.dll.hash.md5) ?? "")``
     - ``dll.hash.md5``
   * - ``downcase(to_string(.dll.hash.sha256) ?? "")``
     - ``dll.hash.sha256``
   * - ``process.parent.executable``
     - ``process.parent.command_line``
   * - ``length(to_string(.source.domain) ?? "")``
     - ``source.size_in_char``
   * - ``length(to_string(.destination.domain) ?? "")``
     - ``destination.size_in_char``
   * - ``replace(to_string(.process.executable) ?? "", r'^.*[\\/]', "")``
     - ``process.name``
   * - ``replace(to_string(.process.executable) ?? "", r'[^\\/]*$', "")``
     - ``process.working_directory``
   * - ``replace(to_string(.process.parent.executable) ?? "", r'^.*[\\/]', "")``
     - ``process.parent.name``
   * - ``replace(to_string(.process.parent.executable) ?? "", r'[^\\/]*$', "")``
     - ``process.parent.working_directory``
   * - ``"powershell.exe"``
     - ``process.name``
   * - ``"-1"``
     - ``file.size``
   * - ``Event.EventData.QueryName``
     - ``dns.question.name``
   * - ``Event.EventData.QueryStatus``
     - ``dns.response_code``
   * - ``"query"``
     - ``dns.type``
   * - ``"answer"``
     - ``dns.type``
   * - ``length(to_string(.dns.question.name) ?? "")``
     - ``dns.size_in_char``
   * - ``[to_string(.Event.EventData.Details) ?? ""]``
     - ``registry.data.strings``
   * - ``Event.EventData.TargetObject``
     - ``registry.path``
   * - ``split!(.Event.EventData.TargetObject, "\\")[0]``
     - ``registry.hive``
   * - ``join!(slice!(split!(.Event.EventData.TargetObject, "\\"), 1, -1), "\\")``
     - ``registry.key``
   * - ``split!(.Event.EventData.TargetObject, "\\")[-1]``
     - ``registry.value``
   * - ``"STRING"``
     - ``registry.data.type``
   * - ``[replace(to_string(.Event.EventData.Details) ?? "", r'^"|"$', "")]``
     - ``registry.data.strings``
   * - ``split!(to_string!(.Event.EventData.Details), " ")[0]``
     - ``registry.data.type``
   * - ``custom``
     - 
   * - ``url.original``
     - ``url.full``
   * - ``parse_url.host``
     - ``url.domain``
   * - ``parse_url.scheme``
     - ``url.scheme``
   * - ``parse_url.path``
     - ``url.path``
   * - ``"ipv6"``
     - ``network.type``
   * - ``"ipv4"``
     - ``network.type``
   * - ``parsed_hashes_kv.IMPHASH``
     - ``process.pe.imphash``
   * - ``parsed_hashes_kv_2.IMPHASH``
     - ``process.pe.imphash``
   * - ``parsed_hashes_kv.SHA1``
     - ``process.hash.sha1``
   * - ``parsed_hashes_kv_2.SHA1``
     - ``process.hash.sha1``
   * - ``parsed_hashes_kv.MD5``
     - ``process.hash.md5``
   * - ``parsed_hashes_kv_2.MD5``
     - ``process.hash.md5``
   * - ``parsed_hashes_kv.SHA256``
     - ``process.hash.sha256``
   * - ``parsed_hashes_kv_2.SHA256``
     - ``process.hash.sha256``
   * - ``Event.EventData.ProcessID``
     - ``process.pid``
   * - ``Event.EventData.ProcessId``
     - ``process.pid``
   * - ``Event.EventData.SourceProcessId``
     - ``process.pid``
   * - ``parse_int!(.Event.EventData.NewProcessId)``
     - ``process.pid``
   * - ``parse_int!(.Event.EventData.ProcessId)``
     - ``process.parent.pid``
   * - ``parse_int!(.Event.EventData.ProcessId)``
     - ``process.pid``
   * - ``process.pid``
     - ``process.id``
   * - ``Event.EventData.ThreadID``
     - ``process.thread.id``
   * - ``action.properties.Param1``
     - ``user.name``
   * - ``action.properties.Param2``
     - ``user.domain``
   * - ``custom``
     - 
   * - ``user.name``
     - ``user.id``
   * - ``custom``
     - 
   * - ``split!(.user.name, "\\")[0]``
     - ``user.domain``
   * - ``split!(.user.name, "\\")[1]``
     - ``user.name``
   * - ``Event.EventData.Domain``
     - ``user.domain``
   * - ``Event.System.Computer``
     - ``user.domain``
   * - ``action.properties.SubjectUserName``
     - ``user.name``
   * - ``action.properties.SubjectDomainName``
     - ``user.domain``
   * - ``action.properties.SubjectUserSid``
     - ``user.id``
   * - ``action.properties.UserSid``
     - ``user.id``
   * - ``action.properties.SID``
     - ``user.id``
   * - ``.Event.System.Security."#attributes".UserID``
     - ``user.id``
   * - ``custom``
     - 
   * - ``Event.EventData.IpPort``
     - ``source.port``
   * - ``Event.EventData.WorkstationName``
     - ``source.domain``
   * - ``source.domain``
     - ``source.address``
   * - ``Event.EventData.CallingStationID``
     - ``source.ip``
   * - ``Event.EventData.CallingStationID``
     - ``source.mac``
   * - ``Event.EventData.AuthenticationServer``
     - ``destination.ip``
   * - ``Event.EventData.AuthenticationServer``
     - ``destination.domain``
   * - ``"success"``
     - ``action.outcome``
   * - ``"failure"``
     - ``action.outcome``
   * - ``"success"``
     - ``event.outcome``
   * - ``"failure"``
     - ``event.outcome``
   * - ``Event.EventData.RuleName``
     - ``rule.name``
   * - ``"network-traffic"``
     - ``action.target``
   * - ``"registry"``
     - ``action.target``
   * - ``Event.EventData.DestinationIp``
     - ``destination.ip``
   * - ``Event.EventData.DestAddress``
     - ``destination.ip``
   * - ``Event.EventData.DestinationPort``
     - ``destination.port``
   * - ``Event.EventData.DestPort``
     - ``destination.port``
   * - ``Event.EventData.DestinationHostname``
     - ``destination.domain``
   * - ``url.domain``
     - ``destination.domain``
   * - ``Event.EventData.DestinationAddress``
     - ``destination.address``
   * - ``Event.EventData.DestAddress``
     - ``destination.address``
   * - ``url.domain``
     - ``destination.address``
