import pandas as pd
from ctgan.ctgan import CTGAN
import matplotlib.pyplot as plt
from rdt.transformers import ClusterBasedNormalizer, OneHotEncoder
import pickle
from imblearn.over_sampling import SMOTE

# Load CSV Data
def load_data(file_path):
    data = pd.read_csv(file_path)
    if data.isnull().values.any():
        data.dropna(inplace=True)  
    
    # Add Continuous Column Name
    continuous_columns = []
    
    for col in data.columns:
        if col in continuous_columns:
            data[col] = data[col].astype(float)
        else:
            data[col] = data[col].astype(int)
    return data

# Add Discrete Column Name
discrete_columns = []

file_path = ''
real_data = load_data(file_path)

# Change As You Need
ddos_attack = real_data
other_data = real_data

# Merge DDoS Attack Data And Other Data (After Randomly Select Data from Training Dataset)
resampled_data = pd.concat([ddos_attack, other_data])
resampled_data = resampled_data.sample(frac=1, random_state=42).reset_index(drop=True)

# Initialize CTGAN Model And Train
ctgan = CTGAN(epochs=500)
ctgan.fit(resampled_data, discrete_columns)

# Save Model
with open('ctgan_model.pkl', 'wb') as f:
    pickle.dump(ctgan, f)

# Visualization (Optional)
# def plot_losses(ctgan):
#     plt.figure(figsize=(20, 5))
#     plt.plot(ctgan.generator_losses, label='Generator Loss')
#     plt.plot(ctgan.discriminator_losses, label='Discriminator Loss')
#     plt.title('Training Losses')
#     plt.xlabel('Epochs')
#     plt.ylabel('Loss')
#     plt.legend()
#     plt.show()
#     plt.savefig('loss.png')

# plot_losses(ctgan)
