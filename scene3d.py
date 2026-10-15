"""3D apparatus built with PyVista (units: cm). Fiber end at x=0, screen at x=L."""
import numpy as np
import pyvista as pv
import na_physics as phys


class ApparatusScene:
    def __init__(self, plotter):
        self.p = plotter
        self.na, self.L, self.laser_on, self.t = 0.48, 8.0, True, 0.0
        p = self.p
        p.set_background("#05070d", top="#1b2a49")
        p.add_mesh(pv.Box(bounds=(-34, 20, -9, 9, -4.2, -3.2)), color="#3a3f4b", name="bench")
        p.add_mesh(pv.Cylinder(center=(-28, 0, 0), direction=(1, 0, 0), radius=1.6, height=8),
                   color="#b22222", name="laser", specular=0.6)
        p.add_mesh(pv.Cylinder(center=(-28, 0, -2.2), direction=(0, 0, 1), radius=0.8, height=2.2),
                   color="#555b66", name="laser_stand")
        pts = np.array([(-24, 0, 0), (-18, 3, 0.8), (-10, -3, -0.8), (-4, 1, 0), (0, 0, 0)], float)
        self.spline = pv.Spline(pts, 300)
        p.add_mesh(self.spline.tube(radius=0.32), color="#d9d9d9", opacity=0.25, name="jacket")
        p.add_mesh(self.spline.tube(radius=0.12), color="#ff3b3b", name="core", emissive=False)
        p.add_mesh(pv.Cylinder(center=(-1.2, 0, -1.6), direction=(0, 0, 1), radius=0.9, height=3.2),
                   color="#555b66", name="holder")
        self.beads_poly = pv.PolyData(self.spline.points[:8].copy())
        p.add_mesh(self.beads_poly, color="#ffe0e0", point_size=13,
                   render_points_as_spheres=True, name="beads")
        p.add_text("NUMERICAL APERTURE OF OPTICAL FIBER", position="upper_edge",
                   font_size=11, color="white", name="title")
        p.camera_position = [(8, -48, 20), (-8, 0, 0), (0, 0, 1)]
        self.update_beam()

    def set_na(self, na):
        self.na = na
        self.update_beam()

    def set_distance(self, L):
        self.L = L
        self.update_beam()

    def set_laser(self, on):
        self.laser_on = on
        self.update_beam()

    def update_beam(self):
        p, L = self.p, self.L
        th = np.arcsin(min(self.na, 0.999))
        r = L * np.tan(th)
        p.add_mesh(pv.Plane(center=(L, 0, 0), direction=(1, 0, 0), i_size=24, j_size=24),
                   color="#e8e8e8", opacity=0.55, name="screen")
        p.add_mesh(pv.Line((0, 0, -3.6), (L, 0, -3.6)), color="#4ec9ff", line_width=4, name="ruler")
        p.add_mesh(pv.Cone(center=(L / 2, 0, 0), direction=(-1, 0, 0), height=L, radius=r, resolution=72),
                   color="#ff4040", opacity=0.30, name="cone", show_edges=False)
        p.add_mesh(pv.Disc(center=(L - 0.03, 0, 0), inner=0, outer=r * 1.15, normal=(1, 0, 0), c_res=72),
                   color="#ff8080", opacity=0.35, name="glow")
        p.add_mesh(pv.Disc(center=(L - 0.05, 0, 0), inner=0, outer=r, normal=(1, 0, 0), c_res=72),
                   color="#ff1a1a", name="spot")
        for n in ("cone", "glow", "spot"):
            p.actors[n].SetVisibility(self.laser_on)
        p.add_text(f"L = {L:.1f} cm   spot d = {2 * r:.2f} cm   half-angle = {np.degrees(th):.1f} deg",
                   position="lower_left", font_size=11, color="white", name="hud")
        p.render()

    def animate(self):
        if not self.laser_on:
            self.beads_poly.points = self.spline.points[:1].repeat(8, axis=0)
        else:
            self.t = (self.t + 0.006) % 1.0
            s = (np.arange(8) / 8.0 + self.t) % 1.0
            self.beads_poly.points = self.spline.points[(s * (len(self.spline.points) - 1)).astype(int)]
        self.p.render()
