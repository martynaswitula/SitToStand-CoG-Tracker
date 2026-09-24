import sys
import cv2
import numpy as np
import csv
import pandas as pd
from PyQt5 import QtWidgets, QtGui, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl

from pose_extractor import PoseExtractor
from cogs import compute_frame_cog

#### ANALIZA PRZEBIEGU PRÓBY ####
def detect_transition(trial, fps=30):
    if len(trial) < 30:
        return (None, None)

    y_values = np.array([y for _, y in trial])
    
    # Okno porównania (1 sekunda)
    window_size = int(1.0 * fps)
    max_drop = 0
    start, end = None, None

    for i in range(len(y_values) - window_size):
        y1 = np.mean(y_values[i:i+window_size//2])
        y2 = np.mean(y_values[i+window_size//2:i+window_size])
        diff = y2 - y1
        if diff > max_drop:  # Szukamy największego wzrostu (bo odwrócony Y)
            max_drop = diff
            start = i
            end = i + window_size

    if start is not None and end is not None:
        return (start, end)
    else:
        return (None, None)

#### PANEL Z CHECKBOXAMI ####
class VisualOptionsMenu(QtWidgets.QGroupBox):
    def __init__(self):
        super().__init__("☰ Opcje wizualizacji")
        self.setStyleSheet("QGroupBox { font-weight: bold; color: black; }")

        self.checkbox_cog = QtWidgets.QCheckBox("Środek masy")
        self.checkbox_landmarks = QtWidgets.QCheckBox("Punkty ciała")
        
        for cb in (self.checkbox_cog, self.checkbox_landmarks):
            cb.setStyleSheet("color: black;")

        # układ checkboxów
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.checkbox_cog)
        layout.addWidget(self.checkbox_landmarks)
        
        layout.addStretch()
        self.setLayout(layout)

    # zwraca zaznaczone checkboxy
    def get_options(self):
        return {
            "cog": self.checkbox_cog.isChecked(),
            "landmarks": self.checkbox_landmarks.isChecked(),
            
        }


class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(facecolor="#e3f2fd")
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        
        self.current_trial = []
        self.all_trials = []
        self.reference_y_values = []

    #### NOWA WARTOŚĆ Y DO AKTUALNEJ PRÓBY ####
    def update_plot(self, y):
        x = self.current_trial[-1][0] + 1 if self.current_trial else 0
        self.current_trial.append((x, y))

    #### ZAPISUJE AKTUALNĄ PRÓBĘ/RYSUJE WYKRES ####
    def finalize_trial(self):
        if not self.current_trial:
            return
        transition = detect_transition(self.current_trial)
        if transition == (None, None):
            print("Nie wykryto przejścia. Pomijam próbę.")
            return
        transition_start, transition_end = transition
        transition_mid = (transition_start + transition_end) // 2
        shift = -transition_mid
        adjusted_trial = [(x + shift, y) for x, y in self.current_trial]
        if not self.reference_y_values:
            self.reference_y_values = [y for x, y in adjusted_trial if x >= 0]
        elif len([y for x, y in adjusted_trial if x >= 0]) > 0:
            target = np.mean(self.reference_y_values)
            current = np.mean([y for x, y in adjusted_trial if x >= 0])
            offset = current - target
            adjusted_trial = [(x, y - offset) for x, y in adjusted_trial]
        self.all_trials.append(adjusted_trial)
        self.current_trial = []
        self.plot_trials()

    #### RYSUJE WSZYSTKIE PRÓBY NA WYKRESIE ####
    def plot_trials(self):
        self.ax.clear()
        self.fig.patch.set_facecolor('none')
        self.ax.set_facecolor('#e3f2fd')
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                  '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
                  '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5',
                  '#c49c94', '#f7b6d2', '#c7c7c7', '#dbdb8d', '#9edae5']
        for i, trial in enumerate(self.all_trials):
            color = colors[i % len(colors)]
            xs = [x for x, _ in trial]
            ys = [y for _, y in trial]
            transition = detect_transition(trial)
            if transition == (None, None):
                self.ax.plot(xs, ys, label=f'Trial {i+1}', color=color)
                continue
            transition_start, transition_end = transition
            sitting = trial[:transition_start]
            transition_segment = trial[transition_start:transition_end]
            standing = trial[transition_end:]
            self.ax.plot(xs, ys, linestyle='-', color=color, label=f'Trial {i+1}')
            #jeśli chcemy rysować widoczne fazy np. różnymi kolorami siedzenie i wstawanie zakomentowac linijke wyzej i odkomentowac te poniżej

            # if sitting:
            #     self.ax.plot([x for x, _ in sitting], [y for _, y in sitting], linestyle='-', color=color)
            # if transition_segment:
            #     self.ax.plot([x for x, _ in transition_segment], [y for _, y in transition_segment], linestyle='-', color=color)
            # if standing:
            #     self.ax.plot([x for x, _ in standing], [y for _, y in standing], linestyle='-', color=color)
        if self.current_trial:
            trial = self.current_trial
            transition = detect_transition(trial)
            if transition != (None, None):
                transition_start, transition_end = transition
                shift = -(transition_start + transition_end) // 2
                trial = [(x + shift, y) for x, y in trial]
            xs = [x for x, _ in trial]
            ys = [y for _, y in trial]
            self.ax.plot(xs, ys, color='gray', alpha=0.5)
        if self.reference_y_values:
            mean_y = np.mean(self.reference_y_values)
        if self.reference_y_values and trial:
            transition = detect_transition(trial)
            if transition != (None, None):
                transition_start, transition_end = transition
                transition_mid = (transition_start + transition_end) // 2
                x_transition = trial[transition_mid][0]
                self.ax.axvline(x_transition, color='black', linestyle='--', alpha=0.8)
        self.ax.set_title("CoG Y Coordinate", color='black')
        self.ax.set_xlabel("Frame", color='black')
        self.ax.set_ylabel("Y Position (pixels)", color='black')
        self.ax.tick_params(colors='black')
        self.fig.subplots_adjust(left=0.15, right=0.98, top=0.95, bottom=0.1)
        if self.ax.get_legend_handles_labels()[0]:
            self.ax.legend(loc='lower right', fontsize=9, frameon=True)
        self.draw()

    #### CZYŚCI WSZYSTKIE DANE ####
    def reset_plot(self):
        self.current_trial = []
        self.all_trials = []
        self.reference_y_values = []
        self.ax.clear()
        self.ax.set_title("CoG Y Coordinate", color='white')
        self.ax.set_xlabel("Frame", color='white')
        self.ax.set_ylabel("Y position", color='white')
        self.ax.tick_params(colors='white')
        self.draw()

    #### ZAPISUJE WYKRES DO JPG ####
    def save_plot_as_jpg(self, filename):
        self.fig.savefig(filename, format='jpg')
        print(f"Wykres zapisany jako JPG: {filename}")

    #### TWORZY CSV ####
    def save_plot_data_as_csv(self, filename):
        if not self.all_trials:
            print("Brak prób do zapisania.")
            return

        all_columns = []
        max_rows = 0

        for idx, trial in enumerate(self.all_trials):
            frames = [x for x, _ in trial]
            y_values = [y for _, y in trial]

            # Normalizacja do 100 próbek
            resampled_y = np.interp(
                np.linspace(0, len(y_values) - 1, 100),
                np.arange(len(y_values)),
                y_values
            )
            y_min = np.min(resampled_y)
            y_max = np.max(resampled_y)
            normalized_y = (resampled_y - y_min) / (y_max - y_min)

            # Zapisz kolumny dla tej próby
            col_frame = frames + [""] * (max(len(frames), 100) - len(frames))
            col_y = y_values + [""] * (max(len(y_values), 100) - len(y_values))
            col_norm = list(np.round(normalized_y, 6)) + [""] * (max(len(y_values), 100) - 100)

            max_rows = max(max_rows, len(col_frame))

            all_columns.append((
                f"Frame_Trial{idx+1}",
                f"YPosition_Trial{idx+1}",
                f"Normalized_Trial{idx+1}",
                col_frame,
                col_y,
                col_norm
            ))

        # Zapisz do pliku
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file, delimiter=';')

            # Nagłówki
            header = []
            for col in all_columns:
                header.extend(col[:3])
            writer.writerow(header)

            # Wiersze danych
            for i in range(max_rows):
                row = []
                for col in all_columns:
                    row.append(col[3][i] if i < len(col[3]) else "")
                    row.append(col[4][i] if i < len(col[4]) else "")
                    row.append(col[5][i] if i < len(col[5]) else "")
                writer.writerow(row)

        print(f"Dane wszystkich prób zapisane jako CSV: {filename}")
    
    #### RYSUJE TYLKO OSTATNIĄ PRÓBĘ ####
    def plot_only_last_trial(self):
        self.ax.clear()
        self.fig.patch.set_facecolor('none')
        self.ax.set_facecolor('#e3f2fd')

        trial = self.all_trials[-1]
        xs = [x for x, _ in trial]
        ys = [y for _, y in trial]

        self.ax.plot(xs, ys, linestyle='-', color='#1f77b4', label=f'Trial {len(self.all_trials)}')

        transition = detect_transition(trial)
        if transition != (None, None):
            transition_start, transition_end = transition
            transition_mid = (transition_start + transition_end) // 2
            x_transition = trial[transition_mid][0]
            self.ax.axvline(x_transition, color='black', linestyle='--', alpha=0.8)

        self.ax.set_title("CoG Y Coordinate (last trial)", color='black')
        self.ax.set_xlabel("Frame", color='black')
        self.ax.set_ylabel("Y Position (pixels)", color='black')
        self.ax.tick_params(colors='black')
        self.fig.subplots_adjust(left=0.05, right=0.98, top=0.95, bottom=0.1)
        if self.ax.get_legend_handles_labels()[0]:
            self.ax.legend(loc='lower right', fontsize=9, frameon=True)
        self.draw()



class AppGUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pose Capture & CoG Tracker")
        self.resize(1600, 900)

        self.beep_player = QMediaPlayer()
        self.beep_url = QUrl.fromLocalFile("beep.wav")
        self.last_beep_time = QtCore.QTime()
        
        self.setStyleSheet("""
            QWidget {
                background-color: #e3f2fd;
                font-family: Segoe UI, Arial;
                font-size: 14px;
            }
            QPushButton {
                background-color: #90caf9;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 12px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #42a5f5;
            }
            QLabel {
                font-size: 16px;
            }
        """)
        self.frame_counter = 0

        self.capture = None
        self.current_camera_index = 0
        self.timer = QtCore.QTimer()
        self.extractor = PoseExtractor()
        self.is_recording = False
        self.cog_path = []

        self.phase_timer = QtCore.QTimer()
        self.phase_timer.timeout.connect(self.update_phase)
        self.phase_stage = 0
        self.phase_seconds = 0
        self.in_calibration = True

        self.image_label = QtWidgets.QLabel(self)
        self.image_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)

        self.plot_canvas = PlotCanvas(self)
        self.visual_options = VisualOptionsMenu()
        #self.plot_canvas.setMinimumWidth(600)  
        #self.plot_canvas.setMaximumWidth(800)  #ogranicz maksymalnie
        self.plot_canvas.setMinimumWidth(800)
        self.plot_canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.image_label.setMaximumHeight(700)

        self.start_btn = QtWidgets.QPushButton("Start")
        self.reset_btn = QtWidgets.QPushButton("Reset")
        self.show_last_btn = QtWidgets.QPushButton("Wyświetl ostatni")
        self.save_jpg_btn = QtWidgets.QPushButton("Zapisz JPG")
        self.save_csv_btn = QtWidgets.QPushButton("Zapisz CSV")
        self.select_cam_btn = QtWidgets.QPushButton("Kamera")

        self.phase_label = QtWidgets.QLabel("Etap: -", self)
        self.timer_display = QtWidgets.QLabel("00", self)
        self.timer_display.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.phase_label.setAlignment(QtCore.Qt.AlignCenter)
        self.timer_display.setAlignment(QtCore.Qt.AlignCenter)

        self.start_btn.clicked.connect(self.start)
        self.show_last_btn.clicked.connect(self.show_last_trial)
        self.reset_btn.clicked.connect(self.reset)
        self.save_jpg_btn.clicked.connect(self.save_jpg)
        self.save_csv_btn.clicked.connect(self.save_csv)
        self.select_cam_btn.clicked.connect(self.select_camera)

        options_layout = QtWidgets.QHBoxLayout()
        options_layout.addWidget(self.visual_options)
        options_layout.addStretch()

        video_with_options_layout = QtWidgets.QVBoxLayout()
        video_with_options_layout.addWidget(self.image_label)

        # Ramka z opcjami wizualizacji – ograniczona wysokość
        options_container = QtWidgets.QWidget()
        options_container.setLayout(options_layout)
        options_container.setMaximumHeight(85) 

        video_with_options_layout.addWidget(options_container)

        video_layout = QtWidgets.QHBoxLayout()
        video_layout.addLayout(video_with_options_layout, stretch=6)
        video_with_options_layout.setContentsMargins(200, 0, 0, 0)

        plot_canvas_layout = QtWidgets.QVBoxLayout()
        plot_canvas_layout.addWidget(self.plot_canvas)
        plot_canvas_layout.setContentsMargins(0, 0, 0, 100)

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(self.plot_canvas, stretch=4)
        top_layout.addLayout(video_layout, stretch=6)
        top_layout.setContentsMargins(60, 0, 25, 20)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addWidget(self.show_last_btn)
        btn_layout.addWidget(self.save_jpg_btn)
        btn_layout.addWidget(self.save_csv_btn)
        btn_layout.addWidget(self.select_cam_btn)

        info_layout = QtWidgets.QVBoxLayout()
        info_layout.addWidget(self.phase_label)
        info_layout.addWidget(self.timer_display)
        btn_layout.addLayout(info_layout)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        self.timer.timeout.connect(self.update_frame)
        QtCore.QTimer.singleShot(100, self.select_camera)

    #### START NAGRYWANIE I ODLICZANIE ####
    def start(self):
        if self.phase_timer.isActive():
            return
        self.is_recording = True
        self.phase_stage = 0
        self.in_calibration = len(self.plot_canvas.all_trials) == 0
        self.phase_seconds = 10
        self.phase_timer.start(1000)
        if self.capture and not self.timer.isActive():
            self.timer.start(10)
        self.update_phase_label()

    #### RESET DANYCH/CZYŚCI GUI ####
    def reset(self):
        self.extractor.reset()
        self.plot_canvas.reset_plot()
        self.image_label.clear()
        self.cog_path.clear()
        self.is_recording = False
        self.phase_timer.stop()
        self.timer_display.setText("00")
        self.phase_label.setText("Etap: -")
        self.phase_stage = 0
        self.phase_seconds = 0
        self.in_calibration = True

    #### OSTATNIA PRÓBA NA WYKRESIE ####
    def show_last_trial(self):
        if not self.plot_canvas.all_trials:
            QtWidgets.QMessageBox.information(self, "Brak danych", "Brak zapisanych prób.")
            return
        self.plot_canvas.plot_only_last_trial()

    #### ODLICZANIE CZASU FAZY ####
    def update_phase(self):
        self.timer_display.setText(str(self.phase_seconds))
        if self.phase_seconds in [3, 2, 1]:
            self.play_beep()
        self.phase_seconds -= 1
        if self.phase_seconds < 0:
            self.phase_stage += 1
            if self.in_calibration:
                if self.phase_stage == 1:
                    self.phase_seconds = 10
                elif self.phase_stage == 2:
                    self.phase_timer.stop()
                    self.phase_label.setText("Kalibracja zakończona")
                    self.is_recording = False
                    if self.plot_canvas.current_trial:
                        self.plot_canvas.finalize_trial()
                    self.plot_canvas.plot_trials()
            else:
                if self.phase_stage == 1:
                    self.phase_seconds = 10
                elif self.phase_stage == 2:
                    self.phase_timer.stop()
                    self.phase_label.setText("Próba zakończona")
                    self.is_recording = False
                    if self.plot_canvas.current_trial:
                        self.plot_canvas.finalize_trial()
                    self.plot_canvas.plot_trials()
            self.update_phase_label()

    #### AKTUALIZACJA ETAPU SIEDZ/STAN ####
    def update_phase_label(self):
        if self.in_calibration:
            self.phase_label.setText("Próba 1: Siedź" if self.phase_stage == 0 else "Próba 1: Stań")
        else:
            self.phase_label.setText("Próba: Siedź" if self.phase_stage == 0 else "Próba: Stań")

    #### AKTUALIZACJA ETAPU SIEDZ/STAN ####
    def save_jpg(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Zapisz wykres jako JPG", "", "JPG files (*.jpg)")
        if filename:
            self.plot_canvas.save_plot_as_jpg(filename)

    #### ZAPISYWANIE CSV ####
    def save_csv(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Zapisz dane jako CSV", "", "CSV files (*.csv)")
        if filename:
            self.plot_canvas.save_plot_data_as_csv(filename)

    #### POBIERA KLATKI WYZNACZA ŚRODEK COG ####
    def update_frame(self):
        self.frame_counter += 1
        if not self.capture:
            return
        ret, frame = self.capture.read()
        if not ret:
            return

        landmarks = self.extractor.extract(frame)
        options = self.visual_options.get_options()

        if landmarks:
            try:
                row_data = {}
                for i, landmark in enumerate(self.extractor.mp_pose.PoseLandmark):
                    name = landmark.name
                    row_data[f"{name}_x"] = landmarks[i]["x"]
                    row_data[f"{name}_y"] = landmarks[i]["y"]
                row = pd.Series(row_data)
                cog_x, cog_y = compute_frame_cog(row, frame.shape[1], frame.shape[0])
                cog_y = -cog_y
                if self.is_recording:
                    self.plot_canvas.update_plot(cog_y)
                    self.plot_canvas.plot_trials()
                self.cog_path.append((int(cog_x), int(cog_y)))
                if len(self.cog_path) > 1000:
                    self.cog_path = self.cog_path[-1000:]

                if options["cog"]:
                    cv2.circle(frame, (int(cog_x), int(cog_y)), 8, (0, 255, 0), -1)
                if options["landmarks"]:
                    for lm in landmarks:
                        x = int(lm["x"] * frame.shape[1])
                        y = int(lm["y"] * frame.shape[0])
                        cv2.circle(frame, (x, y), 3, (255, 0, 0), -1)
                

            except Exception as e:
                print("Błąd przy obliczaniu CoG:", e)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        qt_image = QtGui.QImage(rgb_frame.data, w, h, ch * w, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qt_image).scaled(self.image_label.size(), QtCore.Qt.KeepAspectRatio)
        self.image_label.setPixmap(pixmap)

    #### WYBÓR KAMERY ####
    def select_camera(self):
        available_cams = []
        for i in range(10):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                available_cams.append(i)
                cap.release()
        if not available_cams:
            QtWidgets.QMessageBox.critical(self, "Błąd", "Nie znaleziono żadnych kamer.")
            return
        items = [f"Kamera {i}" for i in available_cams]
        item, ok = QtWidgets.QInputDialog.getItem(self, "Wybierz kamerę", "Dostępne kamery:", items, 0, False)
        if ok and item:
            cam_index = int(item.split()[-1])
            self.current_camera_index = cam_index
            if self.capture:
                self.capture.release()
            self.capture = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
            if not self.capture.isOpened():
                QtWidgets.QMessageBox.critical(self, "Błąd", f"Nie udało się otworzyć kamery {cam_index}")
                self.capture = None
            else:
                self.timer.start(10)
    
    #### ODTWARZA BEEP ####
    def play_beep(self):
        # Odtwarzaj tylko jeśli od ostatniego piku minęło > 900ms
        now = QtCore.QTime.currentTime()
        if not self.last_beep_time.isValid() or self.last_beep_time.msecsTo(now) > 900:
            self.beep_player.setMedia(QMediaContent(self.beep_url))
            self.beep_player.setVolume(100)  # zmień głośność
            self.beep_player.play()
            self.last_beep_time = now

    #### ZWALNIA KAMERY I TIMER ####
    def closeEvent(self, event):
        if self.capture:
            self.capture.release()
        self.timer.stop()
        self.phase_timer.stop()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    gui = AppGUI()
    gui.showMaximized()
    sys.exit(app.exec_())