import cv2
import numpy as np

# Carica l'immagine fisheye
img_fisheye = cv2.imread("fisheye.png")

# Definisci i parametri della proiezione equiareale
f = 60 # lunghezza focale
w = img_fisheye.shape[1]  # larghezza dell'immagine
h = img_fisheye.shape[0]  # altezza dell'immagine
cx = w/2  # coordinata x del centro dell'immagine
cy = h/2  # coordinata y del centro dell'immagine

# Crea una mappa di distorsione per la proiezione equiareale
map_x = np.zeros((h, w), np.float32)
map_y = np.zeros((h, w), np.float32)
for i in range(h):
    for j in range(w):
        theta = np.arctan2(i - cy, j - cx)
        r = f * theta
        x = int(cx + r * np.cos(theta))
        y = int(cy + r * np.sin(theta))
        if x >= 0 and x < w and y >= 0 and y < h:
            map_x[i, j] = x
            map_y[i, j] = y

# Applica la mappa di distorsione per ottenere l'immagine rettangolare
img_rect = cv2.remap(img_fisheye, map_x, map_y, cv2.INTER_LINEAR)

# Salva l'immagine rettangolare
cv2.imwrite("rectangular.png", img_rect)