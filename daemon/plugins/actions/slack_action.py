# Copyright 2023- by Open Kilt LLC. All rights reserved.
# This file is part of the SSHLog Software (SSHLog)
# Licensed under the Redis Source Available License 2.0 (RSALv2)

from plugins.common.plugin import ActionPlugin
import requests
import json
import socket
from comms.event_types import *

class slack_action(ActionPlugin):

    def init_action(self, slack_webhook_url):
        self.slack_webhook_url = slack_webhook_url

        self.logger.info(f"Initialized action {self.name} with slack channel {self.slack_webhook_url}")

    def shutdown_action(self):
        pass

    def _client_ip_str(self, event_data):
        client_port = event_data['tcp_info']['client_port']
        if str(client_port) == '0':
            return f"{event_data['tcp_info']['client_ip']}"
        else:
            return f"{event_data['tcp_info']['client_ip']}:{client_port}"
    def execute(self, event_data):


        message = ''
        session_id = f"{socket.gethostname()}:{event_data['ptm_pid']}"

        if event_data['event_type'] == SSHTRACE_EVENT_NEW_CONNECTION:
            message = f"{event_data['username']} attempted connection to {session_id} from ip {self._client_ip_str(event_data)}"
        elif event_data['event_type'] == SSHTRACE_EVENT_ESTABLISHED_CONNECTION:
            message = f"{event_data['username']} connected to {session_id} from ip {self._client_ip_str(event_data)}"
        elif event_data['event_type'] == SSHTRACE_EVENT_AUTH_FAILED_CONNECTION:
            message = f"{event_data['username']} failed authorization attempt {session_id} from ip {self._client_ip_str(event_data)}"
        elif event_data['event_type'] == SSHTRACE_EVENT_CLOSE_CONNECTION:
            message = f"{event_data['username']} closed connection {session_id} from ip {self._client_ip_str(event_data)}"
        elif event_data['event_type'] == SSHTRACE_EVENT_COMMAND_START:
            message = f"{event_data['username']} executed command {event_data['filename']} on {session_id}\n{event_data['args']}"
        elif event_data['event_type'] == SSHTRACE_EVENT_COMMAND_END:
            message = f"{event_data['username']} finished executing command {event_data['filename']} on {session_id}\n{event_data['args']}"
        elif event_data['event_type'] == SSHTRACE_EVENT_FILE_UPLOAD:
            message = f"{event_data['username']} uploaded file {event_data['target_path']} on {session_id}"
        elif event_data['event_type'] == SSHTRACE_EVENT_TERMINAL_UPDATE:
            self.logger.warning("Terminal update events probably should not be sent to slack.  Assuming misconfigurationand skipping")
            return

        self.logger.info(f"{self.name} Slack action triggered on {event_data['event_type']} sending slack message")
        content = {
            'text': message
        }

        response = requests.post(self.slack_webhook_url,
                                 data=json.dumps(content),
                                 headers={'Content-Type': 'application/json'})

        self.logger.debug(f"Slack webhook response: {response.status_code} - {response.content}")

