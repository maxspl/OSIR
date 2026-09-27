Components & Terminology
------------------------

- **Master**: Monitors a directory (called "case") containing files to be processed and creates processing tasks for the agents.
- **Agent**: Processes tasks issued by the master and interacts with other components like the Windows machine or Splunk depending on the tasks.
- **Splunk (Optional)**: Can be deployed locally on the same host as the master or remotely.
- **Windows Box (Optional)**: Can be deployed locally on the same host as the master or remotely. Two ways of deploying automatically a Windows VM are currently supported: using vbox and Vagrant or using Dockur (Windows in Docker). If running OSIR agent on a Windows host, there is no need to deploy a Windows VM, the host itself is used.
- **Processing job**: Action of processing a case containing files to process. Handled by master.
- **Processing tasks**: Processing action decribed by a module configuration file, taking in input a directory or file and applying. Handled by agents.

