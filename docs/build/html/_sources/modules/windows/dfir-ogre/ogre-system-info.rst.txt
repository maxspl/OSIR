ogre-system-info
================

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``ogre:windows:system_info`` | name_rex: ``r"\.jsonl$"``

Description
-----------

Parsing of systeminfo - using ANSSI DFIR OGRE

Timeline
--------

.. _tl-windows-dfir-ogre-systeminfo-host-state:

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
   * - ``"Windows System Information"``
     - ``event.provider``
   * - ``host_name``
     - ``host.name``
   * - ``os_name``
     - ``os.name``
   * - ``os_version``
     - ``os.version``
   * - ``to_string!(.os_name) + " " + to_string!(.os_version)``
     - ``os.full``
   * - ``os_manufacturer``
     - ``action.properties.os_manufacturer``
   * - ``os_configuration``
     - ``action.properties.os_configuration``
   * - ``os_build_type``
     - ``action.properties.os_build_type``
   * - ``registered_owner``
     - ``action.properties.registered_owner``
   * - ``registered_organization``
     - ``action.properties.registered_organization``
   * - ``product_id``
     - ``action.properties.product_id``
   * - ``parse_timestamp(system_boot_time)``
     - ``event.start``
   * - ``parse_timestamp(system_boot_time)``
     - ``timestamp``
   * - ``original_install_date``
     - ``action.properties.original_install_date``
   * - ``system_manufacturer``
     - ``action.properties.system_manufacturer``
   * - ``system_model``
     - ``action.properties.system_model``
   * - ``system_type``
     - ``action.properties.system_type``
   * - ``processors``
     - ``action.properties.processors``
   * - ``bios_version``
     - ``action.properties.bios_version``
   * - ``windows_directory``
     - ``action.properties.windows_directory``
   * - ``system_directory``
     - ``action.properties.system_directory``
   * - ``boot_device``
     - ``action.properties.boot_device``
   * - ``system_locale``
     - ``action.properties.system_locale``
   * - ``input_locale``
     - ``action.properties.input_locale``
   * - ``time_zone``
     - ``action.properties.time_zone``
   * - ``total_physical_memory``
     - ``action.properties.total_physical_memory``
   * - ``available_physical_memory``
     - ``action.properties.available_physical_memory``
   * - ``virtual_memory_max_size``
     - ``action.properties.virtual_memory_max_size``
   * - ``virtual_memory_available``
     - ``action.properties.virtual_memory_available``
   * - ``virtual_memory_in_use``
     - ``action.properties.virtual_memory_in_use``
   * - ``page_file_location``
     - ``action.properties.page_file_location``
   * - ``domain``
     - ``action.properties.domain``
   * - ``logon_server``
     - ``action.properties.logon_server``
   * - ``hotfix``
     - ``action.properties.hotfix``
   * - ``network_cards``
     - ``action.properties.network_cards``
   * - ``hyper_v_requirements``
     - ``action.properties.hyper_v_requirements``
