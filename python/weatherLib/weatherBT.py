import bluetooth as bt
import time as tm

from weatherLib.weatherUtil import logMessage,logException

def connectBT(addr, serv):
    """
    Connect to bluetooth of weather sensors device
    Parameters:
        - address: BT address of the device, in hex form (XX:XX:XX:XX:XX:XX)
        - service: UUID of the RFCOMM service in the device
    """
    logMessage(level="INFO",message="Service: {0:s}, address:{1:s}".format(serv,addr))
    srvlist = bt.find_service(uuid = serv, address = addr)
    if len(srvlist) == 0:
        msg = "BT service not available."
        logMessage(level="WARNING", message=msg)
        return False, 0, ""
    else:
        srv = srvlist[0]
        port = srv["port"]
        name = srv["name"]
        host = srv["host"]
        sock=bt.BluetoothSocket(bt.RFCOMM)
        sock.connect((host,port))
        return True, sock, name

def connect_wait_BT(address,service):
    phase=0
    retrChangePhase=10
    delays=[5,60]
    while True:
        connected, sock, name = connectBT(addr=address, serv=service)
        if connected:
            logMessage(level="INFO",message="Connected to weather service at \"%s\" on %s" % (name,address))
            return sock
        else:
            if phase == 0:
                tm.sleep(delays[0])
                retrChangePhase -= 1
                if retrChangePhase <= 0:
                    phase = 1
                    msg = 'Switching to {0:d} seconds delay.'.format(delays[1])
                    logMessage(level="INFO",message=msg)
                else:
                    pass
            else:
                tm.sleep(delays[1])

def getLine(socket):
    """ 
    Read a line from a socket connection.
    It reads characters from a socket until it gets a CR+LF combination. The
    CR+LF is *not* returned as part of the read line. 
    If a line does not include the LF (the terminator is just a CR, it's
    discarded.
    Parameters:
    - socket: opened socket
    Returns:
    Received string        
    """
    line = ""
    onLoop = True                             # End of loop switch
    while onLoop:
        byte = socket.recv(1)                 # Get byte from socket
        if byte == b'\r':                     # Carriage return?
            byte = socket.recv(1)             # Consume LF
            if byte != b'\n':                 # IF not LF, big trouble: discard line
                line = ""
            else:
                onLoop = False                # End of loop, line ready
        else:
            try:
                line = line + byte.decode()   # Add character to current working line
            except UnicodeDecodeError as e:
                msg = "Error decoding received byte: {0:s}".format(repr(e))
                logMessage(level="WARNING",message=msg)
    return line                              # The line is complete
            
def waitAnswer(socket, answer,retries=5):
    """
    Wait for a specific answer, discarding all the read lines until that
    answer is read or the number of retries is exhausted.
    Parameters:
        - socket: Open socket to read
        - answer: text (6 characters) to expect
        - retries: Number of lines to read until leaving
    Returns:
        Boolean (true = anwer found, false = retries exhausted)
    """
    answ = ""
    remain = retries
    while answ != answer[0:6] and remain > 0:
        line = getLine(socket)
        logMessage(level="INFO",message=line)
        answ = line[0:6]
        remain -= 1
    return answ == answer[0:6]

