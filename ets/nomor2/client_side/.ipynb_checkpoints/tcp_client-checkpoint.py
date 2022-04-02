import sys
import socket
import json
import logging
import xmltodict
import ssl
import os

# tambahan
import concurrent.futures
import threading
import random
import datetime

server_address = ('172.16.16.101', 12000)
# ip port nya harus diganti ip mesin yg jd server

def make_socket(destination_address='localhost',port=12000):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        return sock
    except Exception as ee:
        logging.warning(f"error {str(ee)}")

def make_secure_socket(destination_address='localhost',port=10000):
    try:
        #get it from https://curl.se/docs/caextract.html

        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.verify_mode=ssl.CERT_OPTIONAL
        context.load_verify_locations(os.getcwd() + '/domain.crt')

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        secure_socket = context.wrap_socket(sock,server_hostname=destination_address)
        logging.warning(secure_socket.getpeercert())
        return secure_socket
    except Exception as ee:
        logging.warning(f"error {str(ee)}")



def send_command(command_str,is_secure=False):
    alamat_server = server_address[0]
    port_server = server_address[1]
#    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# gunakan fungsi diatas
    if is_secure == True:
        sock = make_secure_socket(alamat_server,port_server)
    else:
        sock = make_socket(alamat_server,port_server)

    logging.warning(f"connecting to {server_address}")
    try:
        logging.warning(f"sending message ")
        sock.sendall(command_str.encode())
        # Look for the response, waiting until socket is done (no more data)
        data_received="" #empty string
        while True:
            #socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
            data = sock.recv(16)
            if data:
                #data is not empty, concat with previous content
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                # no more data, stop the process by break
                break
        # at this point, data_received (string) will contain all data coming from the socket
        # to be able to use the data_received as a dict, need to load it using json.loads()
        hasil = json.loads(data_received)
        logging.warning("data received from server:")
        return hasil
    except:
        logging.warning("error during data receiving")
        return False



def getdatapemain(nomor=0,is_secure=False):
    cmd=f"getdatapemain {nomor}\r\n\r\n"
    hasil = send_command(cmd,is_secure=is_secure)
    return hasil

def kirim_request(nomor=0,is_secure=False):
    time_start = datetime.datetime.now()
    h = getdatapemain(nomor,is_secure)
    if (h):
        print(h['nama'],h['nomor'])
        return datetime.datetime.now() - time_start
    else:
        print("kegagalan pada data transfer")
        return None

if __name__=='__main__':
    
    # atur thread dan request
    n_thread_list = [1, 5, 10, 20]
    jumlah_request = 500
    result_str = list()
    
    for jumlah_thread in n_thread_list:
        nomorDataList = list()
        for i in range(jumlah_request):
            num = random.randint(1,4)
            nomorDataList.append(num)

        with concurrent.futures.ThreadPoolExecutor(max_workers=jumlah_thread) as executor:
            hasil_waktu = list(executor.map(lambda nomor: kirim_request(nomor, False), nomorDataList))

        jumlah_response = len(hasil_waktu) - hasil_waktu.count(None)
        total_latency = sum(list(filter(None, hasil_waktu)), datetime.timedelta(0,0))
        latency = sum(list(filter(None, hasil_waktu)), datetime.timedelta(0,0)) / jumlah_request
        result_str.append(f"# n-thread: {jumlah_thread}, n-request: {jumlah_request}, n-response: {jumlah_response} --avg-latency: {latency}")
    
    for _ in n_thread_list:
        print(result_str.pop(0))
