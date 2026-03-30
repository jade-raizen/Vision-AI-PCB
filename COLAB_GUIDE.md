# Guide : Entraînement YOLO sur Google Colab

Pour obtenir des résultats en quelques minutes plutôt qu'en plusieurs heures, utilisez la puissance d'un GPU NVIDIA gratuit sur Google Colab.

## 1. Préparation
Vous avez déjà une archive prête : [all_pcb_yolo.zip](file:///e:/New_vision_AI/datasets/all_pcb_yolo.zip).

## 2. Étapes sur Colab
1. Allez sur [colab.research.google.com](https://colab.research.google.com/).
2. Créez un **Nouveau Notebook**.
3. **Activer le GPU** : 
   - Allez dans **Modifier** > **Paramètres du notebook**.
   - Choisissez **T4 GPU** comme accélérateur matériel.
4. **Uploader le Dataset** :
   - Cliquez sur l'icône **Dossier** à gauche.
   - Glissez-déposez le fichier `all_pcb_yolo.zip` dans la zone de fichiers.

## 3. Script à copier-coller dans une cellule
```python
# 1. Installer Ultralytics
!pip install ultralytics

# 2. Dézipper le dataset
import shutil
import os
if os.path.exists('/content/all_pcb_yolo.zip'):
    shutil.unpack_archive('/content/all_pcb_yolo.zip', '/content/datasets/all_pcb_yolo')

# 3. Lancer l'entraînement
from ultralytics import YOLO
model = YOLO('yolo11n.pt') # Utilise YOLO11 par défaut
model.train(
    data='/content/datasets/all_pcb_yolo/dataset.yaml',
    epochs=5,
    imgsz=640,
    device=0 # Utilise le GPU automatique
)

# 4. Télécharger le modèle fini
from google.colab import files
files.download('/content/runs/detect/train/weights/best.pt')
```

## 4. Récupération
Une fois l'entraînement fini, le fichier `best.pt` sera téléchargé. Renommez-le en `yolo11_pcb_final.pt` et placez-le dans votre dossier `e:\New_vision_AI\`.
