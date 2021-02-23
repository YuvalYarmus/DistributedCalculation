import sqlite3
from threading import Thread, currentThread, main_thread
import socket
import sys
import select
import concurrent.futures
import time
import datetime
import os

END = "9" * 10
# START = "1" + "0" * 9
START = 3735928559 - 20
OG_HASH = "EC9C0F7EDCC18A98B1F31853B1813301"
ASNWER = 3735928559
run = True

class Server: 

    def __init__(self) -> None:
        self.server = socket.socket()
        self.server.bind(('0.0.0.0', 23))
        self.server.listen(5)
        self.threads = []
        self.conns = []
        self.tups = []
        self.current_number = int(START)
        self.go = True
        self.thread_calc = Thread(target=self.Send_calc, args=())
        self.main()

    def Send_calc(self, conn : socket, cores: str) -> None: 
        try: 
            print("\n\n")
            if self.go: 
                for i in range(int(cores)): 
                    if self.current_number == int(END):
                        print(f"got to the end number end: {END}")
                        for conn2 in self.conns: 
                            conn2.send("/close")
                        self.go = False
                    if self.go: 
                        conn.send(f"/calc:{self.current_number}".encode())
                        print(f"sent for the {i} time: /calc:{self.current_number}")
                        self.current_number += 1
                    time.sleep(1)
                if self.current_number > ASNWER: 
                    global run
                    print(f"Must have been an error - passed the number {ASNWER} in {self.current_number - ASNWER}  --  go is {self.go}")
                    self.go = False
                    if len(self.threads) > 0: 
                        for conn2 in self.conns: 
                            conn2.send("/close".encode())
                    print(f"threads list is: {self.threads}")
                    print(f"global run is {run}")
                    for thread in self.threads:
                        thread.do_run = False
                    self.threads = []
                    self.thread_calc.found = False
                    run = False
                    return None
        except RecursionError as e:
            print("last main block RecursionError: ", e)
        except ConnectionError as e: 
            print(f"had a connection error: {e}")
            self.go = False
            sys.exit()
            
        except: 
            e = sys.exc_info()
            print("exception in main", str(e)) 

    def read_socket(self, conn: socket) -> None: 
        print("started reading")
        t = currentThread()
        if getattr(t, "do_run", True):
            try: 
                data = conn.recv(1024).decode()
                print("data is: ", data)
                if data.startswith("/tasks"):
                    cores = int(data.split(":")[1])
                    print("cores is: ", cores)
                    this_tup = (conn, cores)
                    self.tups.append(this_tup)
                    self.thread_calc = Thread(target=self.Send_calc, args=(conn, cores))
                    self.thread_calc.start()
                    # self.thread_calc.join()
                    t = currentThread()
                    if getattr(t, "do_run", True): 
                        self.read_socket(conn)
                    # for i in range(int(cores)): 
                    #     if self.current_number == int(END):
                    #         print(f"got to the end number end: {END}")
                    #         for conn2 in self.conns: 
                    #             conn2.send("/close")
                    #         self.go = False
                    #     conn.send(f"/calc:{self.current_number}".encode())
                    #     print(f"sent for the {i} time: /calc:{self.current_number}")
                    #     self.current_number += 1
                    #     time.sleep(0.2)
                elif data.startswith("/res"): 
                    num_hash_list = data.split(":")[1].split("-")
                    print(f"num_hash_list is: {num_hash_list}")
                    if num_hash_list[1] == OG_HASH: 
                        print(f"\nfound number: {num_hash_list[0]}\n")
                        for conn2 in self.conns: 
                                conn2.send("/close".encode())
                        for thread in self.threads:
                            thread.do_run = False
                        self.threads = []
                        self.go = False
                        self.thread_calc.found = False
                        # sys.exit(main_thread())
                        global run
                        run = False
                        return None
                        
                    else:   
                        this_conn = None
                        for tup in self.tups: 
                            if tup[0] == conn or tup[0] is conn: 
                                this_conn = tup
                        # print(f"this_conn is: f{this_conn}")
                        self.thread_calc = Thread(target=self.Send_calc, args=(conn, this_conn[1]))
                        self.thread_calc.start()
                        # self.thread_calc.join()
                        t = currentThread()
                        if getattr(t, "do_run", True): 
                            self.read_socket(conn)
                        # for i in range(int(this_conn[1])): 
                        #     if self.current_number == int(END):
                        #         print(f"got to the end number end: {END}")
                        #         for conn2 in self.conns: 
                        #             conn2.send("/close")
                        #         self.go = False
                        #     conn.send(f"/calc:{self.current_number}".encode())
                        #     print(f"sent for the {i} time: /calc:{self.current_number}")
                        #     self.current_number += 1
                        #     time.sleep(0.2)
            except: 
                e = sys.exc_info()
                print(f"\nexception in reading: {str(e)}\n") 
            

    def main(self):
        try:
            global run
            while self.go and run:
                with concurrent.futures.ThreadPoolExecutor(10) as executor:
                    if self.go == False: break
                    if getattr(self.thread_calc, "found", False): break
                    if run == False: break
                    new_socket, address = executor.submit(self.server.accept).result()
                    if new_socket not in self.conns:
                        self.conns.append(new_socket)
                        new_socket.send("Send the number of tasks when you are ready".encode())
                        print("sent to socket")
                        thread = Thread(target=self.read_socket, args=(new_socket, ))
                        print("made thread")
                        self.threads.append(thread)
                        thread.start()
                        print("started thread")
                        if self.go == False: break
                        if getattr(self.thread_calc, "found", False): break
                        if run == False: break

                    for thread in self.threads:
                        thread.do_run = False
                    self.threads = []
                    for conn in self.conns: 
                        print(f"conn is: {conn}")
                        thread = Thread(target=self.read_socket, args=(conn, ))
                        print("sending another conn to read in thread")
                        self.threads.append(thread)
                        thread.start()
                        print("started the thread")
                    print("\ncheck1\n")
                    if self.go == False: break
                    if getattr(self.thread_calc, "found", False): break
                    if run == False: break
        except RecursionError as e:
            print("last main block RecursionError: ", e)
        except ConnectionError as e: 
            print(f"had a connection error: {e}")
            self.main()
        except: 
            e = sys.exc_info()
            print("exception in main", str(e)) 


if __name__ == "__main__": 
    server = Server()
