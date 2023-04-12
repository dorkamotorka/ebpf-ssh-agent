# Copyright 2023- by Open Kilt LLC. All rights reserved.
# This file is part of the SSHLog Software (SSHLog)
# Licensed under the Redis Source Available License 2.0 (RSALv2)

from plugins.common.plugin import ActionPlugin
import subprocess

class run_command_action(ActionPlugin):

    def init_action(self, command, args=[], timeout=None):
        self.command = command
        self.timeout = timeout
        self.args = args
        self.logger.info(f"Initialized action {self.name} with command {command}")

    def shutdown_action(self):
        pass

    def execute(self, event_data):
        args_list = [self.command]
        for arg in self.args:
            # Swap out any {{value}} items in the arguments list
            args_list.append(self._insert_event_data(event_data, arg))

        self.logger.info(f"{self.name} Command action triggered on {event_data['event_type']} executing {args_list}")
        exit_code = subprocess.call(args_list, timeout=self.timeout)

        if exit_code != 0:
            self.logger.info(f"Command {args_list} returned failure exit code {exit_code}")