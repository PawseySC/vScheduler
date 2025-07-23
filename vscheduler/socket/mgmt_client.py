# socket client sitting in management instance in charge of gathering nodes usage statisctics for load balance
import socket, time
from tabulate import tabulate
from vscheduler.general.initiate import PrintCondition
from vscheduler.lib.verbose import verbose
from vscheduler.general.alert import mailFunction
from vscheduler.log.log import CaptureLog

port = 65002
socket_records = CaptureLog("client", __file__)
logger = socket_records.log_agent("socket")

def client_statistics(domains, os):
    """
    collects clients resource statisctcal data for load balance
    by connecting to sockt server running on each client and receiving
    the nodes usage data.
    To do this received domains need to be converted to IP for socket communication.
    """
    print (f"domains: {domains}") if verbose.mode else 0 # if PrintCondition.fprint else 0
    logger.info (f"domains: {domains}")
    ips =[]
            
    # fetch domain ips
    for domain in domains:
        ips = list({addr[-1][0] for addr in socket.getaddrinfo (domain, 0, 0, 0, 0)})
        # addr = socket.getaddrinfo (domain, 0,0,0,0)
        # for result in addr:
        #     ips.append(result[-1][0])
        #     ips = list(set(ips))
    print (f"ips: {ips}") if verbose.mode else 0 # if PrintCondition.fprint else 0
    logger.info (f"\nips:\n{ips}")
    
    nodes_data = {}
    for ip in ips:
        client_socket = socket.socket()                 # instantiate
        try:
            client_socket.connect((ip, port))         # connect to the server
        except socket.error as e:
            print (f"Caught exception socket error from {ip}:{port}\n{e}") if verbose.mode else 0 # if PrintCondition.fprint else 0
            logger.critical (f"Caught exception socket error from {ip}:{port}\n{e}")
            mailFunction("socket error", f"error connecting vis node socket server on {ip}:{port}\n{e}", "", "")
            continue

        message = "Connected.. Requesting data from " + str(ip)
        print (message) if verbose.mode else 0 # if PrintCondition.fprint else 0
        logger.info (message)

        while True:
            client_socket.send(message.encode())        # send message
            data = client_socket.recv(1024).decode()    # receive response

            print (f"Received from {ip}: {data}") if verbose.mode else 0 # if PrintCondition.fprint else 0
            logger.info (f"Received from {ip}: {data}")
            nodes_data[ip] = data.split(",")
            time.sleep(0.1)
            if data:
                break
        
        client_socket.close()  # close the connection
    
    # combine three flat lists into a 2D array showing collected resource statistics in a consolidated format
    print (f"\n{tabulate({list(zip(domains, ips, nodes_data))}, headers=['domain', 'ip', 'data'])}") if verbose.mode else 0 # if PrintCondition.fprint else 0
    logger.info (f"\n{tabulate({list(zip(domains, ips, nodes_data))}, headers=['domain', 'ip', 'data'])}")
        
    return nodes_data