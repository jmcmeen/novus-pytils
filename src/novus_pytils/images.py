import cv2
from skimage import metrics

def ssim_score(image1_path, image2_path):
    image1 = cv2.imread(image1_path)
    image2 = cv2.imread(image2_path)
    image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]), interpolation = cv2.INTER_AREA)
    ssim_score = metrics.structural_similarity(image1, image2, full=True, channel_axis=2)
    return round(ssim_score[0], 3)