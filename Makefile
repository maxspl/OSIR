
# Make file for Ubuntu 22.04

# Makefile

.DEFAULT_GOAL := help

.PHONY: help 

help: ## Show help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n make \033[36m\033[0m\n"} /^[$$()% 0-9a-zA-Z_-]+:.*?##/ { printf " \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

master: ## Start Master Instalation and launch it
	-@cd $(dir $(realpath ./setup/master/master_setup.sh)) && bash master_setup.sh
	@sudo docker exec -it master-master OSIR.py --web

agent: ## Start Agent Installation and launch it
	-@cd $(dir $(realpath ./setup/agent/agent_setup.sh)) && bash agent_setup.sh
	@sudo docker exec -it agent-agent OSIR.py --agent

module: ## Start Module Creation
	-@cd $(dir $(realpath ./setup/setup_scripts/create_module.sh)) && bash create_module.sh

uninstall_agent: ## Uninstall agent
	-@cd $(dir $(realpath ./setup/agent/agent_uninstall.sh)) && bash agent_uninstall.sh

uninstall_master: ## Uninstall master
	-@cd $(dir $(realpath ./setup/master/master_uninstall.sh)) && bash master_uninstall.sh

