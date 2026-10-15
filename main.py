import os, sys, csv, time
os.environ.setdefault("QT_API", "pyside6")
import numpy as np
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QDoubleSpinBox,
                               QSlider, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QGroupBox,
                               QFormLayout, QCheckBox, QFileDialog, QTabWidget, QHeaderView)
from pyvistaqt import QtInteractor
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure
import na_physics as phys
from scene3d import ApparatusScene


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Numerical Aperture of Optical Fiber - Virtual Lab")
        self.resize(1550, 920)
        self.obs, self.tracker, self.prev = [], None, None
        self.fist_t, self.last_rec, self.L_smooth = None, 0.0, 8.0

        self.plotter = QtInteractor(self)
        self.scene = ApparatusScene(self.plotter)

        # ---- controls
        self.n1 = self._spin(1.00, 2.00, 1.49, 0.01)
        self.n2 = self._spin(1.00, 2.00, 1.41, 0.01)
        self.laser = QCheckBox("Laser ON"); self.laser.setChecked(True)
        self.slider = QSlider(Qt.Horizontal); self.slider.setRange(20, 150); self.slider.setValue(80)
        self.dist_lbl = QLabel()
        self.d_spin = self._spin(0.0, 40.0, 0.0, 0.1)
        self.live = QLabel()
        box = QGroupBox("Fiber & measurement"); f = QFormLayout(box)
        f.addRow("Core index n1", self.n1); f.addRow("Cladding index n2", self.n2)
        f.addRow(self.laser); f.addRow("Distance L (cm)", self.slider); f.addRow(self.dist_lbl)
        f.addRow("Measured spot dia. d (cm)", self.d_spin); f.addRow(self.live)

        btns = QHBoxLayout()
        for text, fn in (("Record", self.record), ("Delete last", self.delete_last),
                         ("Clear", self.clear), ("Export CSV", self.export)):
            b = QPushButton(text); b.clicked.connect(fn); btns.addWidget(b)

        self.cam_btn = QPushButton("Start hand-gesture control"); self.cam_btn.clicked.connect(self.toggle_cam)
        self.cam_view = QLabel("Camera off"); self.cam_view.setFixedSize(320, 240)
        self.cam_view.setAlignment(Qt.AlignCenter); self.cam_view.setStyleSheet("background:#111;color:#aaa")
        self.gesture_lbl = QLabel("Gestures: point = rotate | open palm (thumb-index spread) = distance | fist 1s = record")
        self.gesture_lbl.setWordWrap(True)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["No.", "L (cm)", "d (cm)", "r (cm)", "NA", "theta (deg)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.summary = QLabel("No readings yet."); self.summary.setWordWrap(True)
        self.fig = Figure(figsize=(6, 3)); self.canvas = Canvas(self.fig)
        tab_data = QWidget(); v = QVBoxLayout(tab_data); v.addWidget(self.table); v.addWidget(self.summary)
        tabs = QTabWidget(); tabs.addTab(tab_data, "Observations"); tabs.addTab(self.canvas, "Graphs")

        right = QWidget(); right.setFixedWidth(480); rv = QVBoxLayout(right)
        for w in (box,): rv.addWidget(w)
        rv.addLayout(btns); rv.addWidget(self.cam_btn); rv.addWidget(self.cam_view, 0, Qt.AlignCenter)
        rv.addWidget(self.gesture_lbl); rv.addWidget(tabs, 1)
        central = QWidget(); h = QHBoxLayout(central); h.addWidget(self.plotter.interactor, 1); h.addWidget(right)
        self.setCentralWidget(central)

        self.n1.valueChanged.connect(self.on_indices); self.n2.valueChanged.connect(self.on_indices)
        self.laser.toggled.connect(self.scene.set_laser)
        self.slider.valueChanged.connect(self.on_distance)
        self.on_indices(); self.on_distance(self.slider.value())
        self.timer = QTimer(self); self.timer.timeout.connect(self.scene.animate); self.timer.start(33)

    @staticmethod
    def _spin(lo, hi, val, step):
        s = QDoubleSpinBox(); s.setRange(lo, hi); s.setValue(val); s.setSingleStep(step); s.setDecimals(2)
        return s

    def theory_na(self):
        return phys.na_from_indices(self.n1.value(), self.n2.value())

    def on_indices(self):
        self.scene.set_na(self.theory_na()); self.on_distance(self.slider.value())

    def on_distance(self, v):
        L = v / 10.0
        self.scene.set_distance(L)
        self.dist_lbl.setText(f"L = {L:.1f} cm")
        self.d_spin.setValue(round(phys.spot_diameter(self.theory_na(), L), 1))  # ruler resolution 0.1 cm
        self.live.setText(f"Theoretical NA = {self.theory_na():.3f}")

    # ---- data
    def record(self):
        self.obs.append((self.slider.value() / 10.0, self.d_spin.value())); self.refresh()

    def delete_last(self):
        if self.obs: self.obs.pop(); self.refresh()

    def clear(self):
        self.obs.clear(); self.refresh()

    def export(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "na_readings.csv", "CSV (*.csv)")
        if path:
            with open(path, "w", newline="") as fh:
                w = csv.writer(fh); w.writerow(["L_cm", "d_cm", "r_cm", "NA", "theta_deg"])
                for L, d in self.obs:
                    na = phys.na_from_spot(d, L); w.writerow([L, d, d / 2, f"{na:.4f}", f"{phys.half_angle_deg(na):.2f}"])

    def refresh(self):
        self.table.setRowCount(len(self.obs))
        nas = []
        for i, (L, d) in enumerate(self.obs):
            na = phys.na_from_spot(d, L); nas.append(na)
            for j, val in enumerate([i + 1, f"{L:.1f}", f"{d:.2f}", f"{d / 2:.2f}", f"{na:.4f}",
                                     f"{phys.half_angle_deg(na):.2f}"]):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))
        self.fig.clear(); a1 = self.fig.add_subplot(121); a2 = self.fig.add_subplot(122)
        a1.set_xlabel("L (cm)"); a1.set_ylabel("r = d/2 (cm)"); a1.set_title("r vs L"); a2.set_title("NA per reading")
        a2.set_xlabel("Reading no."); a2.set_ylabel("NA")
        if not self.obs:
            self.summary.setText("No readings yet."); self.fig.tight_layout(); self.canvas.draw(); return
        Ls = np.array([o[0] for o in self.obs]); rs = np.array([o[1] for o in self.obs]) / 2
        a1.scatter(Ls, rs, color="red")
        a2.bar(range(1, len(nas) + 1), nas, color="tab:blue"); a2.axhline(self.theory_na(), color="k", ls="--")
        txt = f"Mean NA = {np.mean(nas):.4f}\nMean theta = {phys.half_angle_deg(np.mean(nas)):.2f} deg\n" \
              f"Acceptance angle 2*theta = {2 * phys.half_angle_deg(np.mean(nas)):.2f} deg\n"
        if len(self.obs) >= 2 and len(set(Ls)) > 1:
            k, c = np.polyfit(Ls, rs, 1); xs = np.linspace(0, Ls.max() * 1.05, 20)
            a1.plot(xs, k * xs + c, "b-"); txt += f"NA from graph slope = {phys.fit_na(Ls, 2 * rs):.4f}\n"
        err = abs(np.mean(nas) - self.theory_na()) / self.theory_na() * 100
        txt += f"Theoretical NA (n1,n2) = {self.theory_na():.4f}  (error {err:.1f}%)"
        self.summary.setText(txt); self.fig.tight_layout(); self.canvas.draw()

    # ---- gestures
    def toggle_cam(self):
        if self.tracker:
            self.tracker.stop(); self.tracker = None
            self.cam_btn.setText("Start hand-gesture control"); self.cam_view.setText("Camera off"); return
        from hand_tracking import HandTracker
        self.tracker = HandTracker()
        self.tracker.frame_ready.connect(lambda img: self.cam_view.setPixmap(QPixmap.fromImage(img)))
        self.tracker.gesture.connect(self.on_gesture)
        self.tracker.error.connect(lambda m: self.cam_view.setText(m))
        self.tracker.start(); self.cam_btn.setText("Stop hand-gesture control")

    def on_gesture(self, g, x, y, s):
        now = time.monotonic()
        if g != "point": self.prev = None
        if g != "fist": self.fist_t = None
        if g == "point":
            if self.prev:
                cam = self.plotter.camera
                cam.Azimuth(-(x - self.prev[0]) * 200); cam.Elevation((y - self.prev[1]) * 150)
                cam.OrthogonalizeViewUp(); self.plotter.render()
            self.prev = (x, y)
        elif g == "open":
            target = float(np.interp(s, [0.3, 1.3], [2, 15]))
            self.L_smooth += 0.2 * (target - self.L_smooth); self.slider.setValue(int(self.L_smooth * 10))
        elif g == "fist":
            if self.fist_t is None: self.fist_t = now
            elif now - self.fist_t > 1.2 and now - self.last_rec > 2.0:
                self.record(); self.last_rec, self.fist_t = now, None

    def closeEvent(self, e):
        self.timer.stop()
        if self.tracker: self.tracker.stop()
        self.plotter.close(); super().closeEvent(e)


if __name__ == "__main__":
    app = QApplication(sys.argv); w = Main(); w.show(); sys.exit(app.exec())
