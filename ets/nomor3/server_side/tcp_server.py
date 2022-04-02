import sys
import socket
import logging
import json
import os
import ssl
import threading

alldata = dict()
alldata['1']=dict(nomor=1, nama="dean henderson", posisi="kiper")
alldata['2']=dict(nomor=2, nama="luke shaw", posisi="bek kiri")
alldata['3']=dict(nomor=3, nama="aaron wan-bissaka", posisi="bek kanan")
alldata['4']=dict(nomor=4, nama="victor lindelof", posisi="bek tengah kanan")

def proses_request(request_string):
    #format request
    # NAMACOMMAND spasi PARAMETER
    cstring = request_string.split(" ")
    hasil = None
    try:
        command = cstring[0].strip()
        if (command == 'getdatapemain'):
            # getdata spasi parameter1
            # parameter1 harus berupa nomor pemain
            nomorpemain = cstring[1].strip()
            logging.warning("Request: getdatapemain {}".format(nomorpemain))
            try:
                hasil = alldata[nomorpemain]
            except:
                hasil = None
        elif (command == 'versi'):
            hasil = versi()
    except:
        hasil = None
    return hasil

def accept_connection(koneksi, client_address, is_secure, socket_context):
    try:
        if is_secure == True:
            connection = socket_context.wrap_socket(koneksi, server_side=True)
        else:
            connection = koneksi

        selesai=False
        data_received="" #string
        while True:
            data = connection.recv(32)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    selesai=True

                if (selesai==True):
                    hasil = proses_request(data_received)
                    logging.warning(f"Sending response: {hasil}")

                    #hasil bisa berupa tipe dictionary
                    #harus diserialisasi dulu sebelum dikirim via network
                    # Send data
                    # some data structure may have complex structure
                    # how to send such data structure through the network ?
                    # use serialization
                    #  example : json, xml

                    # complex structure, nested dict
                    # all data that will be sent through network has to be encoded into bytes type"
                    # in this case, the message (type: string) will be encoded to bytes by calling encode

                    hasil = serialisasi(hasil)
                    hasil += "\r\n\r\n"
                    connection.sendall(hasil.encode())
                    selesai = False
                    data_received = ""  # string
                    break

            else:
                logging.warning(f"no more data from {client_address}")
                break
        # Clean up the connection
    except ssl.SSLError as error_ssl:
        logging.warning(f"SSL error: {str(error_ssl)}")


def serialisasi(a):
    #print(a)
    #serialized = str(dicttoxml.dicttoxml(a))
    serialized =  json.dumps(a)
    return serialized

def run_server(server_address,is_secure=False):
    # ------------------------------ SECURE SOCKET INITIALIZATION ----
    socket_context = None
    if is_secure == True:
        print(os.getcwd())
        cert_location = os.getcwd() + '/certs/'
        socket_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        socket_context.load_cert_chain(
            certfile=cert_location + 'domain.crt',
            keyfile=cert_location + 'domain.key'
        )
    # ---------------------------------

    #--- INISIALISATION ---
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind the socket to the port
    if is_secure:
        logging.warning(f"starting up secure server on {server_address}")
    else:
        logging.warning(f"starting up on {server_address}")
    sock.bind(server_address)
    # Listen for incoming connections
    sock.listen(1000)


    while True:
        # Wait for a connection
        koneksi, client_address = sock.accept()
        print("")
        logging.warning(f"Incoming connection from {client_address}")
        conn_thread = threading.Thread(target=accept_connection, args=(koneksi,client_address, is_secure, socket_context))
        conn_thread.start()

if __name__=='__main__':
    try:
        run_server(('0.0.0.0', 12000),is_secure=True)
    except KeyboardInterrupt:
        logging.warning("Control-C: Program berhenti")
        exit(0)
    finally:
        logging.warning("selesai")