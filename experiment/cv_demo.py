import cv2
import numpy as np

def cv_show(name,img):
    cv2.namedWindow(name,0)
    cv2.resizeWindow(name, 600, 800)
    cv2.imshow(name, img)  
    cv2.waitKey(0)  
    cv2.destroyAllWindows()

img = cv2.imread ('/Users/jiadong/project/WeChat/experiment/raw.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  #图像从BGR转为灰度
binary_image = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
# cv_show('ss',binary_image)

contours,hierarchy = cv2.findContours(binary_image,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)   #查找图像轮廓
contours = sorted(contours, key=cv2.contourArea, reverse=True)[2:35]  #这里的[2:35]是需要调试出来的

mask = np.zeros_like(binary_image)
cv2.drawContours(mask, contours, -1, (255), thickness=cv2.FILLED) # 在全黑的mask进行绘制
result = cv2.bitwise_and(binary_image, mask)

# 展示 and 保存
# cv_show('s',result)
cv2.imwrite('masked.jpg', result)

