import socket


class Server:

    def __init__(self, host=socket.gethostname(), port=1234) -> None:
        super().__init__()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host_name = host
        self.port = port
        self.server_socket.bind((host, port))

    def receive(self):
        data, addr = self.server_socket.recvfrom(1024)
        return data, addr

    def close(self):
        self.server_socket.close()


if __name__ == '__main__':
    server = Server()
    print('Server is online \nHost Name : {}:{}'.format(server.host_name, server.port))
    while True:
        (message, address) = server.receive()
        print(repr(address) + ": " + message)
        if message == 'q':
            server.close()
            break
