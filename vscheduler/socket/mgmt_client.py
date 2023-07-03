import socket, time

def client_program():
    hosts = ["192.168.2.66", "192.168.2.144"]
    port = 65002
    all_data = {}

    for host in hosts:
        client_socket = socket.socket()  # instantiate
        try:
            client_socket.connect((host, port))  # connect to the server
        except socket.error as e:
            print (f"Caught exception socket.error: {e}")
            continue

        message = "Requesting data from " + str(host)

        while True:
            client_socket.send(message.encode())  # send message
            data = client_socket.recv(1024).decode()  # receive response

            print (f"Received from {host}: {data}")  # show in terminal
            all_data[host] = data.split(",")
            if data:
                break
        
        client_socket.close()  # close the connection
        time.sleep(0.1)

    return all_data

# if __name__ == '__main__':
#     client_program()