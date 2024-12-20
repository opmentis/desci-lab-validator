# Decentralized Scientific Discovery Lab (Validator)
DeSci Lab: Engage in groundbreaking protein folding research and advance scientific breakthroughs.
Validator is a component of the OpMentis decentralized protein structure prediction network. It validates protein structure predictions made by miners by running its own predictions and comparing the results.

## Features

- Validates miner predictions by comparing structures and confidence metrics
- Supports both CPU and GPU execution
- Automatic download of required model parameters
- Robust error handling and logging

## Requirements

- 20,000 $OPM tokens
- Python 3.8+
- CUDA-compatible GPU (recommended)
- 16GB+ RAM
- 30GB+ disk space for model parameters

## Installation
1. Clone the repository:
```bash
git clone https://github.com/opmentis/desci-lab-validator.git
cd desci-lab-validator
```

2. Install dependencies:
```bash 
chmod +x install.sh 
./install.sh
```

3. Initialize Conda:
```bash
export PATH="$(pwd)/miniconda3/bin:$PATH"
conda init
conda activate
```

4. Configure .env file:
```bash
nano .env
```
#### Configuration

The validator can be configured through environment variables or .env file:

- `WALLET_ADDRESS`: Your validator wallet address
- `USE_GPU`: Whether to use GPU acceleration (true/false)
- `TF_FORCE_UNIFIED_MEMORY`: GPU memory setting (default: 1)
- `XLA_PYTHON_CLIENT_MEM_FRACTION`: GPU memory fraction (default: 4.0)

5. Run the validator:
```bash
python validator.py --wallet YOUR_WALLET_ADDRESS
```
The validator will:
1. Download required AlphaFold parameters on first run
2. Connect to the OpMentis network
3. Get pending validation tasks
4. Run AlphaFold predictions
5. Compare results with miner predictions
6. Submit validation results
7. Receive rewards for successful validations

## Architecture

The validator consists of several key components:

- `ValidatorService`: Main service orchestrating the validation process
- `ModelService`: Handles AlphaFold model predictions
- `RelaxationService`: Performs structure refinement
- `ConfidenceService`: Calculates confidence metrics

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on GitHub or contact the OpMentis team.
