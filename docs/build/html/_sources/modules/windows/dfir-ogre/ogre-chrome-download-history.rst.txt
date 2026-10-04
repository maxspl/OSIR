ogre-chrome-download-history
============================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:ogre:chrome_download_history`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of browser\_download\_history - using ANSSI DFIR OGRE

Timeline
--------

.. _tl-windows-browsers-visited:
.. _tl-windows-browsers-downloaded:
.. _tl-windows-browsers-searched:

.. list-table::
   :header-rows: 1

   * - Relation
     - Message
   * - `visited <rel-windows-browsers-visited_>`_
     - ``User {user.name} visited {url.original}``
   * - `downloaded <rel-windows-browsers-downloaded_>`_
     - ``User {user.name} downloaded {file.name} to {file.path}``
   * - `searched <rel-windows-browsers-searched_>`_
     - ``User {user.name} searched for {labels.search_term}``

Relationships
-------------

.. _rel-windows-browsers-visited:
.. _rel-windows-browsers-downloaded:
.. _rel-windows-browsers-searched:

.. list-table::
   :header-rows: 1

   * - Relation
     - Source
     - Target
     - Type
   * - `visited <tl-windows-browsers-visited_>`_
     - ``user.name``
     - ``url.original``
     - ``visited``
   * - `downloaded <tl-windows-browsers-downloaded_>`_
     - ``user.name``
     - ``file.path``
     - ``downloaded to``
   * - `searched <tl-windows-browsers-searched_>`_
     - ``user.name``
     - ``labels.search_term``
     - ``searched for``

Fields
------

.. list-table::
   :header-rows: 1

   * - Original
     - ECS field
   * - ``encode_json!(.)``
     - ``event.original``
   * - ``"web.browser"``
     - ``event.dataset``
   * - ``"browser"``
     - ``event.module``
   * - ``"event"``
     - ``event.kind``
   * - ``[web]``
     - ``event.category``
   * - ``[access, info]``
     - ``event.type``
   * - ``"Browser artifacts"``
     - ``event.provider``
   * - ``"success"``
     - ``event.outcome``
   * - ``url``
     - ``url.original``
   * - ``title``
     - ``labels.title``
   * - ``to_int(visit_count)``
     - ``labels.visit_count``
   * - ``parse_timestamp(last_visit_time)``
     - ``timestamp``
   * - ``filename``
     - ``file.name``
   * - ``target_path``
     - ``file.path``
   * - ``current_path``
     - ``labels.current_path``
   * - ``to_int(total_bytes)``
     - ``file.size``
   * - ``to_int(received_bytes)``
     - ``labels.received_bytes``
   * - ``to_bool(opened)``
     - ``labels.opened``
   * - ``mime_type``
     - ``labels.mime_type``
   * - ``parse_timestamp(start_time)``
     - ``timestamp``
   * - ``parse_timestamp(start_time)``
     - ``event.start``
   * - ``parse_timestamp(end_time)``
     - ``file.mtime``
   * - ``parse_timestamp(last_access_time)``
     - ``file.accessed``
   * - ``term``
     - ``labels.search_term``
   * - ``normalized_term``
     - ``labels.normalized_term``
   * - ``url``
     - ``url.original``
   * - ``title``
     - ``labels.title``
   * - ``to_int(visit_count)``
     - ``labels.visit_count``
   * - ``to_int(hidden)``
     - ``labels.hidden``
   * - ``ogre_md``
     - ``labels.ogre_md``
   * - ``parse_timestamp(visit_date)``
     - ``timestamp``
   * - ``target_path``
     - ``file.path``
   * - ``url``
     - ``url.original``
   * - ``to_int(total_bytes)``
     - ``file.size``
   * - ``to_int(received_bytes)``
     - ``labels.received_bytes``
   * - ``state``
     - ``labels.state``
   * - ``danger_type``
     - ``labels.danger_type``
   * - ``to_bool(deleted)``
     - ``labels.deleted``
   * - ``interrupt_reason``
     - ``labels.interrupt_reason``
   * - ``to_bool(opened)``
     - ``labels.opened``
   * - ``ogre_md``
     - ``labels.ogre_md``
   * - ``parse_timestamp(start_time)``
     - ``timestamp``
   * - ``parse_timestamp(start_time)``
     - ``event.start``
   * - ``parse_timestamp(end_time)``
     - ``file.mtime``
   * - ``custom``
     - 
