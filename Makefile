
# Make file for Ubuntu 22.04

# Makefile

.DEFAULT_GOAL := help

.PHONY: help 

help: ## Show help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n make \033[36m\033[0m\n"} /^[$$()% 0-9a-zA-Z_-]+:.*?##/ { printf " \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

master: ## Start Master Instalation and launch it
	-@cd $(dir $(realpath ./setup/master/master_setup.sh)) && bash master_setup.sh
	@sudo docker exec -it master-master OSIR.py --web

master_offline: ## Start OFFLINE Master Instalation and launch it
	-@cd $(dir $(realpath ./setup/master/master_setup.sh)) && bash master_setup.sh -o
	@sudo docker exec -it master-master OSIR.py --web

agent: ## Start Agent Installation and launch it
	-@cd $(dir $(realpath ./setup/agent/agent_setup.sh)) && bash agent_setup.sh
	@sudo docker exec -it agent-agent OSIR.py --agent

agent_offline: ## Start OFFLINE Agent Installation and launch it
	-@cd $(dir $(realpath ./setup/agent/agent_setup.sh)) && bash agent_setup.sh -o
	@sudo docker exec -it agent-agent OSIR.py --agent

module: ## Start Module Creation
	-@cd $(dir $(realpath ./setup/setup_scripts/create_module.sh)) && bash create_module.sh

uninstall_agent: ## Uninstall agent
	-@cd $(dir $(realpath ./setup/agent/agent_uninstall.sh)) && bash agent_uninstall.sh

uninstall_master: ## Uninstall master
	-@cd $(dir $(realpath ./setup/master/master_uninstall.sh)) && bash master_uninstall.sh

master_full_offline_release: ## Save docker images for offline release of Master
	-@cd $(dir $(realpath ./setup/setup_scripts/parse_docker_compose.sh)) ; \
	COMPOSE_PROFILES="default,master-online,splunk-online,smb-online" \
	IMAGES=$$(./parse_docker_compose.sh master) \
	bash offline_release.sh master

agent_full_offline_release: ## Save agent images for offline release of Agent
	-@cd $(dir $(realpath ./setup/setup_scripts/parse_docker_compose.sh)) ; \
	COMPOSE_PROFILES="default,win" \
	IMAGES=$$(./parse_docker_compose.sh agent) \
	bash offline_release.sh agent
	
agent_dockur_offline_release: ## Save dockur images for offline release of Agent
	-@cd $(dir $(realpath ./setup/setup_scripts/parse_docker_compose.sh)) ; \
	COMPOSE_PROFILES="win" \
	IMAGES=$$(./parse_docker_compose.sh agent) \
	bash offline_release.sh win

master_splunk_offline_release: ## Save docker image for offline release of Splunk
	-@cd $(dir $(realpath ./setup/setup_scripts/parse_docker_compose.sh)) ; \
	COMPOSE_PROFILES="splunk-online" \
	IMAGES=$$(./parse_docker_compose.sh master) \
	bash offline_release.sh splunk

master_load_full_release: ## Load docker images from setup/offline_release/master_containers.tar
	docker load < setup/offline_release/master_containers.tar

master_load_splunk_release: ## Load docker image from setup/offline_release/splunk_containers.tar
	docker load < setup/offline_release/splunk_containers.tar

agent_load_full_release: ## Load docker images from setup/offline_release/agent_containers.tar
	docker load < setup/offline_release/agent_containers.tar

agent_load_dockur_release: ## Load docker images from setup/offline_release/win_containers.tar
	docker load < setup/offline_release/win_containers.tar
