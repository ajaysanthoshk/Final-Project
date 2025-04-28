# Final-Project
# Stock Market Analysis with Deep Learning Models

![GitHub last commit](https://img.shields.io/github/last-commit/ajaysanthoshk/Final-Project)
![GitHub repo size](https://img.shields.io/github/repo-size/ajaysanthoshk/Final-Project)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)

## 📝 Project Overview
This repository contains my MSc Data Science final project (7PAM2002) from the University of Hertfordshire, comparing the performance of LSTM, GRU, and CNN models for S&P 500 stock price prediction using over 619,000 daily observations from 2013-2018.

**Key Features:**
- Comparative analysis of three deep learning architectures
- Extensive feature engineering with technical indicators (RSI, moving averages)
- Comprehensive exploratory data analysis (EDA)
- Model performance evaluation with multiple metrics
- Complete implementation in Python using TensorFlow/Keras

## 📊 Key Results
The GRU model outperformed both LSTM and CNN architectures across all evaluation metrics:

| Model    | MSE     | RMSE   | MAE    | R² Score | Training Time |
|----------|---------|--------|--------|----------|---------------|
| **GRU**  | 15.1552 | 3.8930 | 2.8725 | 0.9927   | 38 min        |
| LSTM     | 21.4166 | 4.6278 | 3.7775 | 0.9897   | 52 min        |
| CNN      | 34.7146 | 5.8919 | 4.3117 | 0.9834   | 29 min        |

## 🛠️ Technical Implementation
### Data
- **Source**: Yahoo Finance (via Kaggle)
- **Time Period**: 2013-2018
- **Features**: Open, High, Low, Close prices, Volume + technical indicators (RSI, MA7, MA30, Volatility)
- **Size**: 619,000+ daily observations

### Models
1. **LSTM Architecture**:
   - 2 stacked LSTM layers (50 → 25 units)
   - Dropout (0.2) for regularization
   - ReLU activation + Adam optimizer (lr=0.001)

2. **GRU Architecture**:
   - 2 stacked GRU layers (50 → 25 units)
   - Same hyperparameters as LSTM for fair comparison

3. **CNN Architecture**:
   - 1D Convolutional layer (64 filters, kernel_size=3)
   - Flatten + Dense layers
   - Same optimizer and learning rate

### Tools
- Python 3.8+
- TensorFlow 2.10/Keras
- Pandas, NumPy for data processing
- Matplotlib, Seaborn, Plotly for visualization
- Google Colab with GPU acceleration

 📚 References
Complete literature review with 30+ academic references included in the full report. Key references:

Moghar & Hamiche (2020) on LSTM for stock prediction

Rahman et al. (2019) on GRU advantages

Chicco et al. (2021) on evaluation metrics

👨‍💻 Author
Ajay Santhosh K V

MSc Data Science, University of Hertfordshire

Student ID: 23024049


Supervisor: William Cooper
