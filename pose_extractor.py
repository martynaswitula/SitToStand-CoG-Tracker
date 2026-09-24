import cv2
import mediapipe as mp

class PoseExtractor:
    def __init__(self, max_frames=500):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.landmark_buffer = []  # Zapis punktów
        self.max_frames = max_frames
        self.frame_index = 0

    def extract(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)

        landmarks_data = []
        if results.pose_landmarks:
            for landmark in results.pose_landmarks.landmark:
                landmarks_data.append({
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z,
                    'visibility': landmark.visibility
                })
            self.landmark_buffer.append(landmarks_data)
            self.frame_index += 1
        return landmarks_data

    def reset(self):
        self.landmark_buffer = []
        self.frame_index = 0

    def get_data(self):
        return self.landmark_buffer
