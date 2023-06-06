import socket
import threading
import subprocess

# IP = socket.gethostbyname(socket.gethostname())
IP = ""
PORT = 54321
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECT"

def handle_client(conn, addr):
    print(f"[NEW CONNECTION TO COMP] {addr} connected from MGMT client.")

    connected = True
    while connected:
        msg = conn.recv(SIZE).decode(FORMAT)

        # print("splited:", msg.split("-"))
        print("mgmt client sent:", msg)
        # node = msg.split("-")[0]
        # user = msg.split("-")[1]
        # print (msg.split("-")[0])
        # print (msg.split("-")[1])
        p1 = subprocess.Popen(["top", "-n", "1", "-b"], stdout=subprocess.PIPE)
        p2 = subprocess.run(["awk", "/^%Cpu/{print $2}"], stdin=p1.stdout, capture_output=True, text=True)
        print ("p2:", p2.stdout)
        print(f"[{addr}] {msg}")

        count = 0
        exception = "" #"admin"
        p = subprocess.run(["users"],text=True,stdout=subprocess.PIPE)
        # p.stdout
        for u in p.stdout.split():
            if u != exception:
                count = count + 1
        #len(p.stdout.split())


        msg = f"Msg received from mgmt: {msg}, sent back cpu and users from COMP: {p2.stdout}, {count}"
        # msg = wikipedia.summary(msg, sentences=1)
        conn.send(msg.encode(FORMAT))
        connected = False
    conn.close()

def main():
    print("[STARTING] COMP Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] COMP Server is listening on {IP}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS TO COMP] {threading.active_count() - 1}")

if __name__ == "__main__":
    main()