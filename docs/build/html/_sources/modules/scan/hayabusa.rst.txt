hayabusa
========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``hayabusa`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Hayabusa scan of evtx files

Timeline
--------

No timeline messages.

Relationships
-------------

No relationships.

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``custom``
     - 
   * - ``"event"``
     - ``event.kind``
   * - ``"hayabusa"``
     - ``event.module``
   * - ``"hayabusa"``
     - ``agent.type``
   * - ``del(.RuleTitle)``
     - ``rule.name``
   * - ``.rule.name``
     - ``event.reason``
   * - ``downcase(string!(.Level))``
     - ``log.level``
   * - ``downcase(string!(.Level))``
     - ``hayabusa.level``
   * - ``"90"``
     - ``event.severity``
   * - ``"75"``
     - ``event.severity``
   * - ``"50"``
     - ``event.severity``
   * - ``"25"``
     - ``event.severity``
   * - ``del(.Computer)``
     - ``host.name``
   * - ``.Channel``
     - ``hayabusa.channel``
   * - ``.Channel``
     - ``winlog.channel``
   * - ``downcase(string!(.Channel))``
     - ``channel_lower``
   * - ``"windows.security"``
     - ``event.dataset``
   * - ``"windows.system"``
     - ``event.dataset``
   * - ``"windows.defender"``
     - ``event.dataset``
   * - ``"hayabusa." + string!(.channel_lower)``
     - ``event.dataset``
   * - ``to_string!(.EventID)``
     - ``event.code``
   * - ``to_string!(.EventID)``
     - ``winlog.event_id``
   * - ``to_string!(del(.RecordID))``
     - ``winlog.record_id``
   * - ``del(.Details)``
     - ``hayabusa.details``
   * - ``del(.ExtraFieldInfo)``
     - ``hayabusa.extra``
   * - ``.hayabusa.extra.SubjectUserName``
     - ``user.name``
   * - ``.hayabusa.extra.SubjectDomainName``
     - ``user.domain``
   * - ``.hayabusa.extra.SubjectUserSid``
     - ``user.id``
   * - ``.hayabusa.extra.SubjectLogonId``
     - ``winlog.subject.logon_id``
   * - ``.hayabusa.extra.TargetDomainName``
     - ``user.target.domain``
   * - ``.hayabusa.details.SrcComp``
     - ``source.domain``
   * - ``.hayabusa.details.SrcIP``
     - ``source.ip``
   * - ``to_string!(.hayabusa.extra.IpPort)``
     - ``source.port``
   * - ``.hayabusa.details.AuthPkg``
     - ``winlog.logon.authentication_package``
   * - ``.hayabusa.details.Type``
     - ``winlog.logon.type``
   * - ``.hayabusa.extra.LogonProcessName``
     - ``winlog.logon.process.name``
   * - ``.hayabusa.extra.KeyLength``
     - ``winlog.logon.key_length``
   * - ``.hayabusa.details.Path``
     - ``process.executable``
   * - ``.hayabusa.details.Path``
     - ``file.path``
   * - ``basename!(.hayabusa.details.Path)``
     - ``file.name``
   * - ``.hayabusa.details.Svc``
     - ``service.display_name``
   * - ``.hayabusa.details.Acct``
     - ``service.account``
   * - ``.hayabusa.details.StartType``
     - ``service.start_type``
   * - ``.hayabusa.extra.ServiceType``
     - ``service.type``
   * - ``.hayabusa.extra."Product Name"``
     - ``observer.product``
   * - ``.hayabusa.extra."Product Version"``
     - ``observer.version``
   * - ``.hayabusa.extra.FailureReason``
     - ``error.message``
   * - ``.hayabusa.extra.Status``
     - ``winlog.status``
   * - ``.hayabusa.extra.SubStatus``
     - ``winlog.sub_status``
   * - ``.hayabusa.details.TgtUser``
     - ``user.target.name``
   * - ``.hayabusa.extra.TargetUserName``
     - ``user.target.name``
   * - ``.hayabusa.extra.TargetUserSid``
     - ``user.target.id``
   * - ``.hayabusa.extra.TargetSid``
     - ``user.target.id``
   * - ``.hayabusa.details.Proc``
     - ``process.executable``
   * - ``to_int(.hayabusa.extra.ProcessId) ?? null``
     - ``process.pid``
   * - ``[authentication]``
     - ``event.category``
   * - ``[start, denied]``
     - ``event.type``
   * - ``"logon_failed"``
     - ``event.action``
   * - ``"failure"``
     - ``event.outcome``
   * - ``[.source.ip]``
     - ``related.ip``
   * - ``.user.target.name``
     - ``user.name``
   * - ``[.user.name]``
     - ``related.user``
   * - ``[iam]``
     - ``event.category``
   * - ``[change]``
     - ``event.type``
   * - ``"password_reset_attempt"``
     - ``event.action``
   * - ``[.user.target.name]``
     - ``related.user``
   * - ``[process, persistence]``
     - ``event.category``
   * - ``[creation, start]``
     - ``event.type``
   * - ``"service_installed"``
     - ``event.action``
   * - ``basename!(.process.executable)``
     - ``file.name``
   * - ``[.file.path]``
     - ``related.files``
   * - ``[malware, configuration]``
     - ``event.category``
   * - ``[change]``
     - ``event.type``
   * - ``"defender_scanning_disabled"``
     - ``event.action``
   * - ``[authentication]``
     - ``event.category``
   * - ``[protocol]``
     - ``event.type``
   * - ``"ntlmv1_authentication_detected"``
     - ``event.action``
