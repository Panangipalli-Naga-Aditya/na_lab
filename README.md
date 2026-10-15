# Virtual Numerical Aperture Lab (Python)
Install Python 3.10 or 3.11 (64-bit), then double-click `run.bat` (or: `pip install -r requirements.txt` and `python main.py`).

Theory: r = d/2, NA = sin(theta) = r / sqrt(r^2 + L^2), acceptance angle = 2*theta, theory NA = sqrt(n1^2 - n2^2).

Procedure: move the distance slider, read spot diameter d, press Record; repeat for 5+ distances.
Mean NA, acceptance angle, graph-slope NA and % error vs theory appear automatically.

Gestures (Start hand-gesture control): index finger only = rotate view; open palm, change thumb-index spread = distance L;
closed fist held ~1.2 s = record reading. Mouse also works (left drag rotate, wheel zoom).
