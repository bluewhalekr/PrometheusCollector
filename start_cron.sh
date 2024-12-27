#!/usr/bin/bash
PYTHONPATH=/opt/collector:/opt/collector/venv/lib/python3.12/site-packages SLACK_API_TOKEN="###SLACK_API_TOKEN###" /opt/collector/venv/bin/python collector_cron.py -d 1