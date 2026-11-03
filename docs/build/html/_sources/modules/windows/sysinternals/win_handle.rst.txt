win_handle
==========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:sysinternals:handle`` | name_rex: ``r"--win_handle\.jsonl$"``

Description
-----------

Parse handle from DFIR ORC (handle.exe /a command)

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
   * - ``"Sysinternals Handle"``
     - ``event.provider``
   * - ``process_name``
     - ``process.name``
   * - ``to_int(pid)``
     - ``process.pid``
   * - ``pid``
     - ``action.properties.pid``
   * - ``handle_id``
     - ``action.properties.handle_id``
   * - ``handle_type``
     - ``action.properties.handle_type``
   * - ``name``
     - ``action.properties.name``
   * - ``rights``
     - ``action.properties.rights``
   * - ``user``
     - ``action.properties.user``
   * - ``split!(to_string!(.action.properties.user), "\\")[-1]``
     - ``user.name``
   * - ``get!(parse_regex(to_string!(.action.properties.user), r'^(?:\\)?(?<domain>[^\\]+(?:\\[^\\]+)*)\\(?<name>[^\\]+)$') ?? { "domain": "" }, ["domain"])``
     - ``user.domain``
   * - ``to_string!(.user.domain) + "\\" + to_string!(.user.name)``
     - ``user.full_name``
   * - ``name``
     - ``file.path``
   * - ``[file]``
     - ``event.category``
   * - ``[process]``
     - ``event.category``
