from matchbot.gameservermanager import GameServerManager
from os import getenv

gsm = GameServerManager(server_token=getenv("SERVER_TOKEN"),
                        server_ip=getenv("SERVER_IP"),
                        server_port_min=getenv("SERVER_PORT_MIN"),
                        server_port_max=getenv("SERVER_PORT_MAX"))

print("Hello from manager")