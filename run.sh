#!/usr/bin/bash

mqtt_topic="$(bashio::config 'mqtt_topic')"

bashio::log.info "Starting InverterData.py"

watch -n 300 'python3 ./InverterData.py'

bashio::log.info "Script terminated"
