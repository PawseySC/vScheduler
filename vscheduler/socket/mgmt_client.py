# socket client sitting in management instance in charge of gathering nodes usage statisctics for load balance
import socket, time
from vscheduler.log.log import Capture_log
from vscheduler.general.initiate import PrintCondition as MyPrintCondition
from vscheduler.general.alert import mailFunction

port = 65002

socket_records = Capture_log("socket", __file__)
logger_win = socket_records.log_agent("windows")
logger_unix = socket_records.log_agent("linux")


def client_statistics(domains, os):
    print (f"domains: {domains}") if MyPrintCondition.fprint else 0
    logger_win.info (f"domains: {domains}") if os == "windows" else logger_unix.info (f"domains: {domains}")
    hosts =[]

    # fetch domain IPs
    for domain in domains:
        # addr = socket.getaddrinfo (domain, 0,0,0,0)
        # for result in addr:
        #     hosts.append(result[-1][0])
        #     hosts = list(set(hosts))
        hosts = list({addr[-1][0] for addr in socket.getaddrinfo (domain, 0, 0, 0, 0)})
    print (f"hosts IPs: {hosts}") if MyPrintCondition.fprint else 0
    logger_win.info (f"hosts IPs: {hosts}") if os == "windows" else logger_unix.info (f"hosts IPs: {hosts}")

    all_data = {}
    for host in hosts:
        client_socket = socket.socket()                 # instantiate
        try:
            client_socket.connect((host, port))         # connect to the server
        except socket.error as e:
            print (f"Caught exception socket.error: {e} {host} {port}") if MyPrintCondition.fprint else 0
            logger_win.critical (f"Caught exception socket.error: {e} {host} {port}") if os == "windows" else logger_unix.critical (f"Caught exception socket.error: {e} {host} {port}")
            mailFunction("socket error","error connecting vis node socket server\n" + e + " " + host + " " + port, "", "")
            continue

        message = "Requesting data from " + str(host)
        print (message) if MyPrintCondition.fprint else 0
        logger_win.info (message) if os == "windows" else logger_unix.info (message)

        while True:
            client_socket.send(message.encode())        # send message
            data = client_socket.recv(1024).decode()    # receive response

            print (f"Received from {host}: {data}") if MyPrintCondition.fprint else 0
            logger_win.info (f"Received from {host}: {data}") if os == "windows" else logger_unix.info (f"Received from {host}: {data}")
            all_data[host] = data.split(",")
            time.sleep(0.1)
            if data:
                break
        
        client_socket.close()  # close the connection
        
    return all_data

# if __name__ == '__main__':
#     client_program()