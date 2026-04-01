import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import joblib, os

#Config
SAVE_DIR    = os.path.join(os.path.dirname(__file__), "saved_models")
BATCH_SIZE  = 256
EPOCHS      = 60
LR          = 1e-3
HIDDEN      = [256, 128, 64, 32]
THRESHOLD   = 0.4
DEVICE      = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#Load preprocessed data
X_train = np.load(os.path.join(SAVE_DIR, "X_train.npy")).astype(np.float32)
X_test  = np.load(os.path.join(SAVE_DIR, "X_test.npy")).astype(np.float32)
y_train = np.load(os.path.join(SAVE_DIR, "y_train.npy")).astype(np.float32)
y_test  = np.load(os.path.join(SAVE_DIR, "y_test.npy")).astype(np.float32)

#Tensors & DataLoaders
train_ds = TensorDataset(torch.from_numpy(X_train), torch.from_numpy(y_train))
test_ds  = TensorDataset(torch.from_numpy(X_test),  torch.from_numpy(y_test))
train_dl = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
test_dl  = DataLoader(test_ds,  batch_size=BATCH_SIZE)

#Class weight (handle imbalance 78/22)
pos_weight = torch.tensor([(y_train == 0).sum() / (y_train == 1).sum()]).to(DEVICE)

#Model
class MLP(nn.Module):
    def __init__(self, in_features, hidden_sizes):
        super().__init__()
        layers = []
        prev = in_features
        for h in hidden_sizes:
            layers += [nn.Linear(prev, h), nn.BatchNorm1d(h), nn.ReLU(), nn.Dropout(0.3)]
            prev = h
        layers.append(nn.Linear(prev, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x).squeeze(1)

model     = MLP(X_train.shape[1], HIDDEN).to(DEVICE)
criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
optimizer = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=1e-4)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=15, gamma=0.5)

#Training loop
print(f"Training on {DEVICE}  |  {len(train_ds)} train / {len(test_ds)} test samples")
print(f"Network: {X_train.shape[1]} → {' → '.join(map(str, HIDDEN))} → 1   |  threshold={THRESHOLD}\n")
print(f"{'Epoch':>6}  {'Train Loss':>11}  {'Val Loss':>9}  {'Val Acc':>8}")
print("-" * 42)

for epoch in range(1, EPOCHS + 1):
    model.train()
    train_loss = 0.0
    for Xb, yb in train_dl:
        Xb, yb = Xb.to(DEVICE), yb.to(DEVICE)
        optimizer.zero_grad()
        loss = criterion(model(Xb), yb)
        loss.backward()
        optimizer.step()
        train_loss += loss.item() * len(Xb)
    train_loss /= len(train_ds)

    model.eval()
    val_loss, correct = 0.0, 0
    with torch.no_grad():
        for Xb, yb in test_dl:
            Xb, yb = Xb.to(DEVICE), yb.to(DEVICE)
            logits = model(Xb)
            val_loss += criterion(logits, yb).item() * len(Xb)
            preds = (torch.sigmoid(logits) >= THRESHOLD).float()
            correct += (preds == yb).sum().item()
    val_loss /= len(test_ds)
    val_acc   = correct / len(test_ds) * 100

    scheduler.step()
    print(f"{epoch:>6}  {train_loss:>11.4f}  {val_loss:>9.4f}  {val_acc:>7.2f}%")

#Final evaluation
model.eval()
all_probs, all_preds, all_labels = [], [], []
with torch.no_grad():
    for Xb, yb in test_dl:
        logits = model(Xb.to(DEVICE))
        probs  = torch.sigmoid(logits).cpu().numpy()
        preds  = (probs >= THRESHOLD).astype(int)
        all_probs.extend(probs)
        all_preds.extend(preds)
        all_labels.extend(yb.numpy().astype(int))

print("\n=== CLASSIFICATION REPORT ===")
print(classification_report(all_labels, all_preds, target_names=["Safe", "Risky"]))

print("=== CONFUSION MATRIX ===")
cm = confusion_matrix(all_labels, all_preds)
print(f"              Predicted Safe  Predicted Risky")
print(f"Actual Safe        {cm[0,0]:>5}           {cm[0,1]:>5}")
print(f"Actual Risky       {cm[1,0]:>5}           {cm[1,1]:>5}")

auc = roc_auc_score(all_labels, all_probs)
print(f"\nROC-AUC Score: {auc:.4f}")

torch.save(model.state_dict(), os.path.join(SAVE_DIR, "mlp_model.pth"))
print(f"\nModel saved → saved_models/mlp_model.pth")