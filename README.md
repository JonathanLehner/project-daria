# Project Daria

## Installation Instructions

### Step 1: Create a Conda Environment
1. Open a terminal or command prompt.
2. Run the following command to create a new Conda environment:
    ```bash
    conda create -n project-daria python=3.10
    ```
3. Activate the environment:
    ```bash
    conda activate project-daria
    ```

### Step 2: Install Required Packages
Install the necessary Python packages from the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

## Running the Project
To run the project, ensure you are in the Conda environment created in Step 1. 
Then:
- Start the SlimeVR application and ensure your SlimeVR device is connected.
- Start the slimeVR data capture script:
```bash
python capture_data_slimeVR.py
```

---

## Deleting the Conda Environment
If you need to remove the Conda environment, follow these steps:
1. Deactivate the environment (if active):
    ```bash
    conda deactivate
    ```
2. Delete the environment:
    ```bash
    conda remove -n project-daria --all
    ```