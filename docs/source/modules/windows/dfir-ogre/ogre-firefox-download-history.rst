ogre-firefox-download-history
=============================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``ogre:application:firefox:download`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of browser\_download\_history - using ANSSI DFIR OGRE

Timeline
--------

.. _tl-windows-dfir-ogre-browsers-visited:
.. _tl-windows-dfir-ogre-browsers-downloaded:

.. list-table::
   :header-rows: 1

   * - Relation
     - Message
   * - `visited <rel-windows-dfir-ogre-browsers-visited_>`_
     - ``User {user.name} visited {url.original}``
   * - `downloaded <rel-windows-dfir-ogre-browsers-downloaded_>`_
     - ``User {user.name} downloaded {file.name} to {file.path}``

Relationships
-------------

.. _rel-windows-dfir-ogre-browsers-visited:
.. _rel-windows-dfir-ogre-browsers-downloaded:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `visited <tl-windows-dfir-ogre-browsers-visited_>`_
     - ``user.name``
     - ``url.original``
     - ``visited``
   * - `downloaded <tl-windows-dfir-ogre-browsers-downloaded_>`_
     - ``user.name``
     - ``file.path``
     - ``downloaded to``

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``url``
     - ``url.original``
   * - ``title``
     - ``action.properties.title``
   * - ``to_int(visit_count)``
     - ``action.properties.visit_count``
   * - ``to_int(hidden)``
     - ``action.properties.hidden``
   * - ``referer``
     - ``action.properties.referer``
   * - ``parse_timestamp(visit_date)``
     - ``timestamp``
   * - ``target_path``
     - ``file.path``
   * - ``url``
     - ``url.original``
   * - ``to_int(total_bytes)``
     - ``file.size``
   * - ``to_int(received_bytes)``
     - ``action.properties.received_bytes``
   * - ``state``
     - ``action.properties.state``
   * - ``danger_type``
     - ``action.properties.danger_type``
   * - ``to_bool(deleted)``
     - ``action.properties.deleted``
   * - ``interrupt_reason``
     - ``action.properties.interrupt_reason``
   * - ``to_bool(opened)``
     - ``action.properties.opened``
   * - ``parse_timestamp(start_time)``
     - ``timestamp``
   * - ``parse_timestamp(start_time)``
     - ``event.start``
   * - ``parse_timestamp(end_time)``
     - ``file.mtime``
   * - ``parse_timestamp(end_time)``
     - ``event.end``
   * - ``custom``
     - 
