win_memory
==========

.. tip:: In Splunk you can find the result of the module after
   ingestion with the following sourcetype:

   * ``windows:live_response:memory:ram:device`` | name_rex: ``r"devices"``
   * ``windows:live_response:memory:ram:drivers`` | name_rex: ``r"drivers"``
   * ``windows:live_response:memory:ram:files`` | name_rex: ``r"files"``
   * ``windows:live_response:memory:ram:findevil`` | name_rex: ``r"findevil"``
   * ``windows:live_response:memory:ram:general`` | name_rex: ``r"general"``
   * ``windows:live_response:memory:ram:handles`` | name_rex: ``r"handles"``
   * ``windows:live_response:memory:ram:modules`` | name_rex: ``r"modules"``
   * ``windows:live_response:memory:ram:net`` | name_rex: ``r"net"``
   * ``windows:live_response:memory:ram:prefetch`` | name_rex: ``r"prefetch"``
   * ``windows:live_response:memory:ram:process`` | name_rex: ``r"process"``
   * ``windows:live_response:memory:ram:registry`` | name_rex: ``r"registry"``
   * ``windows:live_response:memory:ram:services`` | name_rex: ``r"services"``
   * ``windows:live_response:memory:ram:sysinfo`` | name_rex: ``r"sysinfo"``
   * ``windows:live_response:memory:ram:tasks`` | name_rex: ``r"tasks"``
   * ``windows:live_response:memory:ram:threads`` | name_rex: ``r"threads"``
   * ``windows:live_response:memory:ram:timeline`` | name_rex: ``r"timeline.json"``
   * ``windows:live_response:memory:ram:timeline_all`` | name_rex: ``r"timeline_all"``
   * ``windows:live_response:memory:ram:timeline_kernelobject`` | name_rex: ``r"timeline_kernelobject"``
   * ``windows:live_response:memory:ram:timeline_net`` | name_rex: ``r"timeline_net"``
   * ``windows:live_response:memory:ram:timeline_ntfs`` | name_rex: ``r"timeline_ntfs"``
   * ``windows:live_response:memory:ram:timeline_prefetch`` | name_rex: ``r"timeline_prefetch"``
   * ``windows:live_response:memory:ram:timeline_process`` | name_rex: ``r"timeline_process"``
   * ``windows:live_response:memory:ram:timeline_registry`` | name_rex: ``r"timeline_registry"``
   * ``windows:live_response:memory:ram:timeline_task`` | name_rex: ``r"timeline_task"``
   * ``windows:live_response:memory:ram:timeline_thread`` | name_rex: ``r"timeline_thread"``
   * ``windows:live_response:memory:ram:timeline_web`` | name_rex: ``r"timeline_web"``
   * ``windows:live_response:memory:ram:unloaded_modules`` | name_rex: ``r"unloaded_modules"``
   * ``windows:live_response:memory:ram:virtualmachines`` | name_rex: ``r"virtualmachines"``
   * ``windows:live_response:memory:ram:yara`` | name_rex: ``r"yara"``

Description
-----------

Parsing of Windows memory dump.

Timeline
--------

No transform configuration found for this module.

Relationships
-------------

No transform configuration found for this module.

Fields
------

No transform configuration found for this module.
