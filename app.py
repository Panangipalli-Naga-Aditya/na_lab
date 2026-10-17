import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Virtual Numerical Aperture Lab")
st.write("Web version of the NA Lab application.")

distance = st.slider("Select Distance (L)", min_value=10.0, max_value=200.0, value=50.0)
spot_diameter = st.slider("Select Spot Diameter (d)", min_value=1.0, max_value=50.0, value=10.0)

r = spot_diameter / 2.0
theta = np.arctan(r / distance)
na = np.sin(theta)
acceptance_angle = 2 * np.degrees(theta)

st.metric(label="Calculated Numerical Aperture (NA)", value=f"{na:.4f}")
st.metric(label="Acceptance Angle", value=f"{acceptance_angle:.2f}°")

fig, ax = plt.subplots()
ax.plot([0, distance], [0, r], label="Ray Path")
ax.set_xlabel("Distance L")
ax.set_ylabel("Radius r")
ax.legend()
st.pyplot(fig)
