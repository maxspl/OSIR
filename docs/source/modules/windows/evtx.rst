evtx
====

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:evtx`` | name_rex: ``r"\.evtx.*\.jsonl$"``
   * ``windows:evtx:powershell`` | name_rex: ``r"PowerShell\.evtx.*\.jsonl$"``
   * ``windows:evtx:powershell:operational`` | name_rex: ``r"PowerShell.*Operational\.evtx.*\.jsonl$"``
   * ``windows:evtx:security`` | name_rex: ``r"Security\.evtx.*\.jsonl$"``
   * ``windows:evtx:sysmon`` | name_rex: ``r"Sysmon.*\.evtx.*\.jsonl$"``
   * ``windows:evtx:system`` | name_rex: ``r"System\.evtx.*\.jsonl$"``

Description
-----------

Parsing of EVTX collected by DFIR ORC or in the filesystem

Timeline
--------

.. _tl-windows-evtx-evtx-4624:
.. _tl-windows-evtx-evtx-4624-2:
.. _tl-windows-evtx-evtx-4625:
.. _tl-windows-evtx-evtx-4625-2:
.. _tl-windows-evtx-evtx-4634:
.. _tl-windows-evtx-evtx-4648:
.. _tl-windows-evtx-evtx-4648-2:
.. _tl-windows-evtx-evtx-4657:
.. _tl-windows-evtx-evtx-4662:
.. _tl-windows-evtx-evtx-4672:
.. _tl-windows-evtx-evtx-4688:
.. _tl-windows-evtx-evtx-4689:
.. _tl-windows-evtx-evtx-4720:
.. _tl-windows-evtx-evtx-4722:
.. _tl-windows-evtx-evtx-4723:
.. _tl-windows-evtx-evtx-4723-2:
.. _tl-windows-evtx-evtx-4725:
.. _tl-windows-evtx-evtx-4726:
.. _tl-windows-evtx-evtx-4727:
.. _tl-windows-evtx-evtx-4768:
.. _tl-windows-evtx-evtx-4768-2:
.. _tl-windows-evtx-evtx-4769:
.. _tl-windows-evtx-evtx-4769-2:
.. _tl-windows-evtx-evtx-4771:
.. _tl-windows-evtx-evtx-4776:
.. _tl-windows-evtx-evtx-4776-2:
.. _tl-windows-evtx-evtx-4798:
.. _tl-windows-evtx-evtx-4799:
.. _tl-windows-evtx-evtx-4825:
.. _tl-windows-evtx-evtx-1149:
.. _tl-windows-evtx-evtx-21:
.. _tl-windows-evtx-evtx-25:
.. _tl-windows-evtx-evtx-5145:
.. _tl-windows-evtx-evtx-5145-2:
.. _tl-windows-evtx-evtx-5154:
.. _tl-windows-evtx-evtx-5156:
.. _tl-windows-evtx-evtx-1:
.. _tl-windows-evtx-evtx-2:
.. _tl-windows-evtx-evtx-3:
.. _tl-windows-evtx-evtx-5:
.. _tl-windows-evtx-evtx-6:
.. _tl-windows-evtx-evtx-7:
.. _tl-windows-evtx-evtx-8:
.. _tl-windows-evtx-evtx-9:
.. _tl-windows-evtx-evtx-10:

.. list-table::
   :header-rows: 1

   * - Relation
     - Message
   * - 
     - ``Hostname: {host.name} - Source: {event.provider} - EventID: {action.id}``
   * - 
     - ``Hostname: {host.name} - {action.name}``
   * - `evtx-4624 <rel-windows-evtx-evtx-4624_>`_
     - ``{action.properties.TargetDomainName}\\{action.properties.TargetUserName} logged on to {host.name} (LogonType {action.properties.LogonType})``
   * - `evtx-4624-2 <rel-windows-evtx-evtx-4624-2_>`_
     - ``{action.properties.TargetDomainName}\\{action.properties.TargetUserName} logged on to {host.name} from IP {source.ip} (LogonType {action.properties.LogonType})``
   * - `evtx-4625 <rel-windows-evtx-evtx-4625_>`_
     - ``{action.properties.TargetDomainName}\\{action.properties.TargetUserName} failed to log on to {host.name} (LogonType {action.properties.LogonType})``
   * - `evtx-4625-2 <rel-windows-evtx-evtx-4625-2_>`_
     - ``{action.properties.TargetDomainName}\\{action.properties.TargetUserName} failed to log on to {host.name} from IP {source.ip} (LogonType {action.properties.LogonType})``
   * - `evtx-4634 <rel-windows-evtx-evtx-4634_>`_
     - ``{action.properties.TargetDomainName}\\{action.properties.TargetUserName} logged off from {host.name}``
   * - `evtx-4648 <rel-windows-evtx-evtx-4648_>`_
     - ``{action.properties.TargetDomainName}\\{action.properties.TargetUserName} attempted to log on to {action.properties.TargetServerName} using explicit credentials``
   * - `evtx-4648-2 <rel-windows-evtx-evtx-4648-2_>`_
     - ``{action.properties.TargetDomainName}\\{action.properties.TargetUserName} attempted to log on to {host.name} using explicit credentials``
   * - `evtx-4657 <rel-windows-evtx-evtx-4657_>`_
     - ``{user.domain}\\{user.name} modified the value {action.properties.ObjectValueName} of the registry key {action.properties.ObjectName} to {action.properties.NewValue} on {host.name}``
   * - `evtx-4662 <rel-windows-evtx-evtx-4662_>`_
     - ``{user.domain}\\{user.name} accessed the object {action.properties.ObjectName} on {host.name}``
   * - `evtx-4672 <rel-windows-evtx-evtx-4672_>`_
     - ``{user.domain}\\{user.name} logged on to {host.name} with special privileges``
   * - `evtx-4688 <rel-windows-evtx-evtx-4688_>`_
     - ``{user.domain}\\{user.name} executed {process.command_line} on {host.name}``
   * - `evtx-4689 <rel-windows-evtx-evtx-4689_>`_
     - ``Process {process.name} exited. It was executed by {user.domain}\\{user.name} on {host.name}``
   * - `evtx-4720 <rel-windows-evtx-evtx-4720_>`_
     - ``{user.domain}\\{user.name} created account {action.properties.TargetDomainName}\\{action.properties.TargetUserName} on {host.name}``
   * - `evtx-4722 <rel-windows-evtx-evtx-4722_>`_
     - ``{user.domain}\\{user.name} enabled account {action.properties.TargetDomainName}\\{action.properties.TargetUserName}``
   * - `evtx-4723 <rel-windows-evtx-evtx-4723_>`_
     - ``{user.domain}\\{user.name} changed their password on {host.name}``
   * - `evtx-4723-2 <rel-windows-evtx-evtx-4723-2_>`_
     - ``{user.domain}\\{user.name} failed to change their password on {host.name}``
   * - `evtx-4725 <rel-windows-evtx-evtx-4725_>`_
     - ``{user.domain}\\{user.name} disabled account {action.properties.TargetDomainName}\\{action.properties.TargetUserName}``
   * - `evtx-4726 <rel-windows-evtx-evtx-4726_>`_
     - ``{user.domain}\\{user.name} deleted account {action.properties.TargetDomainName}\\{action.properties.TargetUserName} on {host.name}``
   * - `evtx-4727 <rel-windows-evtx-evtx-4727_>`_
     - ``{user.domain}\\{user.name} created group {action.properties.TargetDomainName}\\{action.properties.TargetUserName}``
   * - `evtx-4768 <rel-windows-evtx-evtx-4768_>`_
     - ``{action.properties.TargetDomainName}\\{action.properties.TargetUserName} failed to authenticate from {source.ip} (Error Code: {action.properties.Status})``
   * - `evtx-4768-2 <rel-windows-evtx-evtx-4768-2_>`_
     - ``{action.properties.TargetDomainName}\\{action.properties.TargetUserName} successfully authenticated from {source.ip}``
   * - `evtx-4769 <rel-windows-evtx-evtx-4769_>`_
     - ``{action.properties.TargetDomainName}\\{action.properties.TargetUserName} was denied a service ticket for {action.properties.ServiceName} from {source.ip} (Error Code: {action.properties.Status})``
   * - `evtx-4769-2 <rel-windows-evtx-evtx-4769-2_>`_
     - ``{action.properties.TargetDomainName}\\{action.properties.TargetUserName} was granted a service ticket for {action.properties.ServiceName} from {source.ip}``
   * - `evtx-4771 <rel-windows-evtx-evtx-4771_>`_
     - ``{action.properties.TargetUserName} failed to authenticate from {source.ip}``
   * - `evtx-4776 <rel-windows-evtx-evtx-4776_>`_
     - ``{action.properties.TargetUserName} failed to authenticate on {action.properties.Workstation} (Reason: {action.properties.Status})``
   * - `evtx-4776-2 <rel-windows-evtx-evtx-4776-2_>`_
     - ``{action.properties.TargetUserName} successfully authenticated on {action.properties.Workstation}``
   * - `evtx-4798 <rel-windows-evtx-evtx-4798_>`_
     - ``{user.domain}\\{user.name} enumerated local groups of {action.properties.TargetDomainName}\\{action.properties.TargetUserName} on {host.name}``
   * - `evtx-4799 <rel-windows-evtx-evtx-4799_>`_
     - ``{user.domain}\\{user.name} enumerated members of local group {action.properties.TargetUserName} on {host.name}``
   * - `evtx-4825 <rel-windows-evtx-evtx-4825_>`_
     - ``Authenticated user {user.name} was denied the access to Remote Desktop to {host.name} from IP {action.properties.ClientAddress}``
   * - `evtx-1149 <rel-windows-evtx-evtx-1149_>`_
     - ``{user.domain}\\{user.name} successfully authenticated over RDP to {host.name} from IP {source.ip}``
   * - `evtx-21 <rel-windows-evtx-evtx-21_>`_
     - ``{user.domain}\\{user.name} opened session {action.properties.SessionID} on {host.name} (source: {action.properties.Address})``
   * - 
     - ``{user.domain}\\{user.name} session {action.properties.SessionID} shell started on {host.name}``
   * - 
     - ``{user.domain}\\{user.name} logged off session {action.properties.SessionID} on {host.name}``
   * - 
     - ``{user.domain}\\{user.name} disconnected from session {action.properties.SessionID} on {host.name} (source: {action.properties.Address})``
   * - `evtx-25 <rel-windows-evtx-evtx-25_>`_
     - ``{user.domain}\\{user.name} reconnected to session {action.properties.SessionID} on {host.name} (source: {action.properties.Address})``
   * - `evtx-5145 <rel-windows-evtx-evtx-5145_>`_
     - ``{user.domain}\\{user.name} was granted access to {action.properties.ShareName}\\{action.properties.RelativeTargetName} from IP {source.ip}``
   * - `evtx-5145-2 <rel-windows-evtx-evtx-5145-2_>`_
     - ``{user.domain}\\{user.name} was denied access to {action.properties.ShareName}\\{action.properties.RelativeTargetName} from IP {source.ip}``
   * - `evtx-5154 <rel-windows-evtx-evtx-5154_>`_
     - ``{action.properties.Application} was allowed to listen on {source.ip}:{source.port} on {host.name}``
   * - `evtx-5156 <rel-windows-evtx-evtx-5156_>`_
     - ``{host.name} allowed a connection from {source.ip}:{source.port} to {destination.ip}:{destination.port}``
   * - 
     - ``{user.domain}\\{user.name} executed PowerShell code on {host.name}``
   * - 
     - ``{user.domain}\\{user.name} executed PowerShell code on {host.name}``
   * - 
     - ``Started invocation of PowerShell ScriptBlock on {host.name}``
   * - 
     - ``Completed invocation of PowerShell ScriptBlock on {host.name}``
   * - 
     - ``Vault credentials were read by {action.properties.SubjectUserName} on {host.name}``
   * - 
     - ``PowerShell console is starting up on {host.name}``
   * - 
     - ``PowerShell console is ready for user input on {host.name}``
   * - 
     - ``Windows PowerShell has started an IPC listening thread on {host.name}``
   * - `evtx-1 <rel-windows-evtx-evtx-1_>`_
     - ``Process {process.executable} created by {user.name} on {host.name}``
   * - `evtx-2 <rel-windows-evtx-evtx-2_>`_
     - ``Process {process.executable} changed the creation time of the file {file.name} on {host.name}``
   * - `evtx-3 <rel-windows-evtx-evtx-3_>`_
     - ``Network connection from {source.ip} to {destination.ip}:{destination.port} by {process.executable} on {host.name}``
   * - 
     - ``Sysmon service state changed to {action.properties.State} on {host.name}``
   * - `evtx-5 <rel-windows-evtx-evtx-5_>`_
     - ``Process {process.executable} terminated on {host.name}``
   * - `evtx-6 <rel-windows-evtx-evtx-6_>`_
     - ``Driver {process.executable} loaded on {host.name}``
   * - `evtx-7 <rel-windows-evtx-evtx-7_>`_
     - ``Process {process.executable} loaded image {action.properties.ImageLoaded} on {host.name}``
   * - `evtx-8 <rel-windows-evtx-evtx-8_>`_
     - ``Process {action.properties.SourceImage} created a thread in process {action.properties.TargetImage} on {host.name}``
   * - `evtx-9 <rel-windows-evtx-evtx-9_>`_
     - ``Process {process.executable} read on {action.properties.Device} device on {host.name}``
   * - `evtx-10 <rel-windows-evtx-evtx-10_>`_
     - ``{action.properties.SourceImage} was granted {action.properties.GrantedAccess} access to {action.properties.TargetImage} on {host.name}``
   * - 
     - ``{file.name} created by {process.executable} on {host.name}``
   * - 
     - ``Registry key {action.properties.TargetObject} created by {process.executable} on {host.name}``
   * - 
     - ``Registry value {action.properties.TargetObject} created by {process.executable} on {host.name}``
   * - 
     - ``Registry key {action.properties.TargetObject} deleted by {process.executable} on {host.name}``
   * - 
     - ``Registry value {action.properties.TargetObject} deleted by {process.executable} on {host.name}``
   * - 
     - ``Registry key {action.properties.TargetObject} set by {process.executable} on {host.name}``
   * - 
     - ``Registry key {action.properties.TargetObject} renamed to {action.properties.NewName} by {process.executable} on {host.name}``
   * - 
     - ``Registry value {action.properties.TargetObject} renamed to {action.properties.NewName} by {process.executable} on {host.name}``
   * - 
     - ``{action.properties.Image} added a named stream to file {action.properties.TargetFilename} on {host.name}``
   * - 
     - ``Sysmon configuration was updated on {host.name}``
   * - 
     - ``Pipe {action.properties.PipeName} created by {process.executable} on {host.name}``
   * - 
     - ``Pipe {action.properties.PipeName} connected by {process.executable} on {host.name}``
   * - 
     - ``{action.properties.User} created WMI Event Filter {action.properties.Name} on {host.name}``
   * - 
     - ``{action.properties.User} {action.properties.Operation} WMI Consumer {action.properties.Name} on {host.name}``
   * - 
     - ``{action.properties.User} bound WMI Consumer {action.properties.Consumer} to Event Filter {action.properties.Filter} on {host.name}``
   * - 
     - ``{host.name} performed a DNS query for name {dns.question.name} (status: {dns.response_code})``
   * - 
     - ``An anti-malware scan started on {host.name}``
   * - 
     - ``An anti-malware scan finished on {host.name}``
   * - 
     - ``An anti-malware scan was stopped before it finished on {host.name}``
   * - 
     - ``Microsoft Defender Antivirus client is up and running in a healthy state on {host.name}``
   * - 
     - ``Windows Update successfully found updates on {host.name}``
   * - 
     - ``W32time Service configuration parameters have been updated on {host.name}``
   * - 
     - ``Updated Windows Defender status successfully to SECURITY_PRODUCT_STATE_ON on {host.name}``

Relationships
-------------

.. _rel-windows-evtx-evtx-4624:
.. _rel-windows-evtx-evtx-4624-2:
.. _rel-windows-evtx-evtx-4625:
.. _rel-windows-evtx-evtx-4625-2:
.. _rel-windows-evtx-evtx-4634:
.. _rel-windows-evtx-evtx-4648:
.. _rel-windows-evtx-evtx-4648-2:
.. _rel-windows-evtx-evtx-4657:
.. _rel-windows-evtx-evtx-4662:
.. _rel-windows-evtx-evtx-4672:
.. _rel-windows-evtx-evtx-4688:
.. _rel-windows-evtx-evtx-4689:
.. _rel-windows-evtx-evtx-4720:
.. _rel-windows-evtx-evtx-4722:
.. _rel-windows-evtx-evtx-4723:
.. _rel-windows-evtx-evtx-4723-2:
.. _rel-windows-evtx-evtx-4725:
.. _rel-windows-evtx-evtx-4726:
.. _rel-windows-evtx-evtx-4727:
.. _rel-windows-evtx-evtx-4768:
.. _rel-windows-evtx-evtx-4768-2:
.. _rel-windows-evtx-evtx-4769:
.. _rel-windows-evtx-evtx-4769-2:
.. _rel-windows-evtx-evtx-4771:
.. _rel-windows-evtx-evtx-4776:
.. _rel-windows-evtx-evtx-4776-2:
.. _rel-windows-evtx-evtx-4798:
.. _rel-windows-evtx-evtx-4799:
.. _rel-windows-evtx-evtx-4825:
.. _rel-windows-evtx-evtx-1149:
.. _rel-windows-evtx-evtx-21:
.. _rel-windows-evtx-evtx-25:
.. _rel-windows-evtx-evtx-5145:
.. _rel-windows-evtx-evtx-5145-2:
.. _rel-windows-evtx-evtx-5154:
.. _rel-windows-evtx-evtx-5156:
.. _rel-windows-evtx-evtx-1:
.. _rel-windows-evtx-evtx-2:
.. _rel-windows-evtx-evtx-3:
.. _rel-windows-evtx-evtx-5:
.. _rel-windows-evtx-evtx-6:
.. _rel-windows-evtx-evtx-7:
.. _rel-windows-evtx-evtx-8:
.. _rel-windows-evtx-evtx-9:
.. _rel-windows-evtx-evtx-10:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `evtx-4624 <tl-windows-evtx-evtx-4624_>`_
     - ``action.properties.TargetUserName``
     - ``host.name``
     - ``logged on to``
   * - `evtx-4624-2 <tl-windows-evtx-evtx-4624-2_>`_
     - ``action.properties.TargetUserName``
     - ``host.name``
     - ``logged on to``
   * - `evtx-4624-2 <tl-windows-evtx-evtx-4624-2_>`_
     - ``action.properties.TargetUserName``
     - ``source.ip``
     - ``connected from``
   * - `evtx-4625 <tl-windows-evtx-evtx-4625_>`_
     - ``action.properties.TargetUserName``
     - ``host.name``
     - ``failed to log on to``
   * - `evtx-4625-2 <tl-windows-evtx-evtx-4625-2_>`_
     - ``action.properties.TargetUserName``
     - ``host.name``
     - ``failed to log on to``
   * - `evtx-4625-2 <tl-windows-evtx-evtx-4625-2_>`_
     - ``action.properties.TargetUserName``
     - ``source.ip``
     - ``connected from``
   * - `evtx-4634 <tl-windows-evtx-evtx-4634_>`_
     - ``action.properties.TargetUserName``
     - ``host.name``
     - ``logged off from``
   * - `evtx-4648 <tl-windows-evtx-evtx-4648_>`_
     - ``action.properties.TargetUserName``
     - ``action.properties.TargetServerName``
     - ``attempted to log on to``
   * - `evtx-4648-2 <tl-windows-evtx-evtx-4648-2_>`_
     - ``action.properties.TargetUserName``
     - ``host.name``
     - ``attempted to log on to``
   * - `evtx-4657 <tl-windows-evtx-evtx-4657_>`_
     - ``user.name``
     - ``action.properties.ObjectName``
     - ``modified registry value from``
   * - `evtx-4662 <tl-windows-evtx-evtx-4662_>`_
     - ``user.name``
     - ``action.properties.ObjectName``
     - ``accessed``
   * - `evtx-4672 <tl-windows-evtx-evtx-4672_>`_
     - ``user.name``
     - ``host.name``
     - ``logged on to``
   * - `evtx-4688 <tl-windows-evtx-evtx-4688_>`_
     - ``user.name``
     - ``process.command_line``
     - ``executed``
   * - `evtx-4688 <tl-windows-evtx-evtx-4688_>`_
     - ``user.name``
     - ``process.parent.executable``
     - ``executed``
   * - `evtx-4688 <tl-windows-evtx-evtx-4688_>`_
     - ``process.command_line``
     - ``host.name``
     - ``executed on``
   * - `evtx-4688 <tl-windows-evtx-evtx-4688_>`_
     - ``process.command_line``
     - ``process.executable``
     - ``uses executable``
   * - `evtx-4688 <tl-windows-evtx-evtx-4688_>`_
     - ``process.parent.executable``
     - ``host.name``
     - ``executed on``
   * - `evtx-4688 <tl-windows-evtx-evtx-4688_>`_
     - ``process.parent.executable``
     - ``process.command_line``
     - ``started``
   * - `evtx-4689 <tl-windows-evtx-evtx-4689_>`_
     - ``user.name``
     - ``process.executable``
     - ``executed``
   * - `evtx-4720 <tl-windows-evtx-evtx-4720_>`_
     - ``user.name``
     - ``action.properties.TargetDomainName``
     - ``created account``
   * - `evtx-4722 <tl-windows-evtx-evtx-4722_>`_
     - ``user.name``
     - ``action.properties.TargetDomainName``
     - ``enabled account``
   * - `evtx-4723 <tl-windows-evtx-evtx-4723_>`_
     - ``user.name``
     - ``host.name``
     - ``changed their password on``
   * - `evtx-4723-2 <tl-windows-evtx-evtx-4723-2_>`_
     - ``user.name``
     - ``host.name``
     - ``failed to change their password on``
   * - `evtx-4725 <tl-windows-evtx-evtx-4725_>`_
     - ``user.name``
     - ``action.properties.TargetUserName``
     - ``disabled account``
   * - `evtx-4726 <tl-windows-evtx-evtx-4726_>`_
     - ``user.name``
     - ``action.properties.TargetUserName``
     - ``deleted account``
   * - `evtx-4727 <tl-windows-evtx-evtx-4727_>`_
     - ``user.name``
     - ``action.properties.TargetUserName``
     - ``created group``
   * - `evtx-4768 <tl-windows-evtx-evtx-4768_>`_
     - ``action.properties.TargetUserName``
     - ``source.ip``
     - ``failed to log on to``
   * - `evtx-4768-2 <tl-windows-evtx-evtx-4768-2_>`_
     - ``action.properties.TargetUserName``
     - ``source.ip``
     - ``logged on to``
   * - `evtx-4769 <tl-windows-evtx-evtx-4769_>`_
     - ``action.properties.TargetUserName``
     - ``action.properties.ServiceName``
     - ``was denied a ticket for``
   * - `evtx-4769-2 <tl-windows-evtx-evtx-4769-2_>`_
     - ``action.properties.TargetUserName``
     - ``action.properties.ServiceName``
     - ``was granted a ticket for``
   * - `evtx-4771 <tl-windows-evtx-evtx-4771_>`_
     - ``action.properties.TargetUserName``
     - ``source.ip``
     - ``failed to authenticate on``
   * - `evtx-4776 <tl-windows-evtx-evtx-4776_>`_
     - ``action.properties.TargetUserName``
     - ``action.properties.Workstation``
     - ``failed to log on to``
   * - `evtx-4776-2 <tl-windows-evtx-evtx-4776-2_>`_
     - ``action.properties.TargetUserName``
     - ``action.properties.Workstation``
     - ``logged on to``
   * - `evtx-4798 <tl-windows-evtx-evtx-4798_>`_
     - ``user.name``
     - ``action.properties.TargetUserName``
     - ``enumerated local groups of``
   * - `evtx-4799 <tl-windows-evtx-evtx-4799_>`_
     - ``user.name``
     - ``action.properties.TargetUserName``
     - ``enumerated members of``
   * - `evtx-4825 <tl-windows-evtx-evtx-4825_>`_
     - ``user.name``
     - ``host.name``
     - ``was denied RDP access to``
   * - `evtx-1149 <tl-windows-evtx-evtx-1149_>`_
     - ``user.name``
     - ``host.name``
     - ``authenticated over RDP to``
   * - `evtx-1149 <tl-windows-evtx-evtx-1149_>`_
     - ``user.name``
     - ``source.ip``
     - ``connected from``
   * - `evtx-21 <tl-windows-evtx-evtx-21_>`_
     - ``user.name``
     - ``host.name``
     - ``logged on to``
   * - `evtx-25 <tl-windows-evtx-evtx-25_>`_
     - ``user.name``
     - ``host.name``
     - ``logged on to``
   * - `evtx-5145 <tl-windows-evtx-evtx-5145_>`_
     - ``user.name``
     - ``action.properties.RelativeTargetName``
     - ``accessed shared file``
   * - `evtx-5145-2 <tl-windows-evtx-evtx-5145-2_>`_
     - ``user.name``
     - ``action.properties.RelativeTargetName``
     - ``failed to access shared file``
   * - `evtx-5154 <tl-windows-evtx-evtx-5154_>`_
     - ``action.properties.Application``
     - ``host.name``
     - ``listened to port on``
   * - `evtx-5156 <tl-windows-evtx-evtx-5156_>`_
     - ``source.ip``
     - ``destination.ip``
     - ``connected to``
   * - `evtx-1 <tl-windows-evtx-evtx-1_>`_
     - ``user.name``
     - ``process.command_line``
     - ``executed``
   * - `evtx-1 <tl-windows-evtx-evtx-1_>`_
     - ``process.command_line``
     - ``host.name``
     - ``executed on``
   * - `evtx-1 <tl-windows-evtx-evtx-1_>`_
     - ``process.command_line``
     - ``process.executable``
     - ``uses executable``
   * - `evtx-1 <tl-windows-evtx-evtx-1_>`_
     - ``process.parent.command_line``
     - ``process.parent.name``
     - ``uses executable``
   * - `evtx-1 <tl-windows-evtx-evtx-1_>`_
     - ``process.parent.command_line``
     - ``host.name``
     - ``executed on``
   * - `evtx-1 <tl-windows-evtx-evtx-1_>`_
     - ``process.parent.command_line``
     - ``process.command_line``
     - ``started``
   * - `evtx-2 <tl-windows-evtx-evtx-2_>`_
     - ``process.executable``
     - ``file.name``
     - ``changed creation time of``
   * - `evtx-2 <tl-windows-evtx-evtx-2_>`_
     - ``process.executable``
     - ``host.name``
     - ``executed on``
   * - `evtx-3 <tl-windows-evtx-evtx-3_>`_
     - ``source.ip``
     - ``destination.ip``
     - ``connected to``
   * - `evtx-5 <tl-windows-evtx-evtx-5_>`_
     - ``process.executable``
     - ``host.name``
     - ``terminated on``
   * - `evtx-6 <tl-windows-evtx-evtx-6_>`_
     - ``process.executable``
     - ``host.name``
     - ``loaded on``
   * - `evtx-7 <tl-windows-evtx-evtx-7_>`_
     - ``process.executable``
     - ``host.name``
     - ``executed on``
   * - `evtx-7 <tl-windows-evtx-evtx-7_>`_
     - ``process.executable``
     - ``action.properties.ImageLoaded``
     - ``loaded image``
   * - `evtx-8 <tl-windows-evtx-evtx-8_>`_
     - ``action.properties.SourceImage``
     - ``host.name``
     - ``executed on``
   * - `evtx-8 <tl-windows-evtx-evtx-8_>`_
     - ``action.properties.TargetImage``
     - ``host.name``
     - ``executed on``
   * - `evtx-8 <tl-windows-evtx-evtx-8_>`_
     - ``action.properties.SourceImage``
     - ``action.properties.TargetImage``
     - ``created thread in``
   * - `evtx-9 <tl-windows-evtx-evtx-9_>`_
     - ``process.executable``
     - ``host.name``
     - ``executed on``
   * - `evtx-9 <tl-windows-evtx-evtx-9_>`_
     - ``process.executable``
     - ``action.properties.Device``
     - ``read on``
   * - `evtx-10 <tl-windows-evtx-evtx-10_>`_
     - ``action.properties.SourceImage``
     - ``host.name``
     - ``executed on``
   * - `evtx-10 <tl-windows-evtx-evtx-10_>`_
     - ``action.properties.TargetImage``
     - ``host.name``
     - ``executed on``
   * - `evtx-10 <tl-windows-evtx-evtx-10_>`_
     - ``action.properties.SourceImage``
     - ``action.properties.TargetImage``
     - ``was granted access to``

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
