# OLLAMA MODEL EDITOR

**A powerful tool for customizing and optimizing Ollama AI models**

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Documentation](#documentation) • [Contributing](#contributing) • [License](#license)

## About

Ollama Model Editor is a comprehensive GUI application that allows you to customize, optimize, and manage your Ollama AI models. This tool provides an intuitive interface for adjusting model parameters, comparing performance across different configurations, and streamlining your AI workflow.

**This project is a collaboration between human developers and AI assistants, demonstrating the power of human-AI teamwork in software development.**

## Features

- 🎛️ **Parameter Customization**: Fine-tune model parameters through an intuitive GUI
- 📊 **Performance Benchmarking**: Compare different model configurations side-by-side
- 🔄 **Model Management**: Easily manage multiple Ollama models in one interface
- 🎯 **Optimization Presets**: Apply pre-configured optimization settings for specific use cases
- 📝 **Detailed Analysis**: Get insights into how parameter changes affect model performance
- 🌓 **Theming Support**: Choose between light and dark themes for comfortable usage
- 💾 **Configuration Export**: Share your optimized model configurations with others

## Installation

### Prerequisites

- Python 3.8 or higher
- Ollama installed and running on your system
- Git (for cloning the repository)

### Setup

Collecting PySide6>=6.5.0 (from -r requirements.txt (line 1))
  Using cached PySide6-6.8.2.1-cp39-abi3-manylinux_2_28_x86_64.whl.metadata (5.3 kB)
Collecting pytest>=7.3.1 (from -r requirements.txt (line 2))
  Using cached pytest-8.3.5-py3-none-any.whl.metadata (7.6 kB)
Collecting pytest-qt>=4.2.0 (from -r requirements.txt (line 3))
  Using cached pytest_qt-4.4.0-py3-none-any.whl.metadata (7.7 kB)
Collecting requests>=2.28.2 (from -r requirements.txt (line 4))
  Using cached requests-2.32.3-py3-none-any.whl.metadata (4.6 kB)
Collecting pyyaml>=6.0 (from -r requirements.txt (line 5))
  Using cached PyYAML-6.0.2-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (2.1 kB)
Collecting loguru>=0.7.0 (from -r requirements.txt (line 6))
  Using cached loguru-0.7.3-py3-none-any.whl.metadata (22 kB)
Collecting shiboken6==6.8.2.1 (from PySide6>=6.5.0->-r requirements.txt (line 1))
  Using cached shiboken6-6.8.2.1-cp39-abi3-manylinux_2_28_x86_64.whl.metadata (2.5 kB)
Collecting PySide6-Essentials==6.8.2.1 (from PySide6>=6.5.0->-r requirements.txt (line 1))
  Using cached PySide6_Essentials-6.8.2.1-cp39-abi3-manylinux_2_28_x86_64.whl.metadata (3.7 kB)
Collecting PySide6-Addons==6.8.2.1 (from PySide6>=6.5.0->-r requirements.txt (line 1))
  Using cached PySide6_Addons-6.8.2.1-cp39-abi3-manylinux_2_28_x86_64.whl.metadata (4.0 kB)
Collecting iniconfig (from pytest>=7.3.1->-r requirements.txt (line 2))
  Using cached iniconfig-2.0.0-py3-none-any.whl.metadata (2.6 kB)
Collecting packaging (from pytest>=7.3.1->-r requirements.txt (line 2))
  Using cached packaging-24.2-py3-none-any.whl.metadata (3.2 kB)
Collecting pluggy<2,>=1.5 (from pytest>=7.3.1->-r requirements.txt (line 2))
  Using cached pluggy-1.5.0-py3-none-any.whl.metadata (4.8 kB)
Collecting charset-normalizer<4,>=2 (from requests>=2.28.2->-r requirements.txt (line 4))
  Using cached charset_normalizer-3.4.1-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (35 kB)
Collecting idna<4,>=2.5 (from requests>=2.28.2->-r requirements.txt (line 4))
  Using cached idna-3.10-py3-none-any.whl.metadata (10 kB)
Collecting urllib3<3,>=1.21.1 (from requests>=2.28.2->-r requirements.txt (line 4))
  Using cached urllib3-2.3.0-py3-none-any.whl.metadata (6.5 kB)
Collecting certifi>=2017.4.17 (from requests>=2.28.2->-r requirements.txt (line 4))
  Using cached certifi-2025.1.31-py3-none-any.whl.metadata (2.5 kB)
Using cached PySide6-6.8.2.1-cp39-abi3-manylinux_2_28_x86_64.whl (550 kB)
Using cached PySide6_Addons-6.8.2.1-cp39-abi3-manylinux_2_28_x86_64.whl (160.6 MB)
Using cached PySide6_Essentials-6.8.2.1-cp39-abi3-manylinux_2_28_x86_64.whl (95.3 MB)
Using cached shiboken6-6.8.2.1-cp39-abi3-manylinux_2_28_x86_64.whl (204 kB)
Using cached pytest-8.3.5-py3-none-any.whl (343 kB)
Using cached pytest_qt-4.4.0-py3-none-any.whl (36 kB)
Using cached requests-2.32.3-py3-none-any.whl (64 kB)
Using cached PyYAML-6.0.2-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (767 kB)
Using cached loguru-0.7.3-py3-none-any.whl (61 kB)
Using cached certifi-2025.1.31-py3-none-any.whl (166 kB)
Using cached charset_normalizer-3.4.1-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (145 kB)
Using cached idna-3.10-py3-none-any.whl (70 kB)
Using cached pluggy-1.5.0-py3-none-any.whl (20 kB)
Using cached urllib3-2.3.0-py3-none-any.whl (128 kB)
Using cached iniconfig-2.0.0-py3-none-any.whl (5.9 kB)
Using cached packaging-24.2-py3-none-any.whl (65 kB)
Installing collected packages: urllib3, shiboken6, pyyaml, pluggy, packaging, loguru, iniconfig, idna, charset-normalizer, certifi, requests, pytest, PySide6-Essentials, pytest-qt, PySide6-Addons, PySide6
Successfully installed PySide6-6.8.2.1 PySide6-Addons-6.8.2.1 PySide6-Essentials-6.8.2.1 certifi-2025.1.31 charset-normalizer-3.4.1 idna-3.10 iniconfig-2.0.0 loguru-0.7.3 packaging-24.2 pluggy-1.5.0 pytest-8.3.5 pytest-qt-4.4.0 pyyaml-6.0.2 requests-2.32.3 shiboken6-6.8.2.1 urllib3-2.3.0

## Usage

1. Launch the application with **python Main.py**
2. Select an Ollama model from the dropdown menu
3. Adjust parameters using the intuitive interface
4. Compare performance with different settings
5. Save your optimized configuration
6. Export settings to share with the community

For more detailed instructions, see the [Quick Start Guide](docs/QuickStartGuide.md).

## Documentation

- [Quick Start Guide](docs/QuickStartGuide.md)
- [Core Components](Core/README.md)
- [Parameter Reference](docs/parameters.md)
- [Advanced Usage](docs/advanced_usage.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (**git checkout -b feature/amazing-feature**)
3. Commit your changes (**git commit -m 'Add some amazing feature'**)
4. Push to the branch (**git push origin feature/amazing-feature**)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- This project is a collaboration between human developers and AI assistants
- Special thanks to the Ollama project for making powerful AI models accessible
- Developed by Herbert J. Bowers (Herb@BowersWorld.com)
