from ImageData import OrigPic, WaveletPic, FVExtraction
from bokeh.plotting import figure, output_file, show
from bokeh.io import output_notebook

class FVVisualization():

    t = OrigPic("images/MMCBNU_6000/003/R_Ring/01.bmp")
    im = OrigPic("images/MMCBNU_6000/003/R_Fore/01.bmp")

    w = WaveletPic()

    f = FVExtraction(4,4)
    v = FVExtraction(4,4)

    f.do(t)
    v.do(im)

    def EvenOddSum(a, n):
        even = 0
        odd = 0
        for i in range(n):

            # Loop to find evem, odd Sum
            if i % 2 == 0:
                even += a[i]
            else:
                odd += a[i]

        print ("Even index positions sum ", even)
        print ("Odd index positions sum ", odd)

    print ("| ------------------------ |")
    n = len(f.data)
    #print ("FeatureVictores are ", f.data)
    EvenOddSum(f.data, n)
    print ("| ------------------------ |")
    m = len(v.data)
    #print ("FeatureVictores are ", v.data)
    EvenOddSum(v.data, m)
    print ("| ------------------------ |")
