from uGlobalConfig import globalConfig


class Log():
    _instance = None
    def __init__(self) -> None:
        pass
    def __del__(self) -> None:
        pass
    def __initLog(self) ->None:
        
        
        pass
    @classmethod
    def get(cls):
        if cls._instance == None:
            cls._instance = Log()
        return cls._instance
    
if __name__ == "__main__":
    pass