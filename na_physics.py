"""Physics for the Numerical Aperture experiment.
Setup: fiber end at x=0, screen at distance L. Light spot on screen has diameter d.
  r = d/2,  tan(theta) = r/L,  NA = sin(theta) = r / sqrt(r^2 + L^2)
  Acceptance angle = 2*theta.   Theory: NA = sqrt(n1^2 - n2^2).
"""
import numpy as np


def na_from_indices(n1, n2):
    return float(np.sqrt(max(n1 ** 2 - n2 ** 2, 0.0)))


def na_from_spot(d, L):
    r = d / 2.0
    return float(r / np.hypot(r, L))


def half_angle_deg(na):
    return float(np.degrees(np.arcsin(min(max(na, 0.0), 1.0))))


def spot_diameter(na, L):
    return float(2 * L * np.tan(np.arcsin(min(na, 0.999))))


def fit_na(Ls, ds):
    """Slope of r vs L gives tan(theta); returns NA from least-squares fit."""
    slope = np.polyfit(np.asarray(Ls, float), np.asarray(ds, float) / 2.0, 1)[0]
    return float(np.sin(np.arctan(slope)))
