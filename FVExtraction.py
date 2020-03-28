
from IProcess import IProcess, EDataType

from PIL import Image
from numpy import *


class FVExtraction(IProcess):

    def __init__(self, number_of_blocks_vertical=32, number_of_blocks_horizontal=32, ignoreLastDetail=True):
        IProcess.__init__(self)

        self.vertical = number_of_blocks_vertical
        self.horizontal = number_of_blocks_horizontal
        self.levelOfM = 0
        self.sumOfFeatures = 0
        self.ignoreLastDetail = ignoreLastDetail
        # Die Hoehe/Breite des Bildes sollte ohne Rest durch die Anzahl an vertikale/horizontalen Bloecken teilbar sein,
        # sonst werden am rechten und unteren Rand Spalten und Zeilen nicht bei der Bildung der Bloecke beruecksichtigt.

        pass

    def toId(self):
        return str(__class__.__name__)+"_BV"+str(self.vertical)+"_BH"+str(self.horizontal)

    def getType(self):
        return EDataType.FeatureVector

    def do(self, img):
        if self.levelOfM == 0:
            IProcess.do(self, img)
            self.data = []  # Delete previous data.
        else: # If features are arleady present, denormalize again.
            for i in range(len(self.data)):
                self.data[i] = self.data[i] * self.sumOfFeatures
        self.levelOfM += 1

        Vi = []
        sumVi = 0
        E = 0

        details = img.data
        if self.ignoreLastDetail:
            details = details[:-1]
        
        for data in details:
            block_size_vertical = ceil(data.height / self.vertical)
            block_size_horizontal = ceil(data.width / self.horizontal)
            block_size = self.vertical * self.horizontal
            Vi = Vi + ([0] * int(block_size))

            # Traverse each 
            for y in range(data.height):
                for x in range(data.width):
                    pixel = data.getpixel((x, y))
                    pixelSquared = pixel * pixel
                    
                    blockX = int(floor(x / block_size_horizontal))
                    blockY = int(floor(y / block_size_vertical) * self.horizontal)
                    index = int(E + blockY + blockX)
                    
                    try:
                        Vi[index] += pixelSquared
                    except IndexError:
                        print("Test: "+str(len(details))+" vs "+str(data.size)+" Index: "+str(index)+" ViSize: "+str(len(Vi))+" BlockSize: "+str(block_size))
                        print("E: "+str(E)+" Width: "+str(data.width)+" and Height: "+str(data.height)+" X: "+str(x)+" Y: "+str(y))
                        print("BlockX: "+str(blockX)+" BlockY: "+str(blockY))
                        print("BlockAmountX: "+str(block_size_horizontal)+" BlockAmountY: "+str(block_size_vertical))
                        raise

                    sumVi += pixelSquared
                    pass
                pass

            E += block_size
            #print("Dimension E: "+str(E))
            pass

        self.sumOfFeatures += sumVi
        self.data = self.data + Vi

        # Normalize values with new concentenated list.
        for i in range(len(self.data)):
            if self.sumOfFeatures == 0:
                self.data[i] = 0.0
            else:
                self.data[i] = self.data[i] / self.sumOfFeatures

        return self
