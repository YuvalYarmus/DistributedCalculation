import sys
import multiprocessing
import time
import msvcrt
import os
import concurrent.futures
import socket
import hashlib
from threading import Thread, current_thread


class My_Client: 

    def __init__(self): 
        self.server_address = ('127.0.0.1', 23)
        self.current_socket = socket.socket()
        self.current_socket.connect(self.server_address)
        self.current_socket.settimeout(2)
        print("client connected")
        thread = Thread(target=self.read, args=())
        thread.start()
        self.thread2 = Thread(target=self.Send_calc, args=())
    
    def Send_calc(self, num: str): 
        hash_num = self.hash_string_number(num)
        print(f"in Send_Calc /res:{num}-{hash_num}\n")
        self.current_socket.send(f"/res:{num}-{hash_num}".encode())

    def hash_string_number(self, num: str): 
        print(f"in turn to hash string, num is: {num}\n")
        return hashlib.md5( f'{num}'.encode() ).hexdigest().upper()

    def read(self):
        print("in read")
        try: 
            data = self.current_socket.recv(64).decode()
            print(f"data is: {data}\n")
            if data.startswith("/calc"): 
                num = data.split(":")[1]
                self.thread2 = Thread(target=self.Send_calc, args=(num,))
                self.thread2.start()
                self.read()
            elif data == "Send the number of tasks when you are ready": 
                print("sending cores")
                self.thread2 = Thread(target=self.Send, args=(f"/tasks:{multiprocessing.cpu_count()}",))
                self.thread2.start()
                self.read()
            elif data.startswith("/close"):
                self.close
            else: self.read()
        except RecursionError as e:
            print(f"\nlast main block RecursionError: {str(e)}\n")
            self.read()
        except TimeoutError as e: 
            print(f"\nlast main block RecursionError: {str(e)}\n")
            self.read()
        except socket.timeout as e: 
            print(f"\nlast main block RecursionError: {str(e)}\n")
            self.read()
        except: 
            e = sys.exc_info()
            print(f"exception in reading: {str(e)}") 

    def Send(self, param : str): 
        self.current_socket.send(str(param).encode()) 
    
    def close(self):
        self.current_socket.close()
    

if __name__ == "__main__": 
    client = My_Client()