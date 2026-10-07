"""Interactive contour-based steel ball detection prototype."""
import cv2
import numpy as np
import argparse
import time
import imutils
from collections import deque
from math import pi


def updateLowThreshold( *args ):
    global lowThreshold
    lowThreshold = args[0]
    pass

def updateHighThreshold( *args ):
    global highThreshold
    highThreshold = args[0]
    pass

def updateBlurAmount( *args ):
    global blurAmount
    blurAmount = args[0]
    pass

def updateApertureIndex( *args ):
    global apertureIndex
    apertureIndex = args[0]
    pass


def update_threshold( *args ):
    global apertureIndex
    apertureIndex = args[0]
    pass


def nothing(x):
    pass


def detect(c):

		shape = "Indefinida"

		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.04 * peri, True)


		if len(approx) == 3:
			shape = "Triangulo"

		elif len(approx) == 4:
			(x, y, w, h) = cv2.boundingRect(approx)
			ar = w / float(h)
			shape = "Cuadrado" if ar >= 0.95 and ar <= 1.05 else "Rectangulo"

		elif len(approx) == 5:
			shape = "Pentagram"

		else:
			shape = "Circulo"


		return shape



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-i", "--input", default="0",
                        help="Video path or camera index (default: 0)")
    parser.add_argument("--logo", help="Optional transparent PNG overlay")
    args = parser.parse_args()
    source = int(args.input) if args.input.isdecimal() else args.input

    logo_bgr = logo_alpha = None
    if args.logo:
        logo = cv2.imread(args.logo, cv2.IMREAD_UNCHANGED)
        if logo is None or logo.ndim != 3 or logo.shape[2] != 4:
            parser.error("--logo must be a readable PNG with an alpha channel")
        logo = cv2.resize(logo, (201, 67))
        logo_bgr = logo[:, :, :3].astype(np.float32)
        logo_alpha = logo[:, :, 3:4].astype(np.float32) / 255.0

    pts = deque(maxlen=64)

    #INCIAL VALUES
    lowThreshold = 0
    highThreshold = 255

    maxThreshold = 255

    apertureSizes = [3, 5, 7]
    maxapertureIndex = 2
    apertureIndex = 0

    blurAmount = 0
    maxBlurAmount = 20

    low_threshold=0
    high_threshold=255
    max_threshold=255


    sleep_=10


    #WINDOWS PARAMETERS
    name_of_windows = "Configuracion"
    cv2.namedWindow(name_of_windows, cv2.WINDOW_AUTOSIZE)
    cv2.createTrackbar("Time Sleep", name_of_windows, 1, 200, nothing)

    cv2.createTrackbar("LH", name_of_windows, 0, 255, nothing)
    cv2.createTrackbar("LS", name_of_windows, 0, 255, nothing)
    cv2.createTrackbar("LV", name_of_windows, 0, 255, nothing)
    cv2.createTrackbar("UH", name_of_windows, 255, 255, nothing)
    cv2.createTrackbar("US", name_of_windows, 255, 255, nothing)
    cv2.createTrackbar("UV", name_of_windows, 255, 255, nothing)
    
    cv2.createTrackbar( "Gaussian Blur", name_of_windows, blurAmount, maxBlurAmount, updateBlurAmount)

    cv2.createTrackbar( "Canny Low Threshold", name_of_windows, lowThreshold, maxThreshold, updateLowThreshold)
    cv2.createTrackbar( "Canny High Threshold", name_of_windows, highThreshold, maxThreshold, updateHighThreshold)
    cv2.createTrackbar( "Canny aperture Size", name_of_windows, apertureIndex, maxapertureIndex, updateApertureIndex)

    cv2.createTrackbar( "Threshold Binary Low", name_of_windows, low_threshold, max_threshold, nothing)
    cv2.createTrackbar( "Threshold Binary High", name_of_windows, high_threshold, max_threshold, nothing)


    #START CAPTURE
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        cap.release()
        cv2.destroyAllWindows()
        parser.error("Cannot open input video or camera")


    try:
        while True:

            #Leer imagen
            flag, img = cap.read()
            if not flag or img is None:
                break
            frame=cv2.resize(img,(720,480))
            frame1 = frame.copy()

            #ratio = img.shape[0] / float(frame.shape[0])
            ratio=1

            #Filtro por color HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            l_h = cv2.getTrackbarPos("LH", name_of_windows)
            l_s = cv2.getTrackbarPos("LS", name_of_windows)
            l_v = cv2.getTrackbarPos("LV", name_of_windows)

            u_h = cv2.getTrackbarPos("UH", name_of_windows)
            u_s = cv2.getTrackbarPos("US", name_of_windows)
            u_v = cv2.getTrackbarPos("UV", name_of_windows)

            l_b = np.array([l_h, l_s, l_v])
            u_b = np.array([u_h, u_s, u_v])

            mask = cv2.inRange(hsv, l_b, u_b)

            res = cv2.bitwise_and(frame, frame, mask=mask)
            final_imagen=res

            cv2.imshow("Filtro hsv",final_imagen)

     
            # Convert it to grayscale, blur it slightly
            h, s, v1 = cv2.split(final_imagen)
            gray=v1


            #blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # perform a series of erosions and dilations to remove
            # any small blobs of noise from the thresholded image
            gray = cv2.erode(gray, None, iterations=1)
            gray = cv2.dilate(gray, None, iterations=1)


            #Filtro Gaussiano - Canny
            if (blurAmount > 0):
                blurredSrc = cv2.GaussianBlur(gray, (2 * blurAmount + 1, 2 * blurAmount + 1), 0)
            else:
                blurredSrc = gray.copy()

            cv2.imshow("blurredSrc",blurredSrc)
            

            # Canny requires aperture size to be odd
            apertureSize = apertureSizes[apertureIndex]

            # Apply canny to detect the images
            #blurredSrc = cv2.bilateralFilter(blurredSrc, 11, 17, 17)
            edges = cv2.Canny(blurredSrc, lowThreshold, highThreshold, apertureSize = apertureSize)
            cv2.imshow("Canny",edges)

            thresh=edges

            threshold_low_value  = cv2.getTrackbarPos("Threshold Binary Low", name_of_windows)
            threshold_high_value = cv2.getTrackbarPos("Threshold Binary High", name_of_windows)

            thresh = cv2.threshold(thresh, threshold_low_value, threshold_high_value, cv2.THRESH_BINARY)[1]
            cv2.imshow("thresh",thresh)


            # find contours in the thresholded imageq
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            #cnts = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            #cnts = cv2.findContours(thresh.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            center = None

            # loop over the contours
            for c in cnts:

                #Calculo del Momemtum
                M = cv2.moments(c)

                #Obtener radio minimo
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                center = (int(x),int(y))

                if (M["m00"] != 0): # and (radius>10) and (radius<50):

                    #Obtener centroides
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                    #Area y perimetro real del objeto detectado
                    area = cv2.contourArea(c)
                    perimeter = cv2.arcLength(c,True)

                    #Area circulo del area minima
                    area_circulo= pi * radius ** 2

                    #Calcular diferencia porcentual entre una y otra
                    diferencia = (area_circulo-area)*100/area

                    if diferencia<=100:

                        # Imprimir info de radio detectado
                        radius_ = ("Radio min: {0} px".format(round(radius,2)))
                        cv2.putText(frame, radius_, (cX - 20, cY - 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                        # Imprimir info de radio detectado
                        area_circulo_ = ("Area Circulo: {0} px2".format(round(area_circulo,2)))
                        cv2.putText(frame, area_circulo_, (cX - 20, cY - 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                        # Imprimir info de radio detectado
                        area_ = ("Area Objeto: {0} px2".format(round(area,2)))
                        cv2.putText(frame, area_, (cX - 20, cY - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                        # Imprimir info de radio detectado
                        diferencia_= ("Diferencia: {0} %".format(round(diferencia,2)))
                        cv2.putText(frame, diferencia_, (cX - 20, cY - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)


                        # multiply the contour (x, y)-coordinates by the resize ratio,
                        c = c.astype("float")
                        c *= ratio
                        c = c.astype("int")
                    
                        #Dibujar contorno real del objeto
                        cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)

                        # Dibujar circunferencia de radio igual al radio minimo. 
                        cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                        cv2.circle(frame, center, 5, (0, 0, 255), -1)

                        #Identificacion dentro del circulo
                        # shape = detect(c)
                        # cv2.putText(frame, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)



            # Optional PNG overlay, loaded once before processing
            if logo_bgr is not None:
                roi = frame[20:87, 499:700].astype(np.float32)
                frame[20:87, 499:700] = np.rint(
                    roi * (1.0 - logo_alpha) + logo_bgr * logo_alpha
                ).astype(np.uint8)

            #Imagen Final
            cv2.imshow("IMAGEN",frame)


            #Tiempo espera final
            sleep_ = cv2.getTrackbarPos("Time Sleep", name_of_windows)
            # Read the keyboard once so Escape is not consumed prematurely
            key = cv2.waitKey(max(1, sleep_)) & 0xFF
            if key == 27:
                break


    finally:
        cap.release()
        cv2.destroyAllWindows()

