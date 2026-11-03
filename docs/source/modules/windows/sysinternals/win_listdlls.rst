win_listdlls
============

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:sysinternals:listdll`` | name_rex: ``r"--win_listdlls\.jsonl$"``

Description
-----------

Parse Listdlls.txt from DFIR ORC (Listdlls.exe command)

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
   * - ``"Sysinternals ListDLLs"``
     - ``event.provider``
   * - ``type``
     - ``action.properties.type``
   * - ``process_name``
     - ``process.name``
   * - ``to_int(pid)``
     - ``process.pid``
   * - ``base_address``
     - ``action.properties.base_address``
   * - ``size``
     - ``action.properties.size``
   * - ``path``
     - ``dll.path``
   * - ``path``
     - ``file.path``
   * - ``split!(to_string!(.path), "\\")[-1]``
     - ``dll.name``
   * - ``split!(to_string!(.path), "\\")[-1]``
     - ``file.name``
   * - ``path``
     - ``process.executable``
