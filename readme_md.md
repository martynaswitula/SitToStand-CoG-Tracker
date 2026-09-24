# Sit-to-Stand CoG Tracker 🚶‍♂️📊

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose-orange.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-GUI-lightgrey.svg)
![Status](https://img.shields.io/badge/Status-Research%20Completed-success.svg)

## Overview

**Sit-to-Stand CoG Tracker** is a computer vision and biomechanics application developed explicitly for clinical physiotherapy research. The software tracks human kinematics during a Sit-to-Stand (STS) task, dynamically estimating and plotting the body's Center of Gravity (CoG) in real-time without the need for expensive marker-based motion capture systems.

### Clinical Background & Purpose

With the increasing occurrence of neurodegenerative diseases affecting human motor abilities, there is a growing need for non-pharmacological support methods. This application was built to investigate **movement sonification**—the process of mapping movement parameters onto elements of music or sound to enhance patient motivation, attention, and exercise accuracy. 

The software tracks the vertical movement of the patient's CoG and facilitates a specific clinical protocol to determine how continuous auditory feedback (e.g., a sound with increasing pitch) influences movement dynamics, such as velocity, acceleration, and jerk.

📖 **Scientific Publication:**
This tool was actively used to acquire and process data for the research described in the following pilot study:

> *"Impact of Auditory Treatment Motives on Basic Movement Support: A Pilot Study"*
> Authors: Aleksandra Tuszy, Patrycja Romaniszyn-Kania, Daniel Ledwoń, **Martyna Śwituła**, et al.
> *Faculty of Biomedical Engineering, Silesian University of Technology, Poland.*

## Key Features

* **Markerless Pose Estimation:** Utilizes Google's MediaPipe Pose to extract 33 anatomical landmarks from standard video feeds continuously.
* **Biomechanical CoG Calculation:** Dynamically computes the whole-body Center of Gravity based on established anthropometric segment mass fractions (head, torso, arms, forearms, hands, thighs, calves, feet).
* **Automated Clinical Workflow:** Includes built-in timers and precise auditory cues (beeps) specifically designed for a 20-second Sit-to-Stand research protocol (10s sit phase followed by 10s stand phase).
* **Transition Detection:** Automatically identifies the exact moment the patient transitions from sitting to standing by analyzing trajectory shifts.
* **Data Export for Statistical Analysis:** Normalizes movement trajectories and exports raw and normalized coordinates to `.csv` format for post-processing and feature extraction.
* **Interactive GUI:** Built with PyQt5 and Matplotlib for real-time visualization of the camera feed, skeletal landmarks, CoG point, and live trajectory plotting.

## System Architecture

1. **`pose_extractor.py`**: A dedicated wrapper around MediaPipe responsible for extracting structural body landmarks and maintaining the coordinate buffer.
2. **`cogs.py`**: Contains the core biomechanical logic. It maps 2D coordinates to anatomical segments and calculates the whole-body CoG using predefined mass fraction tables.
3. **`main.py`**: The main application loop orchestrating the PyQt5 GUI, camera threading, real-time Matplotlib plotting, phase timing, and data serialization.

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

3. Run the application:
   ```bash
   python main.py
   ```
   *Note for Mac/Linux users: The camera capture is currently configured with the `cv2.CAP_DSHOW` flag for Windows DirectShow. If you encounter camera initialization issues on other operating systems, simply remove this flag in the `cv2.VideoCapture` call within `main.py`.*

## Clinical Protocol Usage

The software is designed to be used in a controlled clinical or laboratory environment:

1. Position the patient sideways to the camera, seated on a standard chair.
2. Launch the application and select the correct camera source using the **Kamera** button.
3. Choose the desired real-time overlays (Center of Mass, Body Landmarks).
4. Click **Start** to initiate the protocol. The system will automatically guide the patient via audio cues:
   * **0-10s:** Sitting phase (warning beep at 7s).
   * **10-20s:** Standing phase (accompanied by auditory feedback/sonification).
5. Upon completion, the software automatically plots the transition curve.
6. Click **Zapisz CSV** to export the trial data for external statistical analysis.

## License & Acknowledgments

This project is intended for research, clinical evaluation, and portfolio purposes. Developed as part of biomechanical engineering studies at the Silesian University of Technology.