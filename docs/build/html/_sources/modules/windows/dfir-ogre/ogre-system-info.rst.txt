ogre-system-info
================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:ogre:system_info`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of systeminfo - using ANSSI DFIR OGRE

Timeline
--------

.. _tl-windows-systeminfo-host-state:

.. list-table::
   :header-rows: 1

   * - host.name
     - Relation
     - Message
   * - 
     - ``host-state``
     - ``Host {host.name} runs {os.full} (booted on {timestamp})``

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
   * - ``"windows.systeminfo"``
     - ``event.dataset``
   * - ``"windows"``
     - ``event.module``
   * - ``"state"``
     - ``event.kind``
   * - ``[host]``
     - ``event.category``
   * - ``[info]``
     - ``event.type``
   * - ``"Windows System Information"``
     - ``event.provider``
   * - ``"success"``
     - ``event.outcome``
   * - ``host_name``
     - ``host.name``
   * - ``os_name``
     - ``os.name``
   * - ``os_version``
     - ``os.version``
   * - ``to_string!(.os_name) + " " + to_string!(.os_version)``
     - ``os.full``
   * - ``os_manufacturer``
     - ``labels.os_manufacturer``
   * - ``os_configuration``
     - ``labels.os_configuration``
   * - ``os_build_type``
     - ``labels.os_build_type``
   * - ``registered_owner``
     - ``labels.registered_owner``
   * - ``registered_organization``
     - ``labels.registered_organization``
   * - ``product_id``
     - ``labels.product_id``
   * - ``parse_timestamp(system_boot_time)``
     - ``event.start``
   * - ``parse_timestamp(system_boot_time)``
     - ``timestamp``
   * - ``original_install_date``
     - ``labels.original_install_date``
   * - ``system_manufacturer``
     - ``labels.system_manufacturer``
   * - ``system_model``
     - ``labels.system_model``
   * - ``system_type``
     - ``labels.system_type``
   * - ``processors``
     - ``labels.processors``
   * - ``bios_version``
     - ``labels.bios_version``
   * - ``windows_directory``
     - ``labels.windows_directory``
   * - ``system_directory``
     - ``labels.system_directory``
   * - ``boot_device``
     - ``labels.boot_device``
   * - ``system_locale``
     - ``labels.system_locale``
   * - ``input_locale``
     - ``labels.input_locale``
   * - ``time_zone``
     - ``labels.time_zone``
   * - ``total_physical_memory``
     - ``labels.total_physical_memory``
   * - ``available_physical_memory``
     - ``labels.available_physical_memory``
   * - ``virtual_memory_max_size``
     - ``labels.virtual_memory_max_size``
   * - ``virtual_memory_available``
     - ``labels.virtual_memory_available``
   * - ``virtual_memory_in_use``
     - ``labels.virtual_memory_in_use``
   * - ``page_file_location``
     - ``labels.page_file_location``
   * - ``domain``
     - ``labels.domain``
   * - ``logon_server``
     - ``labels.logon_server``
   * - ``hotfix``
     - ``labels.hotfix``
   * - ``network_cards``
     - ``labels.network_cards``
   * - ``hyper_v_requirements``
     - ``labels.hyper_v_requirements``
   * - ``ogre_md``
     - ``labels.ogre_md``
