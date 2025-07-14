# open-source-rat-behavior
Open source software for controlling operant conditioning chambers, running behavioral experiments, and collecting data. 

## Prerequisites
For specific version see `docs\Software Versions.xlsx`
- `Python` If using standalone [Python version](https://www.python.org/downloads/release/python-3810/), during installation check "Add python.exe to PATH"
- `Git` Can be downloaded from [here](https://git-scm.com/downloads/win)
- `Node.js` Can be downloaded from [here](https://nodejs.org/en/download). Do not check "Automatically install the necessary tools..."
- `Angular CLI`
    ```command
    >npm install -g @angular/cli@15.2.10
    >cd path\to\open-source-rat-behavior\Angular Files
    >ng add @angular/material
    ```

## Installation
1. Clone repository to your machine. 
2. Setup backend environment with `venv`
    - Choose or create a folder to store the environment
    - Open command terminal and run the following to create and activate the environment:
    ```command
    >cd path\to\open-source-rat-behavior\Flask Project Files\pythonBackend
    >python -m venv .venv
    >.venv\Scripts\activate.bat
    ```
    Note: While not necessary, it is best to have the environment folder in the `Flask Project Files\pythonBackend` directory and the environment named `.venv`

    - if the setup was successful, the command prompt will look like:
    ```command
    (.venv) C:\Users\...\open-source-rat-behavior>
    ```
    - (Optional) Upgrade pip and managing modules:
    ```command
    >python -m pip install --upgrade pip setuptools wheel
    ```
    - Install required modules in `requirements.txt` inside virtual environment:
    ```command
    >cd path\to\open-source-rat-behavior
    >pip install -r requirements.txt
    ```
    - To deactivate environment run:
    ```command
    >behavior-chamber-env\Scripts\deactivate.bat
    ```
    - Set name of Flask application (must be run on each usage unless `setx` is used):
    ```command
    >cd path\to\open-source-rat-behavior\Flask Project Files\pythonBackend
    >set FLASK_APP=application.py
    >set FLASK_DEBUG=true
    ```
3. Alternatively, setup backend environment with `conda`
    - In Anaconda Prompt:
    ```command
    >conda create -n behavior-chamber-env python=3.8
    >conda activate behavior-chamber-env
    >cd path\to\open-source-rat-behavior
    >pip install -r requirements.txt
    ```


## Launch Python Backend
1. Open command terminal.
2. Activate environment:
```command
>cd path\to\environment\folder
>behavior-chamber-env\Scripts\activate.bat
```
3. Navigate to the directory containing the file "application.py" and run app:
```command
>cd path\to\open-source-rat-behavior\Flask Project Files\pythonBackend
>flask run
```
Note: You don't need to open the URL (e.g. `http://127.0.0.1:5000`), but you can if you want


## Launch Angular App
1. Open a second command terminal.
2. Navigate to the diretory containing the folders "src", ".angular", etc. 
```command
>cd path\to\open-source-rat-behavior\Angular Files
```
3. Launch app:
```command
>ng serve --o
```
Note: The "--o" flag should open the application for you once it compiles. REMINDER THAT YOU NEED NODE.JS AND GIT INSTALLED, perhaps even Angular CLI.
You don't need Visual Studios unless you intend to modify code

## Launch Frontend and Backend with batch script
Instead of manually opening two terminals to start the app, two batch files are available to launch the frontend and backend automatically

1. `start-full.bat`
    - Run if the Python environment was setup with `venv`
    - Assumes the virtual environment is named `.venv` and is located in:
        `\Flask Project Files\pythonBackend\.venv`
    - If this is not the case update the following in the script:
        - `ENV_NAME`
        - `ENV_DIR`

2. `start-full-conda.bat`
    - Run if the Python environment was setup with `conda`
    - Assumes name of environment is `behavior-chamber-env` and Anaconda installation is `%USERPROFILE%\anaconda3\condabin\`
    - If this is not the case update the following in the script:
        - `ENV_NAME`
        - `ENV_DIR`