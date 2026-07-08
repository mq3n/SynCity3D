# SynCity3D - CityEngine Project





## Project Structure

Project consists of 



## Python Environment Setup

This project uses a Conda environment for Python development in VS Code.

### Prerequisites

- Anaconda or Miniconda installed
- Visual Studio Code with Python extension
- ESRI CityEngine 2025.1+

### Creating the Conda Environment - Creating Dataset

1. **Create a new conda environment** with Python 3.11:
   ```bash
   conda create -n SynCity3D python=3.11
   ```

2. **Activate the environment**:
   ```bash
   conda activate SynCity3D
   ```

3. **Install required packages**:
   ```bash
   pip install cityengine==0.5.1+ce2025111669
   pip install py4j==0.10.9.9
   ```

### Verifying the Environment

Check that the environment is properly configured:

```bash
# List all conda environments
conda info --envs

# Verify Python version
python --version
# Should output: Python 3.11.14

# List installed packages
conda list
```

### Using the Environment in VS Code

1. **Open VS Code** in the project directory
2. **Select the Python interpreter**:
   - Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
   - Type "Python: Select Interpreter"
   - Choose the `SynCity3D` environment from the list
   - Path should be: `E:\anaconda3\envs\SynCity3D\python.exe`

3. **Verify in the terminal**:
   - Open a new terminal in VS Code (`Ctrl+Shift+``)
   - The terminal should show `(SynCity3D)` prefix
   - Run your scripts: `python scripts/main_routine.py`

### Current Environment Details

**Environment Name:** `SynCity3D`  
**Python Version:** 3.11.14  

**Key Dependencies:**
- cityengine 0.5.1+ce2025111669
- py4j 0.10.9.9




### Troubleshooting

- If the environment doesn't activate automatically in VS Code, reload the window or restart VS Code
- Make sure the Python extension is installed in VS Code
- If conda commands don't work, ensure Anaconda/Miniconda is in your system PATH
- For additional Python setup guidance, refer to the [ArcGIS CityEngine Python documentation](https://doc.arcgis.com/en/cityengine/latest/python/python-working-with-python-3.htm)
