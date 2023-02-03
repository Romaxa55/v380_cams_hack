import socket
import struct


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
            while (True):
                # result = (self.s.recvfrom(4096, 0))[0]
                result = b'\xcf39097810.nvdvr.net\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00152.32.227.233\x00\x00\x02\xb6\xfe\x05\x00\x01\x00\x07\x00\x00\x00\x00\x00\x00\x00'
                print(f'Received response from server: {self.byte2str(result)}')  # debugging
                result = self.ParseRelayServer(result)
                print(result)
                break

        except socket.error as e:
            print("socket creation failed with error %s" % (e))

    def ConnenctToRelay(self):
        pass

    def ParseRelayServer(self, data):
        try:
            result = {'id': str(int(data[1:9])),
                      'relay_server': data[33:data.find(b'\x00', 33)].decode('utf-8'),
                      'relay_port': struct.unpack('<H', data[50:52])[0]}
            print(
                f'\u001b[32m[+] Relay found for id {result["id"]} {result["relay_server"]}:{result["relay_port"]}\u001b[37m')
            return result
        except:
            print("Ops")

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
