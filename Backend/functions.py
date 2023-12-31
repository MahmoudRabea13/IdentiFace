import cv2
import tensorflow as tf
import numpy as np
import dlib
import matplotlib.pyplot as plt

class Functions():
    def preprocess(method,input_image, target_size=(128, 128)):
        "Function to preprocess the extracted faces"
        # Initialize the face detector and landmark predictor
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor("Utilities/Face-Detection/shape_predictor_68_face_landmarks.dat")
        
        if method == "offline":
            # Read the original image
            img = cv2.imread(input_image)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            img = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
            
        # Detect faces in the image
        faces = detector(img)

        # Process the first detected face
        if faces:
            face = faces[0]
            landmarks = predictor(img, face)

            # Draw a rectangle around the face
            cv2.rectangle(img, (face.left(), face.top()), (face.right(), face.bottom()), (0, 255, 0), 2)

            # Extract the face region
            extracted_face = img[face.top():face.bottom(), face.left():face.right()]

            # Check if the extracted face is not empty
            if not extracted_face.size:
                return None

            # Resize the face to the target size
            resized_face = cv2.resize(extracted_face, target_size)
            path = 'test.jpg'
            # Save the resized face as 'test.jpg'
            cv2.imwrite(path, resized_face)

            # Normalize the pixel values to the range [0, 1]
            normalized_face = resized_face / 255.0

            # Expand the dimensions to match the input shape expected by the model
            normalized_face = np.expand_dims(normalized_face, axis=0)

            return path,normalized_face

        # If no faces are found, return None
        return None

    def predict_shape(method,image_path, model):
        "Shape prediciton Function"
        if method == "offline":
            # Read the original image
            original_image = cv2.imread(image_path)
        else:
            pass
        # Preprocess the image
        path,preprocessed_image = Functions.preprocess(method,image_path)

        # Make predictions using the loaded model
        predictions = model.predict(preprocessed_image)

        # Determine the predicted class based on the threshold
        predicted_class_index = np.argmax(predictions)
        predicted_class = None

        if predicted_class_index == 0:
            predicted_class = 'Oblong'
        elif predicted_class_index == 1:
            predicted_class = 'Square'
        elif predicted_class_index == 2:
            predicted_class = 'Round'
        elif predicted_class_index == 3:
            predicted_class = 'Heart'
        elif predicted_class_index == 4:
            predicted_class = 'Oval'
        # Return the predictions
        print(predictions)
        return predicted_class,predictions
    
    
    def predict_gender(method,image_path,model ):
        "Gender Classification Function"
        if method == "offline":
            # Read the original image
            original_image = cv2.imread(image_path)
        else:
            pass
        # Preprocess the image
        path,preprocessed_image = Functions.preprocess(method,image_path,target_size=(48,48))

        # Make predictions using the loaded model
        predictions = model.predict(preprocessed_image)

        # Get the index of the highest element in the predictions array
        predicted_index = np.argmax(predictions)

        # Determine the predicted class based on the index
        predicted_class = 'Male' if predicted_index == 1 else 'Female'
        # Return the predictions
        print(predictions)
        return predicted_class,predictions 
    

    def predict_emotion(method, image_path, model):
        "Emotion Recognition Function"
        if method == "offline":
            # Read the original image
            original_image = cv2.imread(image_path)
        else:
            pass

        # Preprocess the image
        path, preprocessed_image = Functions.preprocess(method, image_path, target_size=(48, 48))

        # Make predictions using the loaded model
        predictions = model.predict(preprocessed_image)

        # Get the indices of the top two predicted classes
        top_classes_indices = np.argsort(predictions)[0, -2:][::-1]

        # Get the corresponding class labels
        top_classes_labels = ['neutral', 'happy', 'angry', 'surprise','sad']  # Update with your actual class labels

        # Determine the predicted classes and their respective percentages
        top1_class_index = top_classes_indices[0]
        top1_class_label = top_classes_labels[top1_class_index]
        top1_class_percentage = predictions[0, top1_class_index] * 100

        top2_class_index = top_classes_indices[1]
        top2_class_label = top_classes_labels[top2_class_index]
        top2_class_percentage = predictions[0, top2_class_index] * 100

        # Store the result in the predicted_class string
        predicted_class = f"{top1_class_label}: {top1_class_percentage:.2f}% | {top2_class_label}: {top2_class_percentage:.2f}%"
        print(predictions)
        # Return the predictions along with the stored result in predicted_class
        return predicted_class, predictions

    def face_detection(image):
        "Facial Extraction function"
        # Initialize the face detector and landmark predictor
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor("Utilities/shape_predictor_68_face_landmarks.dat")
    
        # Read the original image
        img = cv2.imread(image)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Detect faces in the image
        faces = detector(img)

        # Process the first detected face
        if faces:
            face = faces[0]
            landmarks = predictor(img, face)

            # Draw a rectangle around the face
            cv2.rectangle(img, (face.left(), face.top()), (face.right(), face.bottom()), (0, 255, 0), 2)

            # Extract the face region
            extracted_face = img[face.top():face.bottom(), face.left():face.right()]

            # Check if the extracted face is not empty
            if not extracted_face.size:
                return None

            # Resize the face to the target size
            resized_face = cv2.resize(extracted_face, (128,128))
            path = 'test.jpg'
            # Save the resized face as 'test.jpg'
            cv2.imwrite(path, resized_face)
        return resized_face

    def face_recognizer(image):
        "Facial Extraction function for the recognition task only"
        image = cv2.resize(image, (128,128))
        dnnFaceDetector = dlib.cnn_face_detection_model_v1("Utilities/Face-Detection/mmod_human_face_detector.dat")
        rects = dnnFaceDetector(image, 1)
        cropped_face=[]
        for (i, rect) in enumerate(rects):
            x1 = rect.rect.left()
            y1 = rect.rect.top()
            x2 = rect.rect.right()
            y2 = rect.rect.bottom()
            cropped_face = image[y1:y2, x1:x2]
        return cropped_face

    def recognizer(method,path, model, labels_path):
        "Recognition Function"
        # Read the labels' text file content
        with open(labels_path, 'r') as file:
            content = file.read()
        content = content.strip('[]')
        elements = content.split() 
        labels_list = [element.strip("'") for element in elements] 
        if method == "offline":
            img = cv2.imread(path,0)
            cropped = np.array(Functions.face_recognizer(img))
        else:
            cropped = np.array(Functions.face_recognizer(path))
      
        resized = cv2.resize(cropped,(128,128))
        input_img = np.expand_dims(resized, axis=-1).astype('float32') / 255.0
        input_img = np.expand_dims(input_img, axis=0)
        predictions = model.predict(input_img)
        class_index = np.argmax(predictions)
        predicted_subject = labels_list[class_index]
        print(predictions)
        return predicted_subject


    
