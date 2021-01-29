import colorsys
import random
import sys
from PyQt5.QtCore import QMutex, QThread, QWaitCondition, pyqtSignal
from PyQt5.QtGui import QStandardItem, QStandardItemModel
import matplotlib
from skimage.measure import find_contours
from matplotlib import patches
import numpy as np
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import *
from PyQt5 import uic

from boundingbox import imageAnalysis, videoAnalysis 

# ui 클래스
mainWindowClass = uic.loadUiType("mainwindow.ui")[0]
imageAnalysisResultDialogClass = uic.loadUiType("imageresult.ui")[0]
videoAnalysisResultDialogClass = uic.loadUiType("videoresult.ui")[0]

#메인 화면
class MainWindow(QMainWindow, mainWindowClass):
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.analysisMode = ""
        self.openFileBtn.clicked.connect(self.openFileBtnClicked)
        self.runAnalysisBtn.clicked.connect(self.runAnalysisBtnClicked)

    def runAnalysisBtnClicked(self):
            
        if self.fileNameEdit.text() == "":
            QMessageBox.about(self, "오류", "분석할 파일의 경로를 지정해주세요.")

        if self.analysisType_Video.isChecked():
            vard = VideoAnalysisResultDialog(videoAnalysis('model.h5', self.fileNameEdit.text()))
            vard.exec()
            vard.show()
        elif self.analysisType_Image.isChecked():
            iard = ImageAnalysisResultDialog(imageAnalysis('model.h5', self.fileNameEdit.text()))
            iard.exec()
            iard.show()
        else:
            QMessageBox.about(self, "오류", "분석할 자료의 종류를 선택해주세요.")

    def openFileBtnClicked(self):
        fname = QFileDialog.getExistingDirectory(self, 'Open file', './')

        if fname[0]:
            self.fileNameEdit.setText(fname[0])

class ImageAnalysisResultDialog(QDialog, imageAnalysisResultDialogClass):
    def __init__(self, image):
        super().__init__()
        self.setupUi(self)
        # image 변수에 담긴 결과 표시
        visualize(image[0], image[1], image[2], image[3], image[4], image[5], ax=self.imageWidget.canvas.ax)
        self.imageWidget.canvas.draw()
        
class VideoAnalysisResultDialog(QDialog, videoAnalysisResultDialogClass):
    def __init__(self, found_frames):
        super().__init__()
        self.setupUi(self)
        # 영상에서 발견된 프레임들을 표시
        self.found_frames = found_frames
        print(found_frames)
        self.frameWidget.canvas.ax.axes.xaxis.set_visible(False)
        self.frameWidget.canvas.ax.axes.yaxis.set_visible(False)
        self.frameWidget.canvas.ax.imshow(found_frames[list(found_frames.keys())[0]])
        print(list(found_frames.keys()))
        for key in list(found_frames.keys()):
            self.frameList.addItem(str(key))
        self.frameList.currentItemChanged.connect(self.selectedFrameChanged)

    def selectedFrameChanged(self):
        self.frameWidget.canvas.ax.imshow(self.found_frames[int(self.frameList.currentItem().text())])
        self.frameWidget.canvas.draw()


# 아래는 시각화용 코드, Mask_RCNN의 visualize.py에서 가져왔음

def random_colors(N, bright=True):
    """
    Generate random colors.
    To get visually distinct colors, generate them in HSV space then
    convert to RGB.
    """
    brightness = 1.0 if bright else 0.7
    hsv = [(i / N, 1, brightness) for i in range(N)]
    colors = list(map(lambda c: colorsys.hsv_to_rgb(*c), hsv))
    random.shuffle(colors)
    return colors

def apply_mask(image, mask, color, alpha=0.5):
    """Apply the given mask to the image.
    """
    for c in range(3):
        image[:, :, c] = np.where(mask == 1,
                                  image[:, :, c] *
                                  (1 - alpha) + alpha * color[c] * 255,
                                  image[:, :, c])
    return image

def visualize(image, boxes, masks, class_ids, class_names,
                      scores=None, title="",
                      figsize=(16, 16), ax=None,
                      show_mask=True, show_bbox=True,
                      colors=None, captions=None):
    N = boxes.shape[0]
    if not N:
        print("\n*** No instances to display *** \n")
        ax.imshow(image)
    else:
        assert boxes.shape[0] == masks.shape[-1] == class_ids.shape[0]

    # If no axis is passed, create one and automatically call show()
    auto_show = False
    if not ax:
        _, ax = plt.subplots(1, figsize=figsize)
        auto_show = True

    # Generate random colors
    colors = colors or random_colors(N)
    
    # Show area outside image boundaries.
    height, width = image.shape[:2]
    ax.set_ylim(height + 10, -10)
    ax.set_xlim(-10, width + 10)
    ax.axis('off')
    ax.set_title(title)
    masked_image = image.astype(np.uint32).copy()
    for i in range(N):
        color = colors[i]

        # Bounding box
        if not np.any(boxes[i]):
            # Skip this instance. Has no bbox. Likely lost in image cropping.
            continue
        y1, x1, y2, x2 = boxes[i]
        if show_bbox:
            p = patches.Rectangle((x1, y1), x2 - x1, y2 - y1, linewidth=2,
                                alpha=0.7, linestyle="dashed",
                                edgecolor=color, facecolor='none')
            ax.add_patch(p)

        # Label
        if not captions:
            class_id = class_ids[i]
            score = scores[i] if scores is not None else None
            label = class_names[class_id]
            caption = "{} {:.3f}".format(label, score) if score else label
        else:
            caption = captions[i]
        ax.text(x1, y1 + 8, caption,
                color='w', size=11, backgroundcolor="none")

        # Mask
        mask = masks[:, :, i]
        if show_mask:
            masked_image = apply_mask(masked_image, mask, color)
            ax.imshow(masked_image)

        # Mask Polygon
        # Pad to ensure proper polygons for masks that touch image edges.
        padded_mask = np.zeros(
            (mask.shape[0] + 2, mask.shape[1] + 2), dtype=np.uint8)
        padded_mask[1:-1, 1:-1] = mask
        contours = find_contours(padded_mask, 0.5)
        for verts in contours:
            # Subtract the padding and flip (y, x) to (x, y)
            verts = np.fliplr(verts) - 1
            p = patches.Polygon(verts, facecolor="none", edgecolor=color)
            ax.add_patch(p)

if __name__ == "__main__" :
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    app.exec()