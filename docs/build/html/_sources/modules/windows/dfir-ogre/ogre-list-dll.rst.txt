ogre-list-dll
=============

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``ogre:windows:sysinternals:listdll`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of listdlls - using ANSSI DFIR OGRE

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
   * - ``process_name``
     - ``process.name``
   * - ``to_int(pid)``
     - ``process.pid``
   * - ``command_line``
     - ``process.command_line``
   * - ``base_addr``
     - ``action.properties.base_addr``
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
