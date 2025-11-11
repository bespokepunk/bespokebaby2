#!/usr/bin/env python3
"""
Train ResNet-18 classifier on synthetic + real data

Multi-label classification for:
- Expression (neutral, slight_smile)
- Hairstyle (straight, curly, wavy)
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
from PIL import Image
import json
import os
import numpy as np
from sklearn.model_selection import train_test_split

# Configuration
SYNTHETIC_DATA_DIR = "synthetic_training_data"
REAL_DATA_DIR = "runpod_package/training_data_IMPROVED"
OUTPUT_MODEL = "bespoke_classifier.pth"
BATCH_SIZE = 32
EPOCHS = 20
LEARNING_RATE = 0.001

class BespokePunkDataset(Dataset):
    """Dataset for bespoke punks with expression/hairstyle labels"""

    def __init__(self, image_paths, labels, transform=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        # Load image
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert('RGB')

        # Apply transforms
        if self.transform:
            image = self.transform(image)

        # Get labels
        label = self.labels[idx]

        return image, label

def load_synthetic_data():
    """Load synthetic data with labels from JSON"""
    print("Loading synthetic data...")

    labels_file = f"{SYNTHETIC_DATA_DIR}/labels.json"
    if not os.path.exists(labels_file):
        print(f"ERROR: {labels_file} not found. Run generate_synthetic_training_data.py first.")
        return [], []

    with open(labels_file, 'r') as f:
        data = json.load(f)

    image_paths = []
    labels = []

    # Label encoding
    expression_map = {'neutral': 0, 'slight_smile': 1}
    hairstyle_map = {'straight': 0, 'curly': 1, 'wavy': 2}

    for item in data:
        img_path = f"{SYNTHETIC_DATA_DIR}/images/{item['filename']}"
        if os.path.exists(img_path):
            image_paths.append(img_path)
            labels.append({
                'expression': expression_map[item['expression']],
                'hairstyle': hairstyle_map[item['hairstyle']]
            })

    print(f"  ✓ Loaded {len(image_paths)} synthetic images")
    return image_paths, labels

def load_real_data():
    """Load real training data with labels from captions"""
    print("Loading real training data...")

    if not os.path.exists(REAL_DATA_DIR):
        print(f"  ⚠ Real data dir not found: {REAL_DATA_DIR}")
        return [], []

    image_paths = []
    labels = []

    # Label encoding
    expression_map = {'neutral': 0, 'slight_smile': 1, 'neutral expression': 0, 'slight smile': 1}
    hairstyle_map = {'straight': 0, 'curly': 1, 'wavy': 2, 'straight hair': 0, 'curly hair': 1, 'wavy hair': 2}

    for filename in os.listdir(REAL_DATA_DIR):
        if filename.endswith('.png'):
            img_path = f"{REAL_DATA_DIR}/{filename}"
            caption_path = img_path.replace('.png', '.txt')

            if os.path.exists(caption_path):
                with open(caption_path, 'r') as f:
                    caption = f.read().lower()

                # Extract expression
                expression = None
                if 'neutral' in caption or 'straight neutral line' in caption:
                    expression = 0
                elif 'smile' in caption or 'turned up' in caption:
                    expression = 1

                # Extract hairstyle
                hairstyle = None
                if 'curly' in caption or 'coiled' in caption:
                    hairstyle = 1
                elif 'wavy' in caption or 'flowing curves' in caption:
                    hairstyle = 2
                elif 'straight' in caption:
                    hairstyle = 0

                # Only include if both labels present
                if expression is not None and hairstyle is not None:
                    image_paths.append(img_path)
                    labels.append({
                        'expression': expression,
                        'hairstyle': hairstyle
                    })

    print(f"  ✓ Loaded {len(image_paths)} real images with both labels")
    return image_paths, labels

class BespokePunkClassifier(nn.Module):
    """ResNet-18 based multi-label classifier"""

    def __init__(self, num_expression_classes=2, num_hairstyle_classes=3):
        super(BespokePunkClassifier, self).__init__()

        # Load pre-trained ResNet-18
        self.backbone = models.resnet18(pretrained=True)

        # Replace final layer with two heads
        num_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Identity()  # Remove original fc

        # Expression head
        self.expression_head = nn.Linear(num_features, num_expression_classes)

        # Hairstyle head
        self.hairstyle_head = nn.Linear(num_features, num_hairstyle_classes)

    def forward(self, x):
        # Get features from backbone
        features = self.backbone(x)

        # Two separate predictions
        expression_out = self.expression_head(features)
        hairstyle_out = self.hairstyle_head(features)

        return expression_out, hairstyle_out

def train_model():
    """Train the classifier"""

    print("=" * 80)
    print("BESPOKE PUNK CLASSIFIER TRAINING")
    print("=" * 80)
    print()

    # Load data
    synthetic_paths, synthetic_labels = load_synthetic_data()
    real_paths, real_labels = load_real_data()

    # Combine datasets
    all_paths = synthetic_paths + real_paths
    all_labels = synthetic_labels + real_labels

    print(f"\nTotal dataset: {len(all_paths)} images")
    print(f"  - Synthetic: {len(synthetic_paths)}")
    print(f"  - Real: {len(real_paths)}")

    if len(all_paths) == 0:
        print("ERROR: No data found. Generate synthetic data first.")
        return

    # Split train/val
    train_paths, val_paths, train_labels, val_labels = train_test_split(
        all_paths, all_labels, test_size=0.2, random_state=42
    )

    print(f"\nTrain set: {len(train_paths)}")
    print(f"Val set: {len(val_paths)}")

    # Data transforms
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # Create datasets
    train_dataset = BespokePunkDataset(train_paths, train_labels, train_transform)
    val_dataset = BespokePunkDataset(val_paths, val_labels, val_transform)

    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=2)

    # Initialize model
    print("\nInitializing model...")
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    model = BespokePunkClassifier().to(device)

    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    print(f"Device: {device}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Epochs: {EPOCHS}")
    print()

    # Training loop
    best_val_acc = 0.0

    for epoch in range(EPOCHS):
        # Train
        model.train()
        train_loss = 0.0
        train_correct_expr = 0
        train_correct_hair = 0
        train_total = 0

        for images, labels in train_loader:
            images = images.to(device)
            expr_labels = torch.tensor([l['expression'] for l in labels]).to(device)
            hair_labels = torch.tensor([l['hairstyle'] for l in labels]).to(device)

            optimizer.zero_grad()

            expr_out, hair_out = model(images)

            loss_expr = criterion(expr_out, expr_labels)
            loss_hair = criterion(hair_out, hair_labels)
            loss = loss_expr + loss_hair

            loss.backward()
            optimizer.step()

            train_loss += loss.item()

            # Accuracy
            _, expr_pred = torch.max(expr_out, 1)
            _, hair_pred = torch.max(hair_out, 1)
            train_correct_expr += (expr_pred == expr_labels).sum().item()
            train_correct_hair += (hair_pred == hair_labels).sum().item()
            train_total += len(labels)

        # Validation
        model.eval()
        val_loss = 0.0
        val_correct_expr = 0
        val_correct_hair = 0
        val_total = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device)
                expr_labels = torch.tensor([l['expression'] for l in labels]).to(device)
                hair_labels = torch.tensor([l['hairstyle'] for l in labels]).to(device)

                expr_out, hair_out = model(images)

                loss_expr = criterion(expr_out, expr_labels)
                loss_hair = criterion(hair_out, hair_labels)
                loss = loss_expr + loss_hair

                val_loss += loss.item()

                _, expr_pred = torch.max(expr_out, 1)
                _, hair_pred = torch.max(hair_out, 1)
                val_correct_expr += (expr_pred == expr_labels).sum().item()
                val_correct_hair += (hair_pred == hair_labels).sum().item()
                val_total += len(labels)

        # Calculate accuracies
        train_expr_acc = 100.0 * train_correct_expr / train_total
        train_hair_acc = 100.0 * train_correct_hair / train_total
        val_expr_acc = 100.0 * val_correct_expr / val_total
        val_hair_acc = 100.0 * val_correct_hair / val_total
        avg_val_acc = (val_expr_acc + val_hair_acc) / 2

        print(f"Epoch {epoch+1}/{EPOCHS}")
        print(f"  Train: Expr {train_expr_acc:.1f}% | Hair {train_hair_acc:.1f}% | Loss {train_loss/len(train_loader):.4f}")
        print(f"  Val:   Expr {val_expr_acc:.1f}% | Hair {val_hair_acc:.1f}% | Loss {val_loss/len(val_loader):.4f}")

        # Save best model
        if avg_val_acc > best_val_acc:
            best_val_acc = avg_val_acc
            torch.save(model.state_dict(), OUTPUT_MODEL)
            print(f"  ✓ New best model saved (avg {avg_val_acc:.1f}%)")
        print()

    print("=" * 80)
    print("TRAINING COMPLETE")
    print("=" * 80)
    print(f"Best validation accuracy: {best_val_acc:.1f}%")
    print(f"Model saved: {OUTPUT_MODEL}")
    print("\nNext: Run validate_classifier.py to test on real images")

if __name__ == "__main__":
    train_model()
