from keras.models import load_model

class ModelManager:
    def __init__(self):
        self.gender_model = None
        self.shape_model = None
        self.emotion_model = None
        self.recognizer = None

    def load_models(self):
        if self.gender_model is None:
            self.gender_model = load_model('Models/gender.h5')
        if self.recognizer is None:
            self.recognizer = load_model('Models/recognizer.h5')
        if self.shape_model is None:
            self.shape_model = load_model('Models/shape.h5')
        if self.emotion_model is None:
            self.emotion_model = load_model('Models/emotion.h5')

# Create a global instance of ModelManager
model_manager = ModelManager()
