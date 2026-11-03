browsers
========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``application:browser:chrome`` | name_rex: ``r".*chrome.*\.csv$"``
   * ``application:chrome:cookies`` | name_rex: ``r".*chrome.*_cookies\.csv$"``
   * ``application:chrome:download`` | name_rex: ``r".*chrome.*_downloads\.csv$"``
   * ``application:chrome:history`` | name_rex: ``r".*chrome.*_history\.csv$"``
   * ``application:browser:edge`` | name_rex: ``r".*edge.*\.csv$"``
   * ``application:edge:cookies`` | name_rex: ``r".*edge.*_cookies\.csv$"``
   * ``application:edge:download`` | name_rex: ``r".*edge.*_downloads\.csv$"``
   * ``application:edge:history`` | name_rex: ``r".*edge.*_history\.csv$"``
   * ``application:browser:firefox`` | name_rex: ``r".*firefox.*\.csv$"``
   * ``application:firefox:bookmarks`` | name_rex: ``r".*firefox.*_bookmarks\.csv$"``
   * ``application:firefox:cookies`` | name_rex: ``r".*firefox.*_cookies\.csv$"``
   * ``application:firefox:download`` | name_rex: ``r".*firefox.*_downloads\.csv$"``
   * ``application:firefox:history`` | name_rex: ``r".*firefox.*_history\.csv$"``
   * ``application:firefox:historyvisits`` | name_rex: ``r".*firefox.*_historyvisits\.csv$"``
   * ``application:firefox:metadata`` | name_rex: ``r".*firefox.*_metadata\.csv$"``

Description
-----------

Parsing of browsers artifact.

Timeline
--------

.. _tl-windows-browsers-visited:
.. _tl-windows-browsers-downloaded:
.. _tl-windows-browsers-firefox-downloaded:
.. _tl-windows-browsers-visited-ff-historyvisits:
.. _tl-windows-browsers-bookmarked:
.. _tl-windows-browsers-searched:

.. list-table::
   :header-rows: 1

   * - Relation
     - Message
   * - `visited <rel-windows-browsers-visited_>`_
     - ``User {user.name} visited {url.original}``
   * - `downloaded <rel-windows-browsers-downloaded_>`_
     - ``User {user.name} downloaded {file.name} to {file.path}``
   * - `firefox-downloaded <rel-windows-browsers-firefox-downloaded_>`_
     - ``User {user.name} downloaded {file.name} from {url.original}``
   * - `visited-ff-historyvisits <rel-windows-browsers-visited-ff-historyvisits_>`_
     - ``User {user.name} visited {url.original}``
   * - `bookmarked <rel-windows-browsers-bookmarked_>`_
     - ``User {user.name} bookmarked {action.properties.title}``
   * - `searched <rel-windows-browsers-searched_>`_
     - ``User {user.name} searched for {action.properties.term}``

Relationships
-------------

.. _rel-windows-browsers-visited:
.. _rel-windows-browsers-downloaded:
.. _rel-windows-browsers-firefox-downloaded:
.. _rel-windows-browsers-visited-ff-historyvisits:
.. _rel-windows-browsers-bookmarked:
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
   * - `firefox-downloaded <tl-windows-browsers-firefox-downloaded_>`_
     - ``user.name``
     - ``url.original``
     - ``downloaded``
   * - `visited-ff-historyvisits <tl-windows-browsers-visited-ff-historyvisits_>`_
     - ``user.name``
     - ``url.original``
     - ``visited``
   * - `bookmarked <tl-windows-browsers-bookmarked_>`_
     - ``user.name``
     - ``action.properties.title``
     - ``bookmarked``
   * - `searched <tl-windows-browsers-searched_>`_
     - ``user.name``
     - ``action.properties.term``
     - ``searched for``

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
   * - ``parse_timestamp(last_visit_time)``
     - ``timestamp``
   * - ``url``
     - ``url.original``
   * - ``title``
     - ``action.properties.title``
   * - ``host``
     - ``action.properties.host``
   * - ``to_int(visit_count)``
     - ``action.properties.visit_count``
   * - ``description``
     - ``action.properties.description``
   * - ``preview_image_url``
     - ``action.properties.preview_image_url``
   * - ``to_int(id)``
     - ``action.properties.places_id``
   * - ``parse_timestamp(last_visit_date)``
     - ``timestamp``
   * - ``filename``
     - ``file.name``
   * - ``target_path``
     - ``file.path``
   * - ``current_path``
     - ``action.properties.current_path``
   * - ``to_int(total_bytes)``
     - ``file.size``
   * - ``to_int(received_bytes)``
     - ``action.properties.received_bytes``
   * - ``to_bool(opened)``
     - ``action.properties.opened``
   * - ``mime_type``
     - ``file.mime_type``
   * - ``parse_timestamp(start_time)``
     - ``timestamp``
   * - ``parse_timestamp(start_time)``
     - ``event.start``
   * - ``parse_timestamp(end_time)``
     - ``file.mtime``
   * - ``parse_timestamp(end_time)``
     - ``event.end``
   * - ``parse_timestamp(last_access_time)``
     - ``file.accessed``
   * - ``term``
     - ``action.properties.term``
   * - ``normalized_term``
     - ``action.properties.normalized_term``
   * - ``frame_url``
     - ``url.original``
   * - ``top_level_url``
     - ``action.properties.top_level_url``
   * - ``to_int(visit_count)``
     - ``action.properties.visit_count``
   * - ``url``
     - ``url.original``
   * - ``input``
     - ``action.properties.term``
   * - ``to_int(places_id)``
     - ``action.properties.places_id``
   * - ``filename``
     - ``file.name``
   * - ``download_url``
     - ``url.original``
   * - ``to_int(size)``
     - ``file.size``
   * - ``to_bool(deleted)``
     - ``action.properties.deleted``
   * - ``to_bool(canceled)``
     - ``action.properties.canceled``
   * - ``parse_timestamp(endTime)``
     - ``timestamp``
   * - ``parse_timestamp(endTime)``
     - ``event.end``
   * - ``parse_timestamp(endTime)``
     - ``file.mtime``
   * - ``url``
     - ``url.original``
   * - ``to_int(from_visit)``
     - ``action.properties.from_visit``
   * - ``to_int(place_id)``
     - ``action.properties.places_id``
   * - ``visit_type``
     - ``action.properties.visit_type``
   * - ``parse_timestamp(visit_date)``
     - ``timestamp``
   * - ``title``
     - ``action.properties.title``
   * - ``parse_timestamp(dateAdded)``
     - ``timestamp``
   * - ``parse_timestamp(lastModified)``
     - ``action.properties.last_modified``
   * - ``name``
     - ``action.properties.name``
   * - ``value``
     - ``action.properties.value``
   * - ``host``
     - ``action.properties.host``
   * - ``parse_timestamp(expiry)``
     - ``action.properties.expiry``
   * - ``parse_timestamp(lastAccessed)``
     - ``action.properties.last_accessed``
   * - ``parse_timestamp(creationTime)``
     - ``action.properties.creation_time``
   * - ``parse_timestamp(creationTime)``
     - ``timestamp``
   * - ``url``
     - ``url.original``
   * - ``title``
     - ``action.properties.title``
   * - ``host``
     - ``action.properties.host``
   * - ``to_int(visit_count)``
     - ``action.properties.visit_count``
   * - ``to_int(total_view_time_miliseconds)``
     - ``action.properties.total_view_time_ms``
   * - ``to_int(typing_time_miliseconds)``
     - ``action.properties.typing_time_ms``
   * - ``to_int(key_presses)``
     - ``action.properties.key_presses``
   * - ``to_int(scrolling_time_miliseconds)``
     - ``action.properties.scrolling_time_ms``
   * - ``to_int(scrolling_distance_mm)``
     - ``action.properties.scrolling_distance_mm``
