mactime
=======

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``linux:files:bodyfile`` | name_rex: ``r"bodyfile.*\.jsonl$"``

Description
-----------

Parsing logs from '/bodyfile' in UAC collect

Timeline
--------

.. list-table::
   :header-rows: 1

   * - Relation
     - Message
   * - 
     - ``{file.name} — {event.action}``
   * - 
     - ``{file.name} ({file.size} bytes) — {event.action}``
   * - 
     - ``{file.name} ({file.size} bytes, mode {file.mode}) — Created``
   * - 
     - ``{file.name} ({file.size} bytes, mode {file.mode}) — Created by uid {file.uid}``
   * - 
     - ``{file.name} ({file.size} bytes, mode {file.mode}) — Modified``
   * - 
     - ``{file.name} ({file.size} bytes, mode {file.mode}) — Modified by uid {file.uid}``
   * - 
     - ``{file.name} ({file.size} bytes, mode {file.mode}) — Accessed``
   * - 
     - ``{file.name} ({file.size} bytes, mode {file.mode}) — Accessed by uid {file.uid}``
   * - 
     - ``{file.name} — No activity recorded``

Relationships
-------------

No relationships.

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``to_string!(.Date)``
     - ``timestamp``
   * - ``to_int!(.Size)``
     - ``file.size``
   * - ``to_string!(.Mode)``
     - ``file.mode``
   * - ``to_int!(.UID)``
     - ``file.uid``
   * - ``to_int!(.GID)``
     - ``file.gid``
   * - ``get!(., path: ["File Name"])``
     - ``file.name``
   * - ``to_string!(.Meta)``
     - ``file.meta``
