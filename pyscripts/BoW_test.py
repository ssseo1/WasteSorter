import BoW_predict
import os
import cv2
import time

# parameters
NUM_WORDS = 200
# MATCH_TYPE = "BF"
MATCH_TYPE = "FLANN"

rootdir = os.getcwd()
datadir = os.path.join(rootdir,'testset')
object_list = sorted(os.listdir(datadir))

score = 0
total = 0

f = open(f"SIFT_{MATCH_TYPE}_{NUM_WORDS}_Results.txt", 'w')

# measure processing time
start_time = time.time()

for object in object_list:
    obj_score = 0
    obj_total = 0
    objectdir = os.path.join(datadir, object)
    object_images = os.listdir(objectdir)

    for test_image in object_images:
        filepath = os.path.join(objectdir,test_image)
        image = cv2.imread(filepath, 0)   
        objectName = BoW_predict.identifyObject(image)
        f.write(f"Actual: {object}, Prediction: {objectName}\n")
        print(f"Actual: {object}, Prediction: {objectName}\n")
        if objectName == object:
            score += 1
            obj_score += 1
            total += 1
            obj_total += 1 
        else:
            total += 1
            obj_total += 1 
    obj_percent = round(100*obj_score/obj_total,2)
    f.write(f"Object Accuracy: {obj_score}/{obj_total} correct, {obj_percent}%\n\n")
    print(f"Object Accuracy: {obj_score}/{obj_total} correct, {obj_percent}%\n\n")
        
percentage = round(100*score/total,2)
f.write(f"\n\nOverall Accuracy: {score}/{total} correct, {percentage}%")
print(f"\n\nOverall Accuracy: {score}/{total} correct, {percentage}%")

end_time = time.time()
proc_time = end_time - start_time
print(f"Test Proc Time: {proc_time:.4f} s\n")