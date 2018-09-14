import bluetooth as bt
import time as tm

from weatherLib.weatherUtil import WLogger

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
        
    @staticmethod
    def connect_wait(address,service):
        """
        Connect (create) a BT object, with timed retries
        Parameters:
            - address: BT address of the device, in hex form (XX:XX:XX:XX:XX:XX)
            - service: UUID of the RFCOMM service in the device
        Returns:
            The created object
        """            
        phase=0
        retrChangePhase=10
        delays=[5,60]
        while True:
            try:
                theBT = WeatherBT(addr=address, serv=service)
                WeatherBT._logger.logMessage(level="INFO",message="Connected to weather service at {0:s} : {1:s}"  \
                           .format(theBT.theName,address))
                return theBT
            except:
                WeatherBT._logger.logMessage(level="WARNING",
                                       message="BT Connection atempt failed")
                if phase == 0:
                    tm.sleep(delays[0])
                    retrChangePhase -= 1
                    if retrChangePhase <= 0:
                        phase = 1
                        msg = 'Switching to {0:d} seconds delay.'.format(delays[1])
                        WeatherBT._logger.logMessage(level="INFO",message=msg)
                    else:
                        pass
                else:
                    tm.sleep(delays[1])

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
