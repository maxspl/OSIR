prefetch
========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:files:prefetch`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Eric Zimmerman - PECmd.exe

Timeline
--------

.. _tl-windows-prefetch-executed:

.. list-table::
   :header-rows: 1

   * - Relation
     - Message
   * - `executed <rel-windows-prefetch-executed_>`_
     - ``Program {process.name} was executed (last run {timestamp})``

Relationships
-------------

.. _rel-windows-prefetch-executed:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `executed <tl-windows-prefetch-executed_>`_
     - ``process.name``
     - ``file.path``
     - ``recorded in``

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"windows.prefetch"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"event"``
     - ``event.kind``
   * - ``[process]``
     - ``event.category``
   * - ``[start, info]``
     - ``event.type``
   * - ``"Windows Prefetch"``
     - ``event.provider``
   * - ``"prefetch_entry"``
     - ``event.action``
   * - ``"success"``
     - ``event.outcome``
   * - ``SourceFilename``
     - ``file.path``
   * - ``ExecutableName``
     - ``process.name``
   * - ``Hash``
     - ``labels.hash``
   * - ``Version``
     - ``labels.version``
   * - ``parse_timestamp(LastRun)``
     - ``timestamp``
   * - ``parse_timestamp(LastRun)``
     - ``event.start``
   * - ``parse_timestamp(LastRun)``
     - ``labels.last_run``
   * - ``parse_timestamp(SourceCreated)``
     - ``file.created``
   * - ``parse_timestamp(SourceModified)``
     - ``file.mtime``
   * - ``parse_timestamp(SourceAccessed)``
     - ``file.accessed``
   * - ``to_int(Size)``
     - ``file.size``
   * - ``to_int(RunCount)``
     - ``labels.run_count``
   * - ``parse_timestamp(PreviousRun0)``
     - ``labels.previous_run0``
   * - ``parse_timestamp(PreviousRun1)``
     - ``labels.previous_run1``
   * - ``parse_timestamp(PreviousRun2)``
     - ``labels.previous_run2``
   * - ``parse_timestamp(PreviousRun3)``
     - ``labels.previous_run3``
   * - ``parse_timestamp(PreviousRun4)``
     - ``labels.previous_run4``
   * - ``parse_timestamp(PreviousRun5)``
     - ``labels.previous_run5``
   * - ``parse_timestamp(PreviousRun6)``
     - ``labels.previous_run6``
   * - ``Volume0Name``
     - ``labels.volume0_name``
   * - ``Volume0Serial``
     - ``labels.volume0_serial``
   * - ``Volume1Name``
     - ``labels.volume1_name``
   * - ``Volume1Serial``
     - ``labels.volume1_serial``
   * - ``parse_timestamp(Volume0Created)``
     - ``labels.volume0_created``
   * - ``parse_timestamp(Volume1Created)``
     - ``labels.volume1_created``
   * - ``split(Directories)``
     - ``labels.directories``
   * - ``split(FilesLoaded)``
     - ``labels.files_loaded``
