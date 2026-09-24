# Sit-to-Stand CoG Tracker 🚶‍♂️📊

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose-orange.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-GUI-lightgrey.svg)
![Status](https://img.shields.io/badge/Status-Research%20Completed-success.svg)

## Overview
**Sit-to-Stand CoG Tracker** is a computer vision and biomechanics application designed for physiotherapy research. It tracks a patient's movement during a Sit-to-Stand (STS) task, dynamically estimating and plotting their Center of Gravity (CoG) in real-time. 

This software was explicitly developed for and utilized in clinical trials to analyze the impact of auditory feedback on movement dynamics in older adults. 

📖 **Scientific Publication:**  
This tool was used to conduct the research described in the pilot study:  
> *"Impact of Auditory Treatment Motives on Basic Movement Support: A Pilot Study"*  
> Authors: Aleksandra Tuszy, Patrycja Romaniszyn-Kania, Daniel Ledwoń, **Martyna Śwituła**, et al.  
> *Silesian University of Technology, Faculty of Biomedical Engineering.*

## Features
* **Real-time Pose Estimation:** Utilizes Google's MediaPipe Pose to extract body landmarks continuously.
* **Biomechanical CoG Calculation:** Dynamically computes the Center of Gravity based on anthropometric segment mass fractions (head, torso, arms, thighs, calves, feet).
* **Clinical Trial Workflow:** Built-in timers and auditory cues (beeps) specifically designed for a 20-second Sit-to-Stand protocol (10s sit, 10s stand).
* **Phase Transition Detection:** Automatically detects the exact moment the patient transitions from sitting to standing by analyzing the Y-coordinate drop.
* **Data Export:** Exports normalized movement trajectories to `.csv` for statistical analysis and `.jpg` for quick visualization.
* **Interactive GUI:** Built with PyQt5 and Matplotlib for real-time visualization of the camera feed and CoG trajectory.

## Demo / UI Overview
*(Add a screenshot of your application here. You can name it `app_screenshot.jpg` and place it in your repository)*
![Application GUI](app_screenshot.jpg)

## Architecture & Logic
1. **`pose_extractor.py`**: A wrapper around MediaPipe to extract 33 body landmarks and store them in a buffer.
2. **`cogs.py`**: Contains the core biomechanical logic. It maps 2D coordinates of body joints to anatomical segments and calculates the whole-body CoG using predefined mass fraction tables.
3. **`main.py`**: The main application loop. Handles the PyQt5 GUI, threading/timers for the camera feed, real-time Matplotlib plotting, and data saving operations.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/martynaswitula/SitToStand-CoG-Tracker.git
   cd SitToStand-CoG-Tracker
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: The dependencies include `opencv-python`, `mediapipe`, `pandas`, `numpy`, `PyQt5`, and `matplotlib`)*

3. Run the application:
   ```bash
   python main.py
   ```
   *Note for Mac/Linux users: The camera capture is currently configured with the `cv2.CAP_DSHOW` flag for Windows DirectShow. If you encounter camera issues, remove this flag in `main.py`.*

## Usage (Clinical Protocol)
1. Position the patient sideways to the camera, seated on a chair.
2. Select the correct camera source using the **Kamera** button.
3. Check the desired visualization overlays (Center of Mass, Body Landmarks).
4. Click **Start**. The protocol will guide the patient via audio cues:
   * **0-10s:** Sitting phase (auditory cue at 7s).
   * **10-20s:** Standing phase (continuous sound feedback if applied).
5. Review the generated trajectory plot. Click **Zapisz CSV** to export the trial data for further analysis.

## License
This project is intended for research and portfolio purposes. 
