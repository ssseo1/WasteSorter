import cv2
import numpy as np
import os
import time

# parameters
NUM_WORDS = 200

# file path setup
rootdir = os.getcwd()
datadir = os.path.join(rootdir,'dataset')
object_list = sorted(os.listdir(datadir))

# measure processing time
start_time = time.time()

# dictionary and extractor list setup
# orb = cv2.ORB_create()
sift = cv2.SIFT_create()
# surf = cv2.xfeatures2d.SURF_create() # patented
bow_trainer = cv2.BOWKMeansTrainer(NUM_WORDS) # vocab size

# create a dictionary for each object and its sample images
# iterate through each object type
for object in object_list:
    objectdir = os.path.join(datadir, object)
    object_samples = os.listdir(objectdir)
    # iterate through sample images of each object
    for sample_image in object_samples:
        filepath = os.path.join(objectdir,sample_image)
        image = cv2.imread(filepath, 0)     # 0 loads as grayscale

        # extract features from each image and add it to the BoW
        keypoints, descriptors = sift.detectAndCompute(image, None)
        bow_trainer.add(descriptors)

# perform k-means clustering on the list of descriptors to create a visual dictionary
dictionary = bow_trainer.cluster()
np.save(f"SIFT_dictionary_{NUM_WORDS}_final.npy", dictionary)
end_time = time.time()
proc_time = end_time - start_time
print(f"Generate Vocab Proc Time: {proc_time:.4f} s\n")