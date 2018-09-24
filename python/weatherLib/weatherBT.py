import bluetooth as bt
import time as tm
import threading

from weatherLib.weatherUtil import WLogger,openFile
from weatherLib.weatherQueue import WeatherQueue

class ConnError(Exception):
    """
    Error de connexió a Bt
    """
    pass

class WeatherBT(object):
    _logger = WLogger()

    
    def __init__(self,addr,serv):
        """
        Setup the bluetooth connection object
        Parameters:
            - address: BT address of the device, in hex form (XX:XX:XX:XX:XX:XX)
            - service: UUID of the RFCOMM service in the device
        """
        WeatherBT._logger.logMessage(level="DEBUG",message="Service: {0:s}, address:{1:s}".format(serv,addr))
        srvlist = bt.find_service(uuid = serv, address = addr)
        if len(srvlist) == 0:
            msg = "BT service not available."
            WeatherBT._logger.logMessage(level="WARNING", message=msg)
            raise ConnError
        else:
            srv = srvlist[0]
            port = srv["port"]
            name = srv["name"]
            host = srv["host"]
            sock=bt.BluetoothSocket(bt.RFCOMM)
            sock.connect((host,port))
            self.theSocket = sock
            self.theName = name
        

    def getLine(self):
        """ 
        Read a line from a socket connection.
        It reads characters from a socket until it gets a CR+LF combination. The
        CR+LF is *not* returned as part of the read line. 
        If a line does not include the LF (the terminator is just a CR, it's
        discarded.
        Returns:
        Received string        
        """
        line = ""
        onLoop = True                             # End of loop switch
        while onLoop:
            byte = self.theSocket.recv(1)                 # Get byte from socket
            if byte == b'\r':                     # Carriage return?
                byte = self.theSocket.recv(1)             # Consume LF
                if byte != b'\n':                 # IF not LF, big trouble: discard line
                    line = ""
                else:
                    onLoop = False                # End of loop, line ready
            else:
                try:
                    line = line + byte.decode()   # Add character to current working line
                except UnicodeDecodeError as e:
                    msg = "Error decoding received byte: {0:s}".format(repr(e))
                    WeatherBT._logger.logMessage(level="WARNING",message=msg)
        return line                              # The line is complete
            
    def send(self, line):
        """
        Send a string to the underlying BT socket
        Parameters:
            - line: string to send
        """
        self.theSocket.send(line)
        
        
    def waitAnswer(self, answer,retries=5):
        """
        Wait for a specific answer, discarding all the read lines until that
        answer is read or the number of retries is exhausted.
        Parameters:
            - answer: text (6 characters) to expect
            - retries: Number of lines to read until leaving
        Returns:
            Boolean (true = anwer found, false = retries exhausted)
        """
        answ = ""
        remain = retries
        while answ != answer[0:6] and remain > 0:
            line = self.getLine()
            self._logger.logMessage(level="INFO",message=line)
            answ = line[0:6]
            remain -= 1
        return answ == answer[0:6]
    
    def close(self):
        self.theSocket.close()
        self.theName = None

class WeatherBTThread(threading.Thread):
    """
    This class implements a thread to read the data coming from the Bluetooth 
    device.
    """
    _logger = WLogger() 

    def __init__(self,address, service, queue, event, directory):
        super(WeatherBTThread, self).__init__()

        self.name = 'WeatherBTThread'

        self.theDirectory = directory
        self.theEvent = event
        self.theAddress = address
        self.theService = service
        self.theQueue = queue
        self._stopSwitch = False
        
        
    def stop(self):
        self._stopSwitch = True

    def connect_wait(self,times=10):
        """
        Connect (create) a BT object, with timed retries
        Parameters:
            - address: BT address of the device, in hex form (XX:XX:XX:XX:XX:XX)
            - service: UUID of the RFCOMM service in the device
        Returns:
            The created object
        """            
        numTries = 0
        delay = 5
        while numTries < times and not self._stopSwitch:
            try:
                theBT = WeatherBT(addr=self.theAddress, serv=self.theService)
                WeatherBT._logger.logMessage(level="INFO",message="Connected to weather service at {0:s} : {1:s}"  \
                           .format(theBT.theName,self.theAddress))
                return theBT
            except:
                self._logger.logMessage(level="WARNING",
                                       message="BT Connection atempt {0} failed".format(numTries+1))
                tm.sleep(delay)
                numTries += 1
        return None

    def run(self):
        self._logger.logMessage("Starting thread {0}.".format(self.getName()), level="INFO")

        gizmo = None
        gizmo = self.connect_wait()
        if gizmo == None and not self._stopSwitch:
            raise ConnError
            
            
        f  = openFile(self.theDirectory)

        self._logger.logMessage(message="Start weather processing.", level="INFO")    
        while not self._stopSwitch:
            try:
                line = gizmo.getLine()
                cmd = line[0:5]
                if cmd == "DATA ":              # It is a data line so...
                    f.write(line+'\n')          # ... write it!
                    f.flush()                   # Don't wait, write now!
                    self.theQueue.pushLine(line)
                    self.theEvent.set()         # Send event: data received
                elif cmd == "DEBUG":
                    self._logger.logMessage(level="DEBUG", message=line)            
                elif cmd == "INFO:":
                    self._logger.logMessage(level="INFO", message=line)
                elif cmd == "ERROR":
                    self._logger.logMessage(level="WARNING", message="Error in firmware/hardware: {0:s}".format(line))      
                elif cmd == "HARDW":
                    self._logger.logMessage(level="CRITICAL",message=line)
                elif cmd == "BEGIN":
                    now = tm.gmtime()   # So send current time to set RTC...
                    timcmd = "TIME " + tm.strftime("%Y%m%d%H%M%S",now) + "\r"
                    self._logger.logMessage(level="INFO", 
                                            message="Setting time, command: {0:s}".format(timcmd))
                    gizmo.send(timcmd)
                    gizmo.waitAnswer("OK-000")
                else:
                    self._logger.logMessage(level="WARNING",message="Non-processable line: {0:s}".format(line))
            except:
                self._logger.logMessage(level="CRITICAL",message="Error while reading gizmo")
                raise
                
        if not gizmo == None: 
            gizmo.send(b'BYE  ')        
            gizmo.waitAnswer("OK-BYE")
            gizmo.close()
        
        if self._stopSwitch:
            self._logger.logMessage("Thread {0} stopped by request.".format(self.getName()), level="INFO")
