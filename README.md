# Final-Project

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

## 🚀 How to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/ajaysanthoshk/Final-Project.git
   cd Final-Project
   
