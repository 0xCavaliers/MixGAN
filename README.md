# MixGAN: A Hybrid Semi-Supervised and Generative Approach for DDoS Detection in Cloud-Integrated IoT Networks
**(🎓 Accepted at ECAI 2025)**
MixGAN is a novel framework for network anomaly detection that combines Generative Adversarial Networks (GANs) with semi-supervised learning techniques. It employs a 1-D WideResNet backbone constructed with temporal convolutional layers and residual connections, which effectively captures local burst patterns in network traffic sequences. To address label scarcity and severe class imbalance issues, a pretrained CTGAN is utilized to generate synthetic traffic samples that simulate DDoS attack behaviors and complement unlabeled data. Additionally, a MixUp-Average-Sharpen (MAS) strategy is implemented to mitigate the effect of noisy pseudo-labels, constructing smoothed and sharpened targets by averaging predictions over augmented views and reweighting them towards high-confidence classes.

📄 Paper: [MixGAN: A Hybrid Semi-Supervised and Generative Approach for DDoS Detection in Cloud-Integrated IoT Networks](https://arxiv.org/abs/2508.19273)

### Key Features

- **Data Augmentation with GAN**: Utilizes CTGAN (Conditional Tabular GAN) to generate synthetic network traffic data
- **Semi-Supervised Learning**: Employs MixUp technique to combine labeled and unlabeled data
- **Regularization**: Implements techniques to prevent overfitting and improve model generalization
- **Network Anomaly Detection**: Focuses on effectively identifying various network attacks, including DDoS

### Architecture

The MixGAN framework consists of two main components:

1. **CTGAN Module**: Generates synthetic network traffic data that resembles real attack patterns
2. **MixUp-based Semi-Supervised Module**: Combines labeled and unlabeled data with predictions to improve model training

The backbone network is a WideResNet architecture adapted for network traffic data.

### Requirements

```
pip install -r requirements.txt
```

### How to Use

1. **Data Preparation**:
   
   - Place your network traffic dataset in CSV format
   - Configure the continuous and discrete columns in `gan_train.py`
   
2. **GAN Training**:
   ```bash
   python gan_train.py
   ```

3. **MixGAN Training and Detection**:
   ```bash
   # Use the trained model
   python MixGAN.py
   ```

### Project Structure

- `gan_train.py`: Implementation of CTGAN for synthetic data generation
- `MixGAN.py`: Main implementation of the MixGAN framework with the MixUp technique
- `backbone/WideResNet.py`: The backbone network architecture used for classification
- `requirements.txt`: Required Python packages

### Methodology

MixGAN employs the following key techniques:

1. **GAN-based Augmentation**: Generates realistic synthetic data samples for underrepresented attack classes
2. **MixUp Technique**: Creates virtual training samples by linearly combining input samples and their corresponding labels
3. **Semi-Supervised Learning**: Leverages unlabeled data to improve model performance
4. **Sharpening Function**: Reduces entropy in model predictions for unlabeled data

