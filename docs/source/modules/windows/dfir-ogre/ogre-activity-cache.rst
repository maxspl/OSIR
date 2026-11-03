ogre-activity-cache
===================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``ogre:windows:activity_cache`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of activity\_cache - using ANSSI DFIR OGRE

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
   * - ``"Windows ActivitiesCache"``
     - ``event.provider``
   * - ``id``
     - ``event.id``
   * - ``to_int(priority)``
     - ``event.severity``
   * - ``parse_timestamp(start_time)``
     - ``event.start``
   * - ``parse_timestamp(start_time)``
     - ``timestamp``
   * - ``parse_timestamp(end_time)``
     - ``event.end``
   * - ``parse_timestamp(last_modified_time)``
     - ``event.created``
   * - ``parse_timestamp(last_modified_time)``
     - ``timestamp``
   * - ``user_home``
     - ``action.properties.user_home``
   * - ``user_group``
     - ``action.properties.user_group``
   * - ``enterprise_id``
     - ``action.properties.enterprise_id``
   * - ``activity_type``
     - ``action.properties.activity_type``
   * - ``activity_status``
     - ``action.properties.activity_status``
   * - ``e_tag``
     - ``action.properties.etag``
   * - ``tag``
     - ``action.properties.tag``
   * - ``match_id``
     - ``action.properties.match_id``
   * - ``group``
     - ``action.properties.group``
   * - ``app_activity_id``
     - ``action.properties.app_activity_id``
   * - ``group_app_activity_id``
     - ``action.properties.group_app_activity_id``
   * - ``is_local_only``
     - ``action.properties.is_local_only``
   * - ``platform_device_id``
     - ``action.properties.platform_device_id``
   * - ``package_id_hash``
     - ``action.properties.package_id_hash``
   * - ``app_id``
     - ``action.properties.app_id``
   * - ``payload``
     - ``action.properties.payload``
   * - ``original_payload``
     - ``action.properties.original_payload``
   * - ``clipboard_payload``
     - ``action.properties.clipboard_payload``
   * - ``start_time``
     - ``action.properties.start_time``
   * - ``end_time``
     - ``action.properties.end_time``
   * - ``last_modified_time``
     - ``action.properties.last_modified_time``
   * - ``last_modified_on_client``
     - ``action.properties.last_modified_on_client``
   * - ``original_last_modified_on_client``
     - ``action.properties.original_last_modified_on_client``
   * - ``expiration_time``
     - ``action.properties.expiration_time``
   * - ``created_in_cloud``
     - ``action.properties.created_in_cloud``
   * - ``custom``
     - 
