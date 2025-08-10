import cv2
import numpy as np
import os

def identifyObject(test_image):
    # parameters
    NUM_WORDS = 200
    MATCH_TYPE = "BF"
    # MATCH_TYPE = "FLANN"

    rootdir = os.getcwd()
    datadir = os.path.join(rootdir,'dataset')
    object_list = sorted(os.listdir(datadir))

    name_LUT = object_list

    sift = cv2.SIFT_create()
    if MATCH_TYPE == "BF":
        matcher = cv2.BFMatcher()
    else:
        matcher = cv2.FlannBasedMatcher(dict(algorithm=1, trees=5), {})

    # load in BoW dictionary and create extractor
    loaded_vocab = np.load(f"SIFT_dictionary_{NUM_WORDS}_final.npy")
    bow_extract = cv2.BOWImgDescriptorExtractor(sift,matcher)
    bow_extract.setVocabulary(loaded_vocab)

    # Now create a new SVM & load the model:
    svm = cv2.ml.SVM_load(f"SIFT_{MATCH_TYPE}_{NUM_WORDS}_final.xml")

    # load in a new image and classify the object
    # test_image = cv2.imread(path, 0)
    keypoints, descriptors = sift.detectAndCompute(test_image, None)
    bow_descript = bow_extract.compute(test_image,keypoints)

    # reformat and predict
    test = np.matrix(bow_descript.flatten(),dtype=np.float32)
    id = svm.predict(test)[1]
    id = int(id[0][0])
    print(name_LUT[id])
    return name_LUT[id]

def takeSinglePicture():
    video_capture = cv2.VideoCapture(0)
    ret, frame = video_capture.read()
    while(not ret or not frame.any()):
        ret, frame = video_capture.read()
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    video_capture.release()
    cv2.destroyAllWindows()
    return image

def takeMultiPic(num_caps):
    video_capture = cv2.VideoCapture(0)
    ret, frame = video_capture.read()
    while(not ret or not frame.any()):
        ret, frame = video_capture.read()

    images = []
    # take num_caps number of frames
    for i in range(num_caps):
        ret, frame = video_capture.read()
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        images.append(image)

    video_capture.release()
    cv2.destroyAllWindows()
    return images

if __name__ == "__main__":
    identifyObject(cv2.imread('testset/napkin/napkin_26.png', cv2.COLOR_BGR2GRAY))
    # identifyObject(takePicture())