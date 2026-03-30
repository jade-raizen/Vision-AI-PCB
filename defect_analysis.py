import torch
import torch.nn as nn
import cv2
import numpy as np

class SolderAnomalyAE(nn.Module):
    """
    Convolutional Autoencoder for Solder Joint Anomaly Detection.
    Inspired by 'Anomaly Detection for Solder Joints Using beta-VAE'.
    """
    def __init__(self):
        super(SolderAnomalyAE, self).__init__()
        # Encoder
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 32, 3, stride=2, padding=1), # [batch, 3, 64, 64] -> [batch, 32, 32, 32]
            nn.ReLU(),
            nn.Conv2d(32, 64, 3, stride=2, padding=1), # [batch, 64, 16, 16]
            nn.ReLU(),
            nn.Conv2d(64, 128, 3, stride=2, padding=1), # [batch, 128, 8, 8]
            nn.ReLU()
        )
        # Decoder
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(128, 64, 3, stride=2, padding=1, output_padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(64, 32, 3, stride=2, padding=1, output_padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(32, 3, 3, stride=2, padding=1, output_padding=1),
            nn.Sigmoid()
        )

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x

def analyze_defect(image_patch, model_path=None):
    """
    Analyzes a patch (e.g., a solder joint or a component) for anomalies.
    Returns an anomaly score based on reconstruction error.
    """
    # Preprocessing
    img = cv2.resize(image_patch, (64, 64))
    img = img.astype(np.float32) / 255.0
    img = np.transpose(img, (2, 0, 1))
    img_tensor = torch.from_numpy(img).unsqueeze(0)

    model = SolderAnomalyAE()
    if model_path and os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path))
    model.eval()

    with torch.no_grad():
        reconstruction = model(img_tensor)
        loss = nn.MSELoss()(reconstruction, img_tensor)
        
    return loss.item()

if __name__ == "__main__":
    print("Defect Analysis Module Initialized.")
    # In a real scenario, we would crop detections from YOLO and pass them here.
    dummy_patch = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    score = analyze_defect(dummy_patch)
    print(f"Anomaly Score (DUMMY): {score:.6f}")
