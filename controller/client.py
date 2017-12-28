import socket


class Client:

    def __init__(self, host, port=1234) -> None:
        super().__init__()
        self.host_name = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, message):
        self.client_socket.sendto(message.encode(), (self.host_name, self.port))


# TEST CLIENT
if __name__ == '__main__':
    client = Client(host='DESKTOP-SODT3MG', port=1234)
    client.send('hello friend1')
    client.send('hello friend2')
    client.send('hello friend3')
    client.send('hello friend4')
    client.send('q')
