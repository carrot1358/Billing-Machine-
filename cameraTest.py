import cv2
def get_webcams():
    port_ids = []
    for port in range(10):
        print("Looking for a camera in port %s:" %port)
        try:
            camera = cv2.VideoCapture(port)
            if camera.isOpened():
                ret = camera.read()[0]
                if ret:
                    backendName =camera.getBackendName()
                    w = camera.get(3)
                    h = camera.get(4)
                    print("Camera %s (%s x %s) found in port %s " %(backendName,h,w, port))
                    port_ids.append(port)
                camera.release()
        #trow exception if camera not found
        except:
            pass
    return port_ids

if __name__ == '__main__':
    print(get_webcams())