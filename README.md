# open-source-operant-chamber-control
Open source software for controlling operant conditioning chambers, running behavioral experiments, and collecting data. 

## Prerequisites
For specific version see `docs\Software Versions.xlsx`
- `Python` If using standalone Python version, during installation check "Add python.exe to PATH"
- `Git`
- `Node.js` Do not check "Automatically install the necessary tools..."
- `Angular CLI`
    ```command
    >npm install -g @angular/cli@15.2.10
    >cd path\to\open-source-operant-chamber-control\Angular Files
    >ng add @angular/material
    ```

## Installation
1. Clone repository to your machine. 
2. Setup backend environment with `venv`
    - Choose or create a folder to store the environment
    - Open command terminal and run the following to create and activate the environment:
    ```command
    >cd path\to\environment\folder
    >python -m venv behavior-chamber-env
    >behavior-chamber-env\Scripts\activate.bat
    ```
    - Install required modules in `requirements.txt` inside virtual environment:
    ```command
    >cd path\to\open-source-operant-chamber-control
    >pip install -r requirements.txt
    ```
    - To deactivate environment run:
    ```command
    >behavior-chamber-env\Scripts\deactivate.bat
    ```
    - Set name of Flask application (must be run on each usage unless `setx` is used):
    ```command
    >cd path\to\open-source-operant-chamber-control\Flask Project Files\pythonBackend
    >set FLASK_APP=application.py
    >set FLASK_ENV=development
    ```

## Launch Python Backend
1. Open command terminal.
2. Activate environment:
```command
>cd cd path\to\environment\folder
>behavior-chamber-env\Scripts\activate.bat
```
3. Navigate to the directory containing the file "application.py" and run app:
```command
>cd path\to\open-source-operant-chamber-control\Flask Project Files\pythonBackend
>flask run
```
Note: You don't need to open the URL (e.g. `http://127.0.0.1:5000`), but you can if you want


## Launch Angular App
1. Open a second command terminal.
2. Navigate to the diretory containing the folders "src", ".angular", etc. 
```command
>cd path\to\open-source-operant-chamber-control\Angular Files
```
3. Launch app:
```command
>ng serve --o
```
Note: The "--o" flag should open the application for you once it compiles. REMINDER THAT YOU NEED NODE.JS AND GIT INSTALLED, perhaps even Angular CLI.
You don't need Visual Studios unless you intend to modify code 
