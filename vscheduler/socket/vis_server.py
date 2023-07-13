import socket, threading, subprocess

IP = ""
PORT = 65002
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
hostname = socket.gethostname()
exception = ["root"]

def handle_client(conn, addr):
    print(f"[NEW MGMT CONNECTION TO VIS NODE] {addr}")

    connected = True
    while connected:
        msg = conn.recv(SIZE).decode(FORMAT)

        print("MGMT says:", msg)

        # retrieves number of logged in users
        users_list = []
        users_raw = subprocess.run(['who'], universal_newlines = True, stdout = subprocess.PIPE)
        users_raw_list = users_raw.stdout.splitlines()
        for item in users_raw_list:
            if item.split()[0] not in exception:
                users_list.append(item.split()[0]) 
            else:
                continue
        users_number = len(users_list)
        # count = 0
        # exception = "" #"admin"
        # p = subprocess.run(["users"],text=True,stdout=subprocess.PIPE)
        # for u in p.stdout.split():
        #     if u != exception:
        #         count = count + 1

        # retrieves cpu usage
        p1 = subprocess.Popen(["top", "-n", "1", "-b"], stdout=subprocess.PIPE)
        # p2 = subprocess.run(["awk", "/^%Cpu/{print $2}"], stdin=p1.stdout, capture_output=True, text=True)  # python 3.10
        p2 = subprocess.run(["awk", "/^%Cpu/{print $2}"], stdin=p1.stdout, stdout = subprocess.PIPE)  # python 3.6
        cpu = p2.stdout
        
        msg = str(hostname) + "," + str(cpu) + "," + str(users_number)
        print (f"MSG from VIS SERVER, {msg}")
        conn.send(msg.encode(FORMAT))
        connected = False
    conn.close()

def main():
    print("[STARTING] VIS SERVER STARTING...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] VIS SERVER LISTENING ON {IP}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS TO VIS] {threading.active_count() - 1}")

if __name__ == "__main__":
    main()