'''
ECE276A WI22 PR1: Color Classification and Recycling Bin Detection
'''

import os
import sys
import numpy as np
import cv2
import random
import pdb
from matplotlib import pyplot as plt
import skimage.measure as skm
PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PATH)
from logistic2 import Logistic
from skimage.measure import label, regionprops

w_path = os.path.join(PATH, 'ww.npy')
b_path = os.path.join(PATH, 'bb.npy')

class BinDetector():
	def __init__(self):
		"""
		Initilize your bin detector with the attributes you need,
		e.g., parameters of your classifier
		"""
		
		self.color_space = cv2.COLOR_BGR2RGB
		self.model = Logistic()
		if os.path.exists(w_path) and os.path.exists(b_path):
			self.model.load_param(w_path, b_path)
		else:
			print('parameter not found! start training...')
			self.training()

	def training(self):
		"""
		Train your color classifier if model parameters not found.
		"""
		print('parameter not found! start training...')
		# folder_path = os.path.join(dir_path, 'training')

		file_path = os.path.join(PATH, 'selected_img.npy')
		img = np.load(file_path)
		training_set = img[:, :3]
		training_label = img[:, 3]
		self.model.fit(training_set, training_label)
		self.model.save_param(w_path, b_path)


	def segment_image(self, img):
		'''
			Obtain a segmented image using a color classifier,
			e.g., Logistic Regression, Single Gaussian Generative Model, Gaussian Mixture, 
			call other functions in this class if needed
			
			Inputs:
				img - original image
			Outputs:
				mask_img - a binary image with 1 if the pixel in the original image is red and 0 otherwise
		'''
		################################################################
		# YOUR CODE AFTER THIS LINE
		
		img = cv2.cvtColor(img, self.color_space)
		img = img.astype(np.float32)/255.0
		pixels = img.reshape([-1, 3])
		label = self.model.predict(pixels)
		mask_img = np.reshape(label == 0, (img.shape[0], img.shape[1]))
		return mask_img

		# Replace this with your own approach 
		# YOUR CODE BEFORE THIS LINE
		################################################################

	def get_bounding_boxes(self, img):
		'''
			Find the bounding boxes of the recycling bins
			call other functions in this class if needed
			
			Inputs:
				img - original image
			Outputs:
				boxes - a list of lists of bounding boxes. Each nested list is a bounding box in the form of [x1, y1, x2, y2] 
				where (x1, y1) and (x2, y2) are the top left and bottom right coordinate respectively
		'''
		boxes = []
		total_size = img.shape[0] * img.shape[1]
		img = img * 255
		cv2.imwrite('mask.png', img)
		img = cv2.imread('mask.png')
		img2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

		kernel = np.ones((8,8), np.uint8)
		erode = cv2.erode(img2, kernel, iterations = 1)
		dilation = cv2.dilate(erode, kernel[:5,:5], iterations = 3)
		img2 = cv2.GaussianBlur(dilation, (3,3),0)

		ret, thresh = cv2.threshold(img2, 1, 255, cv2.THRESH_OTSU)
		contours, heirarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		for c in contours:
			approx = cv2.approxPolyDP(c, 0.01*cv2.arcLength(c, True), True)
			M = cv2.moments(c)
			if M['m00'] != 0:
				x = int(M['m10']/M['m00'])
				y = int(M['m01']/M['m00'])
			if len(approx) == 4 or 5 or 6 or 7:
				x, y, w, h = cv2.boundingRect(c)
				# if x != 0 and y != 0 and w != img.shape[1] and h != img.shape[0]:
				if 0.05 * total_size < w * h < 0.3 * total_size and 0.2 < h/w < 4:
					boxes.append([x, y, x+w, y+h])
		return boxes



if __name__ == "__main__":
	detector = BinDetector()
	detector.load_param()
	# folder = './data/validation'
	folder = './data/training'
