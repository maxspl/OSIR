prefetch
========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``eztools:windows:prefetch`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Eric Zimmerman - PECmd.exe

Timeline
--------

.. _tl-windows-zimmerman-prefetch-executed:

.. list-table::
   :header-rows: 1

   * - Relation
     - Message
   * - `executed <rel-windows-zimmerman-prefetch-executed_>`_
     - ``Program {process.name} was executed (last run {timestamp})``

Relationships
-------------

.. _rel-windows-zimmerman-prefetch-executed:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `executed <tl-windows-zimmerman-prefetch-executed_>`_
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
   * - ``"Windows Prefetch"``
     - ``event.provider``
   * - ``"prefetch_entry"``
     - ``event.action``
   * - ``ExecutableName``
     - ``process.name``
   * - ``Hash``
     - ``action.properties.Hash``
   * - ``Version``
     - ``action.properties.Version``
   * - ``custom``
     - 
   * - ``parse_timestamp(LastRun)``
     - ``timestamp``
   * - ``parse_timestamp(LastRun)``
     - ``event.start``
   * - ``parse_timestamp(LastRun)``
     - ``action.properties.LastRun``
   * - ``parse_timestamp(SourceCreated)``
     - ``file.created``
   * - ``parse_timestamp(SourceModified)``
     - ``file.mtime``
   * - ``parse_timestamp(SourceAccessed)``
     - ``file.accessed``
   * - ``to_int(Size)``
     - ``file.size``
   * - ``to_int(RunCount)``
     - ``action.properties.RunCount``
   * - ``parse_timestamp(PreviousRun0)``
     - ``action.properties.PreviousRun0``
   * - ``parse_timestamp(PreviousRun1)``
     - ``action.properties.PreviousRun1``
   * - ``parse_timestamp(PreviousRun2)``
     - ``action.properties.PreviousRun2``
   * - ``parse_timestamp(PreviousRun3)``
     - ``action.properties.PreviousRun3``
   * - ``parse_timestamp(PreviousRun4)``
     - ``action.properties.PreviousRun4``
   * - ``parse_timestamp(PreviousRun5)``
     - ``action.properties.PreviousRun5``
   * - ``parse_timestamp(PreviousRun6)``
     - ``action.properties.PreviousRun6``
   * - ``Volume0Name``
     - ``action.properties.Volume0Name``
   * - ``Volume0Serial``
     - ``action.properties.Volume0Serial``
   * - ``Volume1Name``
     - ``action.properties.Volume1Name``
   * - ``Volume1Serial``
     - ``action.properties.Volume1Serial``
   * - ``parse_timestamp(Volume0Created)``
     - ``action.properties.Volume0Created``
   * - ``parse_timestamp(Volume1Created)``
     - ``action.properties.Volume1Created``
   * - ``split(Directories)``
     - ``action.properties.Directories``
   * - ``split(FilesLoaded)``
     - ``action.properties.FilesLoaded``
