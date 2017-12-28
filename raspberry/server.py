import socket


class Server:

    def __init__(self, host=socket.gethostname(), port=1234) -> None:
        super().__init__()
        self.ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.HostName = host
        self.Port = port
        self.ServerSocket.bind((host, port))

    def receive(self):
        data, addr = self.ServerSocket.recvfrom(1024)
        return data, addr

    def close(self):
        self.ServerSocket.close()


if __name__ == '__main__':
    server = Server()
    print('Server is online \nHost Name : {}:{}'.format(server.HostName, server.Port))
    while True:
        (message, address) = server.receive()
        print(repr(address) + ": " + message)
        if message == 'q':
            server.close()
            break
