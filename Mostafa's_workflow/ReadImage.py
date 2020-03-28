
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image, ImageFilter, ImageDraw
import pywt
import pywt.data

class ReadImage:
    def do(image):
        #plt.ylabel('Quadratzahlen')
        #plt.plot([1,2,3,4], [1,4,9,16], 'bo')
        #plt.axis([0,5,0,20])
        #plt.grid(True)
        #plt.show()

        original = Image.open(image).convert('LA')#pywt.data.camera()#

        #original.save('../greyscale.png')
        #original = Image.open('../greyscale.png')
        titles = ['Approximation', ' Horizontal detail', 'Vertical detail', 'Diagonal detail']
        coeffs2 = pywt.dwt2(original, 'bior1.3')
        LL, (LH, HL, HH) = coeffs2
        fig = plt.figure(figsize=(12, 3))
        for i, a in enumerate([LL, LH, HL, HH]):
            ax = fig.add_subplot(1, 4, i + 1)
            ax.imshow(a, interpolation="nearest", cmap=plt.cm.gray)
            ax.set_title(titles[i], fontsize=10)
            ax.set_xticks([])
            ax.set_yticks([])

        fig.tight_layout()
        plt.show()
