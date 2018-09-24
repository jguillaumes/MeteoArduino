import threading
from time import sleep

from weatherLib.weatherQueue import QueueJanitorThread
from weatherLib.weatherBT import WeatherBTThread
from weatherLib.weatherDB import WeatherDBThread
from weatherLib.weatherES import WeatherESThread
from weatherLib.weatherUtil import WLogger


class WatchdogThread(threading.Thread):
    """
    Class implementing a simple watchdog for the worker threads.
    It will awake periodically to check if the threads are running. If any of them
    is not, it will restart it.
    """
    _logger = WLogger()

    def __init__(self,threadList,period=120):
        super(WatchdogThread, self).__init__()

        self.theList = threadList
        self.thePeriod = period
        self._stopSwitch = False
        self._pending = False
        self.name = 'WatchdogThread'
        WatchdogThread._logger.logMessage("Watchdog configured to run every {0} seconds".format(period))

    def stop(self):
        self._stopSwitch = True

    def run(self):
        theTimer = None
        self._pending = False
        WatchdogThread._logger.logMessage("Starting thread {0}.".format(self.getName()), level="INFO")
        while not self._stopSwitch:
            if not self._pending:
                theTimer = threading.Timer(self.thePeriod,self.doWatch)
                self._pending = True
                theTimer.name = 'WatchDogTimer'
                theTimer.start()
            sleep(1)
        theTimer.cancel()
        WatchdogThread._logger.logMessage("Thread {0} stopped by request.".format(self.getName()), level="INFO")


    def doWatch(self):
        for t in self.theList:
            if t is not None:
                if not t.is_alive():
                    WatchdogThread._logger.logMessage(level="WARNING",
                                                message="Thread {0} was not running - restarting.".format(t.getName()))
                    if isinstance(t,WeatherDBThread):
                        newT = WeatherDBThread(weatherQueue = t.theQueue,
                                               weatherDB = t.theDb,
                                               event = t.theEvent,
                                               retryInterval = t.theRetryInterval)
                    elif isinstance(t,WeatherESThread):
                        newT = WeatherESThread(weatherQueue = t.theQueue,
                                               weatherES = t.theES,
                                               event = t.theEvent)
                    elif isinstance(t,WeatherBTThread):
                        newT = WeatherBTThread(address = t.theAddress,
                                               service = t.theService,
                                               queue = t.theQueue,
                                               event = t.theEvent,
                                               directory = t.theDirectory)
                    elif isinstance(t,QueueJanitorThread):
                        newT = QueueJanitorThread(qeue=t.theQueue,
                                                  period=t.thePeriod)
                    self.theList.remove(t)
                    self.theList.append(newT)
                    newT.start()
                else:
                    WatchdogThread._logger.logMessage(level="DEBUG",
                                                message="Thread {0}, OK".format(t.getName()))
            else:
                WatchdogThread._logger.logMessage(level="CRITICAL",
                                            message="One of the thread objects have been destroyed!")
        self._pending = False
        