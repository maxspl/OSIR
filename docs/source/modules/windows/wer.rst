wer
===

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:wer`` | name_rex: ``--wer\.jsonl$``

Description
-----------

Parse .wer files

Timeline
--------

No timeline messages.

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``"windows.wer"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``custom``
     - 
   * - ``"event"``
     - ``event.kind``
   * - ``[process]``
     - ``event.category``
   * - ``custom``
     - 
   * - ``"failure"``
     - ``event.outcome``
   * - ``del(.Consent)``
     - ``wer.consent``
   * - ``del(.ConsentKey)``
     - ``wer.consent_key``
   * - ``del(.EtwNonCollectReason)``
     - ``wer.etw_non_collect_reason``
   * - ``custom``
     - 
   * - ``del(.AppPath)``
     - ``process.executable``
   * - ``custom``
     - 
   * - ``del(.OriginalFilename)``
     - ``process.pe.original_file_name``
   * - ``del(.ApplicationIdentity)``
     - ``process.entity_id``
   * - ``del(.AppSessionGuid)``
     - ``process.session_leader.id``
   * - ``del(.TargetAppId)``
     - ``wer.target.app.id``
   * - ``del(.TargetAppVer)``
     - ``wer.target.app.version``
   * - ``del(.TargetAsId)``
     - ``wer.target.as_id``
   * - ``del(.BootId)``
     - ``host.boot.id``
   * - ``del(.Wow64Host)``
     - ``wer.wow64.host``
   * - ``del(.Wow64Guest)``
     - ``wer.wow64.guest``
   * - ``custom``
     - 
   * - ``del(._file)``
     - ``log.file.path``
   * - ``del(.FriendlyEventName)``
     - ``event.reason``
   * - ``del(.ReportDescription)``
     - ``message``
   * - ``custom``
     - 
   * - ``del(.Response)``
     - ``wer.response.raw``
   * - ``custom``
     - 
   * - ``del(.dynamic_signatures)``
     - ``wer.dynamic_signatures``
   * - ``del(.dynamic_signatures_raw)``
     - ``wer.dynamic_signatures_raw``
   * - ``custom``
     - 
   * - ``del(.NsPartner)``
     - ``wer.ns_partner``
   * - ``del(.NsGroup)``
     - ``wer.ns_group``
   * - ``custom``
     - 
   * - ``del(.state)``
     - ``wer.state``
   * - ``del(.loaded_modules)``
     - ``wer.loaded_modules``
   * - ``custom``
     - 
   * - ``del(.ReportType)``
     - ``wer.report_type``
   * - ``del(.ReportIdentifier)``
     - ``wer.report_identifier``
   * - ``del(.IntegratorReportIdentifier)``
     - ``wer.integrator_report_identifier``
   * - ``del(.MetadataHash)``
     - ``wer.metadata_hash``
   * - ``del(.ReportFlags)``
     - ``wer.report_flags``
   * - ``del(.ReportStatus)``
     - ``wer.report_status``
   * - ``del(.ServiceSplit)``
     - ``wer.service_split``
   * - ``del(.UserImpactVector)``
     - ``wer.user_impact_vector``
   * - ``del(.Version)``
     - ``wer.version``
   * - ``custom``
     - 
