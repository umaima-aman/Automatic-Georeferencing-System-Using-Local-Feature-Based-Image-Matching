import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk, ImageDraw
import os
from tkinter import Toplevel

# Global Variables
reference_img = None
aerial_img = None
aerial_img_display = None
reference_path = None
aerial_path = None
rotation_angle = 0
aerial_images = []
ref_keypoints, ref_descriptors = None, None
aer_keypoints, aer_descriptors = None, None
ref_x, ref_y = None, None
ref_width, ref_height = None, None
click_coordinates = []
homography_matrix = None
detector_method = "SIFT"  # Default method 
zoom_scale_aer = 0.3

# Load Reference Image
def load_reference_image():
    global reference_img, reference_path, ref_width, ref_height
    file_path = filedialog.askopenfilename(filetypes=[("TIFF Files", "*.tif"), ("All Files", "*.*")])
    
    if not file_path or not os.path.isfile(file_path):
        print("No valid file selected.")
        return
    
    reference_path = file_path
    reference_img = cv2.imread(file_path)

    ref_height, ref_width = reference_img.shape[:2]

    resized_img, display_width, display_height = resize_image_to_fit(reference_img, (700, 500))
    canvas_ref.config(width=display_width, height=display_height)

    ref_width, ref_height = display_width, display_height
    display_image(resized_img, canvas_ref)

# Zoom Levels
zoom_scale_ref = 0.3
zoom_scale_aer = 0.3
# Zoom Function
def zoom_image(image, scale):
    if image is None:
        return None
    h, w = image.shape[:2]
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(image, (new_w, new_h))
# Zoom In and Out Functions
def zoom_in_ref():
    global reference_img, zoom_scale_ref
    if reference_img is not None:
        zoom_scale_ref *= 1.2
        zoomed_img = zoom_image(reference_img, zoom_scale_ref)
        display_image(zoomed_img, canvas_ref)

def zoom_out_ref():
    global reference_img, zoom_scale_ref
    if reference_img is not None:
        zoom_scale_ref /= 1.2
        zoomed_img = zoom_image(reference_img, zoom_scale_ref)
        display_image(zoomed_img, canvas_ref)

def zoom_in_aer():
    global aerial_img, zoom_scale_aer
    if aerial_img is not None:
        zoom_scale_aer *= 1.2
        zoomed_img = zoom_image(aerial_img, zoom_scale_aer)
        display_image(zoomed_img, canvas_aer)
def zoom_out_aer():
    global aerial_img, zoom_scale_aer
    if aerial_img is not None:
        zoom_scale_aer /= 1.2
        zoomed_img = zoom_image(aerial_img, zoom_scale_aer)
        display_image(zoomed_img, canvas_aer)

# Resize Image to Fit Window
def resize_image_to_fit(img, max_size):
    h, w = img.shape[:2]
    max_w, max_h = max_size
    scale = min(max_w / w, max_h / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    resized_img = cv2.resize(img, (new_w, new_h))
    return resized_img, new_w, new_h
# Scan and Load Aerial Images
def scan_aerial_images():
    global aerial_images
    folder_path = filedialog.askdirectory()
    if folder_path:
        aerial_images = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith((".png", ".jpg", ".jpeg", ".tif"))]      
        if aerial_images:
            aerial_dropdown["values"] = aerial_images
            aerial_dropdown.set(aerial_images[0])
        else:
            aerial_dropdown["values"] = []
            aerial_dropdown.set("")

# Load Aerial Image
def load_aerial_image(event):
    global aerial_img, aerial_img_display, aerial_path
    selected_image = aerial_dropdown.get() 
    if selected_image and reference_img is not None:
        aerial_path = selected_image
        aerial_img = cv2.imread(selected_image)
        aerial_img_display = cv2.resize(aerial_img, (ref_width, ref_height))      
        canvas_aer.config(width=ref_width, height=ref_height)
        display_image(aerial_img_display, canvas_aer)
        canvas_aer.bind("<Button-1>", capture_coordinates) 
"""# Rotate Aerial Image
def rotate_aerial_image():
    global aerial_img, aerial_img_display, rotation_angle
    if aerial_img is None:
        return

    rotation_angle += 10
    height, width = aerial_img.shape[:2]
    center = (width // 2, height // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, rotation_angle, 1.0)
    aerial_img_rotated = cv2.warpAffine(aerial_img, rotation_matrix, (width, height))
    
    aerial_img_display = cv2.resize(aerial_img_rotated, (ref_width, ref_height))
    display_image(aerial_img_display, canvas_aer)"""
# Display Image
def display_image(img, canvas):
    if img is None:
        return
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
    img = Image.fromarray(img)
    img_tk = ImageTk.PhotoImage(img)
    canvas.config(width=img.width, height=img.height)
    canvas.pack_propagate(False)  
    canvas.delete("all")  # Remove previous image to avoid overlap
    canvas.create_image(img.width // 2, img.height // 2, anchor=tk.CENTER, image=img_tk)
    canvas.image = img_tk  # Keep a reference to prevent garbage collection

# Capture Click Coordinates
def capture_coordinates(event):
    global click_coordinates
    x, y = event.x, event.y
    click_coordinates.append((x, y))
    update_coordinate_display(x, y)
# Update Coordinate Display
def update_coordinate_display(x, y):
    coord_label.config(text=f"Clicked Coordinates (Aerial): X={x}, Y={y}")
# Compute Keypoints and Descriptors
def compute_keypoints():
    global detector_method, ref_keypoints, aer_keypoints, ref_descriptors, aer_descriptors
    if reference_img is None or aerial_img is None:
        print("Both reference and aerial images must be loaded first.")
        return
    detector_method = method_dropdown.get()
    ref_gray = cv2.cvtColor(reference_img, cv2.COLOR_BGR2GRAY)
    aer_gray = cv2.cvtColor(aerial_img, cv2.COLOR_BGR2GRAY)
    if detector_method == "SIFT":
        detector = cv2.SIFT_create()
        norm_type = cv2.NORM_L2
    elif detector_method == "ORB":
        detector = cv2.ORB_create()
        norm_type = cv2.NORM_HAMMING
    elif detector_method == "Harris":
        # Harris Corner Detection - No descriptors, only keypoints
        ref_corners = cv2.cornerHarris(ref_gray, 2, 3, 0.04)
        aer_corners = cv2.cornerHarris(aer_gray, 2, 3, 0.04)
        ref_keypoints = [cv2.KeyPoint(float(x), float(y), 5) for y, x in np.argwhere(ref_corners > 0.01 * ref_corners.max())]
        aer_keypoints = [cv2.KeyPoint(float(x), float(y), 5) for y, x in np.argwhere(aer_corners > 0.01 * aer_corners.max())]
        print(f"Harris: {len(ref_keypoints)} keypoints in reference image, {len(aer_keypoints)} in aerial image.")
        return  # Stop as Harris has no descriptors
    # Compute Keypoints and Descriptors for SIFT/ORB
    ref_keypoints, ref_descriptors = detector.detectAndCompute(ref_gray, None)
    aer_keypoints, aer_descriptors = detector.detectAndCompute(aer_gray, None)
    if ref_descriptors is None or aer_descriptors is None:
        print("No keypoints detected in one of the images!")
        return
    # Match descriptors
    bf = cv2.BFMatcher(norm_type, crossCheck=True)
    matches = bf.match(ref_descriptors, aer_descriptors)
    matches = sorted(matches, key=lambda x: x.distance)  # Sort by quality
    print(f"{detector_method}: {len(ref_keypoints)} keypoints in reference image, {len(aer_keypoints)} in aerial image.")
    print(f"{detector_method}: {len(matches)} matches found between reference and aerial images.")
# Compute Homography
def compute_homography():
    global homography_matrix, ref_keypoints, ref_descriptors, aer_keypoints, aer_descriptors
    if reference_img is None or aerial_img is None:
        print("Load both reference and aerial images first!")
        return
    detector_method = method_dropdown.get()
    if detector_method == "Harris":
 # Harris has keypoints but no descriptors, so we find nearest keypoints
        if len(ref_keypoints) < 4 or len(aer_keypoints) < 4:
            print("Not enough Harris keypoints found for homography!")
            return
# Convert keypoints to NumPy arrays
        ref_pts = np.float32([kp.pt for kp in ref_keypoints])
        aer_pts = np.float32([kp.pt for kp in aer_keypoints])
        # Find nearest keypoints based on Euclidean distance
        from scipy.spatial import KDTree
        tree = KDTree(aer_pts)
        _, indices = tree.query(ref_pts[:len(aer_pts)])  # nearest matches
# Ensure we have at least 4 valid pairs
        if len(indices) < 4:
            print("Not enough valid matches found for Harris homography!")
            return
        ref_pts = ref_pts[:len(indices)]
        aer_pts = aer_pts[indices]
    else:
        if ref_descriptors is None or aer_descriptors is None:
            print("No descriptors available for homography computation!")
            return
# Match descriptors
        norm_type = cv2.NORM_L2 if detector_method == "SIFT" else cv2.NORM_HAMMING
        bf = cv2.BFMatcher(norm_type, crossCheck=True)
        matches = bf.match(ref_descriptors, aer_descriptors)
        matches = sorted(matches, key=lambda x: x.distance)
        if len(matches) < 4:
            print("Not enough matches for homography!")
            return
 # Extract matched keypoints
        ref_pts = np.float32([ref_keypoints[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        aer_pts = np.float32([aer_keypoints[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
# Compute Homography using RANSAC
    homography_matrix, _ = cv2.findHomography(aer_pts, ref_pts, cv2.RANSAC, 5.0)
    print("Homography matrix computed successfully!")
    homography_label.config(text=f"Homography Matrix:\n{homography_matrix}")

#  Project clicked aerial image pixel to reference image
def project_to_reference():
    global homography_matrix, ref_x, ref_y
    if homography_matrix is None:
        print("Homography matrix is not computed yet!")
        return
    if not click_coordinates:
        print("No coordinates clicked yet!")
        return
    x, y = click_coordinates[-1]  #last clicked point
# Convert point into homogeneous coordinates
    point = np.array([x, y, 1]).reshape(3, 1)
    projected_point = np.dot(homography_matrix, point)
    projected_point /= projected_point[2]  # Normalize
    ref_x, ref_y = int(projected_point[0]), int(projected_point[1])
    print(f"Projected Coordinates on Reference Image: X={ref_x}, Y={ref_y}")
    projected_label.config(text=f"Projected X={ref_x}, Y={ref_y}")
def compute_lat_lon():
    global ref_x, ref_y, lat, lon
    if ref_x is None or ref_y is None:
        print("No projected coordinates available!")
        return
# Define lat/lon bounds 
    TOP_LEFT_LAT, TOP_LEFT_LON = 37.7749, -122.4194  
    BOTTOM_RIGHT_LAT, BOTTOM_RIGHT_LON = 37.7659, -122.4094  
 # Compute scaling factors
    lat_range = TOP_LEFT_LAT - BOTTOM_RIGHT_LAT
    lon_range = BOTTOM_RIGHT_LON - TOP_LEFT_LON
# Compute interpolated lat/lon
    lat = TOP_LEFT_LAT - (ref_y / reference_img.shape[0]) * lat_range
    lon = TOP_LEFT_LON + (ref_x / reference_img.shape[1]) * lon_range
    print(f"Computed Latitude: {lat:.6f}, Longitude: {lon:.6f}")
    lat_lon_label.config(text=f"Latitude: {lat:.6f}, Longitude: {lon:.6f}")
class ZoomableImage:
    def __init__(self, root, image, x, y, lat, lon):
        self.root = root  
        self.image = image  
        self.marker_x, self.marker_y = x, y  
        self.lat, self.lon = lat, lon  
        self.zoom_factor = 1.0  
# Convert OpenCV image to PIL
        self.img_pil = Image.fromarray(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB))
# Create new window
        self.window = Toplevel(self.root)
        self.window.title("Aerial Image with Coordinates")
# Create canvas
        self.canvas = tk.Canvas(self.window, width=self.img_pil.width+50, height=self.img_pil.height+50)
        self.canvas.pack(fill=tk.BOTH, expand=True)
# Add image to canvas
        self.tk_img = ImageTk.PhotoImage(self.img_pil)
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
# Draw marker
        self.draw_marker()
        # Bind zoom events
        self.canvas.bind("<MouseWheel>", self.zoom) 
        self.canvas.bind("<Button-4>", self.zoom)  
        self.canvas.bind("<Button-5>", self.zoom)  
    def draw_marker(self):
        #Draws a marker and coordinates on the zoomed image.
        zoomed_img = self.resize_image(self.image, self.zoom_factor)
        img_pil = Image.fromarray(cv2.cvtColor(zoomed_img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        # Get image dimensions
        img_w, img_h = zoomed_img.shape[1], zoomed_img.shape[0]
        zoomed_x = int(self.marker_x * self.zoom_factor)
        zoomed_y = int(self.marker_y * self.zoom_factor)
        zoomed_x = max(15, min(zoomed_x, img_w - 15))  
        zoomed_y = max(15, min(zoomed_y, img_h - 15))
        # Draw marker 
        marker_size = 10
        draw.ellipse((zoomed_x - marker_size, zoomed_y - marker_size,
                      zoomed_x + marker_size, zoomed_y + marker_size),
                     fill="red", outline="black", width=2)
        text = f"{self.lat:.2f}, {self.lon:.2f}"
        text_x = zoomed_x + 12
        text_y = zoomed_y - 12
        if zoomed_y < 20:
            text_y = zoomed_y + 15  
        if zoomed_x > img_w - 50:
            text_x = zoomed_x - 50  

        draw.text((text_x, text_y), text, fill="black")
        # Convert to Tkinter image and update canvas
        self.tk_img = ImageTk.PhotoImage(img_pil)
        self.canvas.itemconfig(self.image_on_canvas, image=self.tk_img)
        self.canvas.update()  
    def resize_image(self, img, scale):
        h, w = img.shape[:2]
        new_w, new_h = int(w * scale), int(h * scale)
        return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    def zoom(self, event):
        """Handle zooming in and out."""
        zoom_step = 1.2  
        if hasattr(event, "delta"):  
            if event.delta > 0:
                self.zoom_factor *= zoom_step
            else:
                self.zoom_factor /= zoom_step
        elif event.num == 4:  
            self.zoom_factor *= zoom_step
        elif event.num == 5:  
            self.zoom_factor /= zoom_step
        self.zoom_factor = max(0.5, min(self.zoom_factor, 5.0))
        self.draw_marker()
# display coordinates 
def show_coordinates():
    global aerial_img, ref_x, ref_y, lat, lon, root, coord_label
    if aerial_img is None or ref_x is None or ref_y is None:
        print("Cannot display coordinates. Missing data!")
        return

    ZoomableImage(root, aerial_img, ref_x, ref_y, lat, lon)
    ref_x = max(0, min(ref_x, aerial_img.shape[1] - 1))
    ref_y = max(0, min(ref_y, aerial_img.shape[0] - 1))
    display_img = aerial_img.copy()
    cv2.circle(display_img, (ref_x, ref_y), 8, (0, 255, 0), -1)  
    text_position = (ref_x + 10, ref_y - 10)
    if ref_y < 2:  
        text_position = (ref_x + 10, ref_y + 20)
    cv2.putText(display_img, f"{lat:.6f}, {lon:.6f}", text_position,
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    coord_label.config(text=f"Latitude: {lat:.6f}, Longitude: {lon:.6f}")



# GUI Setup
root = tk.Tk()
root.title("Automatic Georeferencing System")

frame_top = tk.Frame(root)
frame_top.pack(pady=5)

btn_load_ref = tk.Button(frame_top, text="Load Reference Image", command=load_reference_image)
btn_load_ref.pack(side=tk.LEFT, padx=5)
btn_scan_aerial = tk.Button(frame_top, text="Select Aerial Image Folder", command=scan_aerial_images)
btn_scan_aerial.pack(side=tk.LEFT, padx=5)
aerial_dropdown = ttk.Combobox(frame_top, state="readonly", width=40)
aerial_dropdown.pack(side=tk.LEFT, padx=5)
aerial_dropdown.bind("<<ComboboxSelected>>", load_aerial_image)
btn_zoom_in_ref = tk.Button(frame_top, text="Zoom In (Ref)", command=zoom_in_ref)
btn_zoom_in_ref.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
btn_zoom_out_ref = tk.Button(frame_top, text="Zoom Out (Ref)", command=zoom_out_ref)
btn_zoom_out_ref.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
btn_zoom_in_aer = tk.Button(frame_top, text="Zoom In (Aerial)", command=zoom_in_aer)
btn_zoom_in_aer.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
btn_zoom_out_aer = tk.Button(frame_top, text="Zoom Out (Aerial)", command=zoom_out_aer)
btn_zoom_out_aer.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
btn_compute_keypoints = tk.Button(frame_top, text="Compute Keypoints", command=compute_keypoints)
btn_compute_keypoints.pack(side=tk.LEFT, padx=5)
method_dropdown = ttk.Combobox(frame_top, state="readonly", width=20)
method_dropdown["values"] = ["SIFT", "ORB", "Harris"]
method_dropdown.set("SIFT")
method_dropdown.pack(side=tk.LEFT, padx=5)
btn_compute_homography = tk.Button(frame_top, text="Compute Homography", command=compute_homography)
btn_compute_homography.pack(side=tk.LEFT, padx=5)
homography_label = tk.Label(root, text="Homography Matrix: Not Computed")
homography_label.pack()
coord_label = tk.Label(root, text="Clicked Coordinates: X=0, Y=0")
coord_label.pack()
btn_project_to_ref = tk.Button(root, text="Project to Reference", command=project_to_reference)
btn_project_to_ref.pack(padx=5)
projected_label = tk.Label(root, text="Projected X: N/A, Y: N/A")
projected_label.pack()
btn_compute_latlon = tk.Button(root, text="Compute Lat/Lon", command=compute_lat_lon)
btn_compute_latlon.pack(padx=5)
lat_lon_label = tk.Label(root, text="Latitude: N/A, Longitude: N/A")
lat_lon_label.pack()
btn_show_coords = tk.Button(root, text="Show Coordinates", command=show_coordinates)
btn_show_coords.pack(padx=5)
displayed_label = tk.Label(root, text="Displayed Coordinates: N/A")
displayed_label.pack()

canvas_ref = tk.Canvas(root, width=500, height=500)
canvas_ref.pack(side=tk.LEFT, padx=5)
canvas_aer = tk.Canvas(root, width=500, height=500)
canvas_aer.pack(side=tk.LEFT, padx=5)



root.mainloop()
