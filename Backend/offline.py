import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog,
    QHBoxLayout, QGroupBox, QFormLayout, QMessageBox
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QThread, Signal,QFile, QTextStream
from Backend.model_manager import model_manager
from Backend.functions import Functions 

class ModelLoaderThread(QThread):
    models_loaded = Signal()

    def __init__(self):
        super().__init__()
        self.models_loaded_flag = False  # Flag indicating whether the models are loaded

    def run(self):
        if not self.models_loaded_flag:
            # Load the models only if they are not already loaded
            model_manager.load_models()

            # Update the flag to indicate that models are loaded
            self.models_loaded_flag = True

        # Notify that models are loaded
        self.models_loaded.emit()

class OfflineWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Load the style sheet
        style_file = QFile("assets/Style/style.qss")
        if style_file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(style_file)
            self.setStyleSheet(stream.readAll())
        else:
            print("Failed to open style file:", style_file.errorString())

        self.setWindowTitle("Offline Mode")
        self.setFixedSize(800, 500)
        icon_path = "assets/Icons/favicon-black.png"
        self.setWindowIcon(QIcon(icon_path))

        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

        layout = QVBoxLayout()

        upload_button = QPushButton("Upload Image")
        upload_button.clicked.connect(self.upload_image)
        upload_button.setFixedWidth(150)

        online_button = self.create_online_button()

        upload_layout = QHBoxLayout()
        upload_layout.addWidget(upload_button, alignment=Qt.AlignHCenter)
        upload_layout.addWidget(online_button, alignment=Qt.AlignHCenter)

        layout.addLayout(upload_layout)
        second_row_layout = QHBoxLayout()
        self.uploaded_image_label = QLabel()
        self.uploaded_image_label.setAlignment(Qt.AlignCenter)
        self.uploaded_image_label.setScaledContents(True)
        second_row_layout.addWidget(self.uploaded_image_label)

        self.preprocessed_image_label = QLabel()
        self.preprocessed_image_label.setAlignment(Qt.AlignCenter)
        self.preprocessed_image_label.setScaledContents(True)
        second_row_layout.addWidget(self.preprocessed_image_label)
        layout.addLayout(second_row_layout)

        third_row_layout = QHBoxLayout()

        self.predict_shape_button = QPushButton("Predict Shape")
        self.predict_gender_button = QPushButton("Predict Gender")
        self.predict_emotion_button = QPushButton("Predict Emotion")

        for button in [self.predict_shape_button, self.predict_gender_button, self.predict_emotion_button]:
            button.setFixedWidth(150)
            button.setEnabled(False)
            button.hide()

        prediction_buttons_layout = QVBoxLayout()
        prediction_buttons_layout.addWidget(self.predict_shape_button)
        prediction_buttons_layout.addWidget(self.predict_gender_button)
        prediction_buttons_layout.addWidget(self.predict_emotion_button)
        third_row_layout.addLayout(prediction_buttons_layout)

        # Connect the predict buttons to their respective methods
        self.predict_shape_button.clicked.connect(self.predict_shape)
        self.predict_gender_button.clicked.connect(self.predict_gender)
        self.predict_emotion_button.clicked.connect(self.predict_emotion)

        self.results_group_box = QGroupBox("Results")
        self.results_layout = QFormLayout()

        self.loading_label = QLabel("Loading...")
        self.results_layout.addRow("Status:", self.loading_label)

        # Create QLabel widgets for predictions
        self.shape_prediction_label = QLabel("Shape Prediction:")
        self.gender_prediction_label = QLabel("Gender Prediction:")
        self.emotion_prediction_label = QLabel("Emotion Prediction:")

        # Add the QLabel widgets to the layout and hide them initially
        self.results_layout.addRow(self.shape_prediction_label)
        self.results_layout.addRow(self.gender_prediction_label)
        self.results_layout.addRow(self.emotion_prediction_label)
        self.shape_prediction_label.hide()
        self.gender_prediction_label.hide()
        self.emotion_prediction_label.hide()

        self.results_group_box.setLayout(self.results_layout)
        self.results_group_box.hide()

        third_row_layout.addWidget(self.results_group_box)
        layout.addLayout(third_row_layout)

        self.model_loader_thread = ModelLoaderThread()
        self.model_loader_thread.models_loaded.connect(self.on_models_loaded)

        self.file_path = None  # Store the file path for prediction

        self.setLayout(layout)

    def upload_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.JPG)")
        if file_path:
            print(f"File Path: {file_path}")
            self.file_path = file_path

            pixmap = QPixmap(file_path)

            resized_uploaded_pixmap = pixmap.scaled(300, 400, Qt.KeepAspectRatio)
            self.uploaded_image_label.setPixmap(resized_uploaded_pixmap)

            result = Functions.preprocess("offline",file_path)

            if result is not None:
                processed_image_path, normalized_face = result

                processed_pixmap = QPixmap(processed_image_path)
                resized_processed_pixmap = processed_pixmap.scaled(300, 400, Qt.KeepAspectRatio)
                self.preprocessed_image_label.setPixmap(resized_processed_pixmap)

                # Clear existing predictions
                self.clear_predictions("Shape Prediction")
                self.clear_predictions("Gender Prediction")
                self.clear_predictions("Emotion Prediction")

                # Clear text of prediction labels
                self.shape_prediction_label.setText("Shape Prediction:")
                self.gender_prediction_label.setText("Gender Prediction:")
                self.emotion_prediction_label.setText("Emotion Prediction:")

                self.predict_shape_button.show()
                self.predict_gender_button.show()
                self.predict_emotion_button.show()
                self.results_group_box.show()

                if not self.model_loader_thread.models_loaded_flag:
                    # If models are not loaded, start the thread to load them
                    self.model_loader_thread.start()
                else:
                    # Models are already loaded, update the UI accordingly
                    self.on_models_loaded()

            else:
                self.preprocessed_image_label.setPixmap(QPixmap())
                self.predict_shape_button.hide()
                self.predict_gender_button.hide()
                self.predict_emotion_button.hide()
                self.results_group_box.hide()

                error_message = "Error processing the image. Please choose a valid image."
                QMessageBox.critical(self, "Error", error_message, QMessageBox.Ok)

    def on_models_loaded(self):
        self.loading_label.setText("Models are loaded!")
        for button in [self.predict_shape_button, self.predict_gender_button, self.predict_emotion_button]:
            button.setEnabled(True)
        self.results_group_box.show()

        # Show prediction labels when models are loaded
        self.shape_prediction_label.show()
        self.gender_prediction_label.show()
        self.emotion_prediction_label.show()

        QMessageBox.information(self, "Notification", "Models are loaded!", QMessageBox.Ok)

    def predict_shape(self):
        if model_manager.shape_model is not None:
            predicted_class, predictions = Functions.predict_shape("offline",self.file_path, model_manager.shape_model)
            # Display the prediction under the "Prediction" section in the results box
            self.display_prediction("Shape Prediction", predicted_class, predictions, self.shape_prediction_label)
        else:
            QMessageBox.warning(self, "Warning", "Shape model not loaded.", QMessageBox.Ok)

    def predict_gender(self):
        if model_manager.gender_model and model_manager.recognizer is not None:
            try:
                predicted_class, predictions = Functions.predict_gender("offline", self.file_path, model_manager.gender_model)
                labels = 'Models/labels-vgg.txt'
                recognized = Functions.recognizer("offline", self.file_path, model_manager.recognizer, labels)
                # Display the prediction under the "Prediction" section in the results box
                self.display_prediction("Gender Prediction", predicted_class + "     " + recognized, predictions, self.gender_prediction_label)
            except Exception as e:
                # Handle the exception and display a warning
                QMessageBox.warning(self, "Warning", f"Only Gender is detected , No recognition due to poor image quality ", QMessageBox.Ok)
                self.display_prediction("Gender Prediction", predicted_class , predictions, self.gender_prediction_label)
        else:
            QMessageBox.warning(self, "Warning", "Gender model not loaded.", QMessageBox.Ok)


    def predict_emotion(self):
        # Uncomment the following lines when the emotion model is available
        if model_manager.emotion_model is not None:
             predicted_class, predictions = Functions.predict_emotion("offline",self.file_path, model_manager.emotion_model)
             # Display the prediction under the "Prediction" section in the results box
             self.display_prediction("Emotion Prediction", predicted_class, predictions, self.emotion_prediction_label)
        else:
            QMessageBox.warning(self, "Warning", "Emotion model not loaded.", QMessageBox.Ok)

    def clear_predictions(self, title):
        # Clear existing predictions with the specified title
        for i in reversed(range(self.results_layout.rowCount())):
            item = self.results_layout.itemAt(i, QFormLayout.LabelRole)
            if item is not None and title in item.widget().text():
                self.results_layout.removeRow(i)

    def display_prediction(self, title, predicted_class, predictions, label_widget):
        # Update the QLabel widget with the prediction
        label_widget.setText(f"{title}:  {predicted_class}")
    
    def create_online_button(self):
        online_button = QPushButton("Switch Online")
        online_button.clicked.connect(self.switch_to_online_mode)
        online_button.setFixedWidth(150)
        return online_button

    def switch_to_online_mode(self):
        from Backend.online import OnlineWindow
        self.online_window = OnlineWindow()
        self.online_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    offline_window = OfflineWindow()
    offline_window.show()
    sys.exit(app.exec())
