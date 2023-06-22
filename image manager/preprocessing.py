from defisheye import Defisheye
import cv2
import numpy as np
import matplotlib.pyplot as plt

def gamma_function(channel, gamma):
    invGamma = 1 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")  # creating lookup table
    channel = cv2.LUT(channel, table)
    return channel

def increase_cool(img1):
    cool = 1
    cool /= 2
    img1[:, :, 0] = gamma_function(img1[:, :, 0], 1 + cool)  # down scaling blue channel
    img1[:, :, 2] = gamma_function(img1[:, :, 2], 1 - cool)  # up scaling red channel
    hsv1 = cv2.cvtColor(img1, cv2.COLOR_BGR2HSV)
    hsv1[:, :, 1] = gamma_function(hsv1[:, :, 1], 1 - cool + 0.01)  # up scaling saturation channel
    img1 = cv2.cvtColor(hsv1, cv2.COLOR_HSV2BGR)
    #cv2.imshow("immagine", img1)
    #cv2.imwrite("D:/Universita/Polito/Interdisciplinary/ML/prova.png", img1)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    return img1

def maskapplication(image, mask_path):
    mask = cv2.imread(mask_path)
    #plt.imshow(mask, cmap='gray')
    #plt.show()
    inverted_mask = cv2.bitwise_not(mask)
    #cv2.imwrite("./mask.png", inverted_mask)
    # Display the mask

    #masked_image = cv2.bitwise_and(image, image, mask=inverted_mask)
    masked_image = cv2.bitwise_and(image, mask)
    #cv2.imwrite("./masked_image.png", masked_image)
    # Display the original image and the masked image side by side
    '''
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    ax1.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    ax1.set_title('Original Image')
    ax1.axis('off')
    ax2.imshow(cv2.cvtColor(masked_image, cv2.COLOR_BGR2RGB))
    ax2.set_title('Masked Image')
    ax2.axis('off')
    plt.show()
    '''
    return masked_image

def undistort(img):
    dtype = 'linear'
    format = 'fullframe'
    fov = 181
    pfov = 142

    img_out = "./rettangolare.jpg"
    obj = Defisheye(img, dtype=dtype, format=format, fov=fov, pfov=pfov)
    # To save image locally
    obj.convert(outfile=img_out)
    # To use the converted image in memory
    new_image = obj.convert()
    return new_image

def preprocessing(image):
    #Trasformazione da fisheye a rettangolare
    image= undistort(image)

    #Applicazione maschera
    mask_path = "./mask.png"
    image = maskapplication(image, mask_path)

    #Color adjustment
    image = increase_cool(image)
    #cv2.imshow("cool", image)
    return image