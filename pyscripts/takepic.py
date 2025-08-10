import cv2
import os

video_capture = cv2.VideoCapture(0)
if not video_capture.isOpened():
    print("Error: Could not open camera.")
else:
    while True:
        # Read a frame
        ret, frame = video_capture.read()

        # If frame is not read successfully, break the loop
        if not ret:
            break

        # Display the frame
        cv2.imshow('Live View', frame)

        # save image on 's' press
        if cv2.waitKey(1) & 0xFF == ord('s'):
            folder_name = input("Please enter object name: ")
            folder_path = os.path.join('dataset',folder_name)
            # check if object has been created before and append number if images already exist
            if os.path.isdir(folder_path):
                folder_files = sorted(os.listdir(folder_path), key=lambda file: os.path.getctime(os.path.join(folder_path, file)))
                last_file = folder_files[-1]
                last_file = last_file.split('.')
                last_file = last_file[0].split('_')
                new_num = int(last_file[1]) + 1
                filename = os.path.join(folder_path,f'{folder_name}_{new_num}.png')
            else:
                os.mkdir(folder_path)
                filename = os.path.join(folder_path,f'{folder_name}_1.png')
                print(filename)
            cv2.imwrite(filename, frame)
            print('\nSaved!\n')

        elif cv2.waitKey(1) & 0xFF == ord('t'):
            folder_name = input("Please enter object name: ")
            # check if object has been created before and append number if images already exist
            filename = os.path.join('test_images',f'{folder_name}_test.png')
            cv2.imwrite(filename, frame)
            print('\nSaved!\n')

        # Break the loop on 'q' key press
        elif cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()