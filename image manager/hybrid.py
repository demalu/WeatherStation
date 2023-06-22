import cv2
import numpy as np
import matplotlib.pyplot as plt

def visualize_image(image_path):
    #cv2.namedWindow("output", cv2.WINDOW_NORMAL)  # Create window with freedom of dimensions
    image = cv2.imread(image_path)  # Read image
    #im_resized = cv2.resize(image, (960, 540))  # Resize image
    #cv2.imshow("output", im_resized)
    #image = image[0:500, :]
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return image

def color_channels_split(img):
    # read the input color image
    #img = cv2.imread(image_path)
    #img = img[0:500, :]
    # split the Blue, Green and Red color channels
    blue, green, red = cv2.split(img)
    # display three channels
    #cv2.imshow('Blue Channel', blue)
    cv2.waitKey(0)
    #cv2.imshow('Green Channel', green)
    cv2.waitKey(0)
    #cv2.imshow('Red Channel', red)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return blue, red

def normalization(blue, red):
    rows = np.shape(blue)[0]
    columns = np.shape(blue)[1]
    normalized_image = np.zeros((rows, columns))
    for i in range(rows):
        for j in range(columns):

            if red[i, j] != 0:
                ratio = blue[i, j] / red[i, j]
            else:
                ratio = blue[i, j]
            normalized_image[i, j] = (ratio - 1) / (ratio + 1)
    #cv2.imshow("normalized image", normalized_image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    return normalized_image

def mu(a,b,h):
    numerator = 0
    denominator = 0
    for i in range(a, b):
        numerator += i * h[i]
        denominator += h[i]
    if denominator==0:
       denominator=0.000001
    mu_value = numerator/denominator
    return mu_value

def m(a, b, h):
    m_value = 0
    for i in range(a, b):
        m_value += i*h[i]
    return m_value

def MCE_thresholding(normalized_image, image):
    #histogram, bin_edges = np.histogram(normalized_image, bins=256)
    threshold_array = np.unique(normalized_image) #unique ratio values
    results = np.zeros((len(threshold_array), 2))
    t=0
    #print(len(threshold_array))
    while t < len(threshold_array)-1:
        #print(f"t = {t}")
        optimal_threshold_value = (-m(0, t + 1, threshold_array) * np.log(mu(0,t + 1, threshold_array))) + \
        (- m(t+1, len(threshold_array), threshold_array)*np.log(mu(t+1, len(threshold_array), threshold_array)))
        results[t,0] = optimal_threshold_value
        results[t,1] = threshold_array[t]
        t += 1
    results = np.nan_to_num(results)
    minimum = results[:,0].argmin()
    cloudiness = fixed_thresholding(results[minimum, 1], normalized_image, image)
    return cloudiness

def fixed_thresholding(threshold, normalized_image, image):
    mask_area = np.count_nonzero(image[:,:,0] == 0)
    #pixels in an unimodal image with a value of lambda_N less than T_f are detected as cloud elements, as sky otherwise
    count = 0
    for i in range(np.shape(normalized_image)[0]):
        for j in range(np.shape(normalized_image)[1]):
            #qui aggiungere che se è un pixel della maschera allora non applichi il conteggio
            if image[i, j, 0] != 0 and image[i, j, 1] != 0 and image[i, j, 2] != 0:
                if normalized_image[i, j] < threshold:
                    count += 1
                    image[i, j] = 0
    #cv2.namedWindow("output", cv2.WINDOW_NORMAL)  # Create window with freedom of dimensions
    #im_resized = cv2.resize(image, (960, 540))  # Resize image
    #cv2.imshow("Processed image", im_resized)
    # image = image[0:500, :]
    #cv2.waitKey(0)
    #cv2.imwrite("processata.png", image)
    #cv2.destroyAllWindows()
    area = (np.shape(image)[0]*np.shape(image)[1]) - mask_area
    cloudiness = round((count/area)*100,2)
    print(f"Cloudiness: {cloudiness/100} %")

    return cloudiness, image

def processing(img):
    #image = visualize_image(path)

    # -----COLOR CHANNELS SPLITTING----
    blue, red = color_channels_split(img)

    # -----PERFORMING B/R NORMALIZATION----
    normalized_image = normalization(blue, red)
    # ------CLASSIFY IMAGE----
    std = np.std(normalized_image)
    if std > 0.03:  # vaue taken from the article
        cloudiness = MCE_thresholding(normalized_image, img)  # bimodal image -> apply MCE thresolding
    else:
        cloudiness = fixed_thresholding(0.25, normalized_image,
                                        img)  # unimodal (made up of just one element, either cloud or sky)image -> apply fixed thresholding
    return cloudiness

if __name__ == "__main__":
    #-----IMAGE UPLOAD-----
    #path = "D:/Universita/Polito/Interdisciplinary/ML/rettangolare.jpg"
    path = "./masked_image_prova.png"
    image = cv2.imread(path)
    #onzero_mean = np.mean(image[image != 0])
    #image[image == 0] = nonzero_mean
    #cv2.imshow("image", image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    cloudiness = processing(image)

