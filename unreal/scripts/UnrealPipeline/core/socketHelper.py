import threading
import socket
import unreal
import time
from UnrealPipeline.core.Config import globalConfig
import UnrealPipeline.core.UnrealHelper as UH
import json

lock = threading.Lock()


class Shared:
    messageList = []



class ThreadSocket(threading.Thread):
    isrunning = True
    def __init__(self, name):
        super().__init__(name=name)
        self.host = globalConfig.get().connectHost
        self.port = globalConfig.get().connectPort
        self.__isListening = True
    def run(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 绑定地址和端口
        self.socket.bind((self.host, self.port))
        # 开始监听，参数5表示等待连接的最大数量
        self.socket.listen()
        print(f"Server is listening on {self.host}:{self.port}")
        # 无限循环来接受客户端连接
        while self.__isListening:
            try:
                # 接受客户端连接，这个调用会阻塞，直到接收到连接
                conn, addr = self.socket.accept()
            except OSError as e:
                print(f"An error occurred: {e}")
                break
            with conn:
                print(f"Connected by {addr}")
                # 持续接收数据
                while True:
                    try:
                        # 接收数据，1024是接收缓冲区的大小
                        data = conn.recv(1024)
                        if not data:
                            # 没有数据，客户端可能关闭了连接
                            break
                        # 打印接收到的数据
                        print(f"Received: {data.decode()}")

                        with lock:
                            Shared.messageList.append(data.decode())
                        # 可以选择回显数据给客户端
                        conn.sendall(str(len(Shared.messageList)).encode())
                    except Exception as e:
                        # 捕获异常，可能是连接中断
                        print(f"An error occurred: {e}")
                        break
        print("listening stoped")
    def stop(self):
        self.__isListening = False
        self.socket.close()
    @classmethod
    def StartListening(cls):
        thread = ThreadSocket("Sockt")
        thread.start()
        unreal.register_python_shutdown_callback(lambda:thread.stop())


class MessageQueueThread(threading.Thread):
    def __init__(self, name):
        super().__init__(name=name)
        self.__isListening = True
    def run(self) -> None:
        while self.__isListening:
            if Shared.messageList:
                message = None
                # 使用锁来保护共享资源
                with lock:
                    message = Shared.messageList.pop(0)
                if message:
                    unreal.PythonExtensionBPLibrary.launch_script_on_game_thread(message)
            else:
                #防止占用cpu
                time.sleep(1)
    def stop(self):
        self.__isListening = False
    @classmethod
    def StartMessageQueue(cls):
        thread = MessageQueueThread("MessageQueueThread")
        thread.start()
        unreal.register_python_shutdown_callback(lambda:thread.stop())


def CheckMessageQueue(*args):
    if Shared.messageList:
        message = None
        # 使用锁来保护共享资源
        with lock:
            message = Shared.messageList.pop(0)
        if message:
            message = json.loads(message)
            UH.importAssetPipline(message)

def StartSocketServer():
    ThreadSocket.StartListening()
    unreal.register_slate_post_tick_callback(CheckMessageQueue)


def sendStringMyBridge(string:str,address:tuple[str,int]):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(address)
        client_socket.sendall(string.encode())
        client_socket.close()
        return True
    except:
        return False


if __name__ == "__main__":
    import json
    from UnrealPipeline import reloadModule
    reloadModule()
    message = {
        "software":"unreal",
        "command":"print('Hello World')"
    }
    sendStringMyBridge(json.dumps(message),("127.0.0.1",45450))