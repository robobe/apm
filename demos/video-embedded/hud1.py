import cv2
import threading
import signal
import sys
import time
from dronekit import connect

font                   = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (200,200)
fontScale              = 2
fontColor              = (255,0,0)
lineType               = 2

class Observer(object):
    def __init__(self):
        self._fns = []
    def __iadd__(self, fn):
        self._fns.append(fn)
        return self
    def __isub__(self, fn):
        self._fns.remove(fn)
        return self
    def fire(self, *args, **kwargs):
        for f in self._fns[:]:
            f(*args, **kwargs)

class Rover():
    def __init__(self):
        self.__vehicle = None
        self.on_data = Observer()
        self.__connect()

    def __connect(self):
        connection_string = "udp:127.0.0.1:14551"
        print(f"Connecting to vehicle on: {connection_string}")
        self.__vehicle = connect(connection_string, wait_ready=True)
        self.__register()

    def __register(self):
        self.__vehicle.add_message_listener("BATTERY_STATUS", self.__cb)

    def __cb(self, x, name, message):
        self.on_data.fire(message.voltages[0])

    

class Hud():
  
    RTSP_IN_PIPE = "rtspsrc location=rtsp://localhost:8554/test \
	! queue \
	! rtph264depay \
	! h264parse \
	! avdec_h264 \
	! videoconvert \
	! videoscale \
	! video/x-raw,width=640,height=480 \
    ! videoconvert ! timeoverlay ! appsink"

    TEST_IN_PIPE = "videotestsrc ! video/x-raw,width=640,height=480,framerate=10/1 ! videoconvert ! timeoverlay ! appsink"
    
    OUT_PIPE = "appsrc \
        ! video/x-raw,width=640,height=480,framerate=10/1 \
        ! videoconvert \
        ! timeoverlay xpad=100 ypad=100 \
        ! x264enc \
        ! rtph264pay \
        ! udpsink host=127.0.0.1 port=5600"

    def __init__(self):
        self.cap = cv2.VideoCapture(Hud.RTSP_IN_PIPE)
        self.out = cv2.VideoWriter(Hud.OUT_PIPE, 0, 10.0, (640,480))
        self.__stop_reqest = False
        self.__data = 'Hello World!'

    def start(self):
        t = threading.Thread(target=self.__start)
        t.setDaemon(False)
        t.setName("video")
        t.start()

    def stop(self):
        print("Try to stop video")
        self.__stop_reqest = True

    def set_data(self, value):
        if value is None:
            return
        self.__data = value

    def __start(self):
        while True:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    continue
                # cv2.imshow("cv", frame)
                cv2.putText(frame,
                    str(self.__data),
                    bottomLeftCornerOfText, 
                    font, 
                    fontScale,
                    fontColor,
                    lineType)
                self.out.write(frame)
                if self.__stop_reqest:
                    break
            except Exception as e:
                print(e)
            # if cv2.waitKey(1) & 0xff == ord('q'):
        
        
        self.cap.release()
        self.out.release()
        print("Video stream stopped")    
            # cv2.destroyAllWindows()



def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    hud.stop()

    # Wait worker thread to close resources
    sys.stdout.flush()
    sys.exit(0)

if __name__ == "__main__":
    hud = Hud()
    hud.start()
    rover = Rover()
    rover.on_data += hud.set_data

    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C')
    signal.pause()
    

    """
    gst-launch-1.0 rtspsrc location=rtsp://localhost:8554/test \
        ! queue ! rtph264depay ! h264parse \
        ! avdec_h264 \
        ! videoconvert \
        ! videoscale \
        ! video/x-raw,width=640,height=480 \
        ! autovideosink
    """