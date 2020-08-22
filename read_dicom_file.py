from io import BytesIO
from ftplib import FTP
import numpy as np
import matplotlib.pyplot as plt
import pydicom as dicom
import os

class IndexTracker(object):
    def __init__(self, ax, X):
        self.ax = ax
        ax.set_title('Scroll to Navigate through the DICOM Image Slices')

        self.X = X
        rows, cols, self.slices = X.shape
        self.ind = self.slices//2

        self.im = ax.imshow(self.X[:, :, self.ind])
        self.update()

    def onscroll(self, event):
        print("%s %s" % (event.button, event.step))
        if event.button == 'up':
            self.ind = (self.ind + 1) % self.slices
        else:
            self.ind = (self.ind - 1) % self.slices
        self.update()

    def update(self):
        self.im.set_data(self.X[:, :, self.ind])
        ax.set_ylabel('Slice Number: %s' % self.ind)
        self.im.axes.figure.canvas.draw()


def GetFromFtpLink(domain, path):
    plots = []
    ftp = FTP(domain)
    ftp.login()
    ftp.cwd(path)
    filenames = ftp.nlst()
    
    for filename in filenames:
        file = BytesIO()
        ftp.retrbinary("RETR " + filename, file.write)
        file.seek(0)
        ds = dicom.dcmread(file)
        ftp.retrbinary("RETR " + filename, open(filename, 'wb').write)
        print(filename)
        pix = ds.pixel_array
        plots.append(pix)
        
        if(filename == 'IM_0022'):
            break
        
    return plots


def GetFromLocal(path):
    plots = []
    
    for i in os.listdir(path):
        file = path + "//" + i
        ds = dicom.dcmread(file)
        pix = ds.pixel_array
        plots.append(pix)

    return plots

# read dicom from local storage
local_path = 'your folder dicom image'

# read dicom from ftp URF
ftp_domain = 'medical.nema.org'
ftp_path = 'medical/dicom/DataSets/WG16/Philips/ClassicSingleFrame/Brain/DICOM/'

# init pyplot
fig, ax = plt.subplots(1,1)

# function for FTP link (un-comment to exec it)
# list_binary = GetFromFtpLink(ftp_domain, ftp_path)

# function for local
list_binary = GetFromLocal(local_path)
y = np.dstack(list_binary)

tracker = IndexTracker(ax, y)
fig.canvas.mpl_connect('scroll_event', tracker.onscroll)
plt.show()
