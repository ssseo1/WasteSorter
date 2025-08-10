import cv2
import numpy as np
import os
import time

# parameters
NUM_WORDS = 10
# MATCH_TYPE = "BF"
MATCH_TYPE = "FLANN"

# file path setup
rootdir = os.getcwd()
datadir = os.path.join(rootdir,'dataset')
object_list = sorted(os.listdir(datadir))

# measure processing time
start_time = time.time()

# dictionary and extractor list setup
# orb = cv2.ORB_create()
sift = cv2.SIFT_create()
# surf = cv2.xfeatures2d.SURF_create()
if MATCH_TYPE == "BF":
    matcher = cv2.BFMatcher()
    print('BF')
else:
    matcher = cv2.FlannBasedMatcher(dict(algorithm=1, trees=5), {})
    print('FLANN')

# load in BoW dictionary and create extractor
loaded_vocab = np.load(f"SIFT_dictionary_{NUM_WORDS}_final.npy")
bow_extract = cv2.BOWImgDescriptorExtractor(sift,matcher)
bow_extract.setVocabulary(loaded_vocab)

# initialize arrays
desc_list = []
name_list = []
name_LUT = {}
name_id = 0

# for each object type
for object in object_list:
    objectdir = os.path.join(datadir, object)
    object_samples = os.listdir(objectdir)
    # cv2.svm only accepts numbers so we need to map the object names to numeric labels
    name_LUT[object] = name_id
    name_id += 1

    # for each sample image of an object
    for sample_image in object_samples:
        filepath = os.path.join(objectdir,sample_image)
        image = cv2.imread(filepath, 0)     # 0 loads as grayscale

        # extract BoW features from each image -- this is a freq histogram of visual words from dictionary
        keypoints, descriptors = sift.detectAndCompute(image, None)
        bow_descript = bow_extract.compute(image,keypoints)
        desc_list.append(bow_descript.flatten())    # flatten to get rid of the extra dimension
        name_list.append(name_LUT[object])

# one row for one picture, each column is the frequency of one of the 200 visual words
trainingData = np.matrix(desc_list,dtype=np.float32)
labels = np.array(name_list)

end_time = time.time()
proc_time = end_time - start_time
print(f"Extract BoW Features Proc Time: {proc_time:.4f} s\n")


start_time = time.time()
# train an SVM model to associate object names with sets of features
svm = cv2.ml.SVM_create()
svm.trainAuto(trainingData, cv2.ml.ROW_SAMPLE, labels)
svm.save(f"SIFT_{MATCH_TYPE}_{NUM_WORDS}_final.xml")
end_time = time.time()
proc_time = end_time - start_time
print(f"Train SVM Proc Time: {proc_time:.4f} s\n")