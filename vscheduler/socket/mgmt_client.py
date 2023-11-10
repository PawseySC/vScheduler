import socket, time
from vscheduler.log.log import Capture_log
from vscheduler.lib.config import Credentials as MyCredentials
from vscheduler.general.alert import mailFunction

def client_program(domains):
    # hosts = ["192.168.2.66", "192.168.2.144"]
    print ("host", domains)
    hosts =[]

    for domain in domains:
        # addr = socket.getaddrinfo (domain, 0,0,0,0)
        # for result in addr:
        #     hosts.append(result[-1][0])
        #     hosts = list(set(hosts))
        hosts = list({addr[-1][0] for addr in socket.getaddrinfo (domain, 0, 0, 0, 0)})

    port = 65002
    all_data = {}

    socket_records = Capture_log("socket", __file__)
    logger = socket_records.log_agent()

    for host in hosts:
        client_socket = socket.socket()                 # instantiate
        try:
            client_socket.connect((host, port))         # connect to the server
        except socket.error as e:
            logger.critical (f"Caught exception socket.error: {e} {host} {port}")
            mailFunction("socket error","error connecting vis node socket server\n" + e + " " + host + " " + port, "", "")
            continue

        message = "Requesting data from " + str(host)

        while True:
            client_socket.send(message.encode())        # send message
            data = client_socket.recv(1024).decode()    # receive response

            logger.info (f"Received from {host}: {data}")
            all_data[host] = data.split(",")
            time.sleep(0.1)
            if data:
                break
        
        client_socket.close()  # close the connection
        

    return all_data

# if __name__ == '__main__':
#     client_program()