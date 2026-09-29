import sys 
import json 
import base64 
import http.client as http 



class RemotePainter() : 
    def __init__(self, port=60041, host='localhost'): 
        self._host = host 
        self._port = port 
        
        # Json server connection 
        self._PAINTER_ROUTE = '/run.json' 
        self._HEADERS = {'Content-type': 'application/json', 'Accept': 'application/json'} 
 
    # Execute a HTTP POST request to the Substance Painter server and send/receive JSON data 
    def _jsonPostRequest( self, route, body) :
        connection = http.HTTPConnection(self._host, self._port, timeout=3600) 
        connection.request('POST', route, body, self._HEADERS) 
        response = connection.getresponse() 
        
        data = response.read().decode("utf-8")
        connection.close() 
        if 'error' in str(data):
            OutJson = json.loads(data)
            sys.stderr.write("\n")
            sys.stderr.write(OutJson["error"]["description"])
            sys.stderr.flush()

 
    def checkConnection(self): 
        connection = http.HTTPConnection(self._host, self._port) 
        connection.connect() 
 
    # Execute a command 
    def execScript( self, script) :
        Command = base64.b64encode( script.encode('utf-8') )

        Command = '{{"python":"{0}"}}'.format(Command.decode('utf-8'))


        Command = Command.encode( "utf-8" ) 
        
        return self._jsonPostRequest( self._PAINTER_ROUTE, Command)
 

 
class PainterError(Exception): 
    def __init__(self, message): 
        super(PainterError, self).__init__(message) 
    
class ExecuteScriptError(PainterError): 
    def __init__(self, data): 
        super(PainterError, self).__init__('An error occured when executing script: {0}'.format(data))


if __name__ == "__main__":
    Remote = RemotePainter()
    Remote.checkConnection()
    script = ""
    with open(sys.argv[1],'r',encoding="utf-8") as f:
        script = f.read()
    Remote.execScript(script)

