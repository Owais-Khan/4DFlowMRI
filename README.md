# 4DFlowMRI
This repository can be used to work with 4D flow MRI acquisitions for CFD applications. <br/>

Cite the code: [![DOI](https://zenodo.org/badge/295950364.svg)](https://zenodo.org/badge/latestdoi/295950364) <br/>

### Features
The main provided functionalities enable to: 
- read 4D flow dicom files and generate .vtk files that can be visualized in Paraview;
- extract velocity profiles from 4D flow and map them to the inlet of a target model;
- write boundary conditions files for multiple CFD software, including Fluent, CFX, Star-CCM+, OpenFoam, SimVascular

### Installation
To run the scripts you need a python interpreter. The use of a conda environment is 
strongly recommended. 

### Dependencies
- [vmtk](https://github.com/conda-forge/vmtk-feedstock) (optional, only required for centerline extraction)
- pydicom
- pyvista


## Scripts

## FlowMRI_MatlabToVTK
**Description:** This script with convert 4D Flow MRI volume stored in matlab format into vtk format. Currently, the matlab file is expected to have an array "PCMR" that should have the data stored in the following format [X Y Z T Mag U V W].
**Code:**
```python FlowMRI_MatlabToVTK.py -InputFileName [MatlabData.mat]```
**Optional arguments:**
* ```--OutputFolder```: Folder to store the output .vtk images. Default=Stores to the same folder as input file.
* ```--FileFormat```: Supports .vti and .nii.gz files. Default=".vti"
* ```--ReflectionPlane```: You can reflect the output image about X Y Z planes. Options include XMin YMin ZMin XMax YMax ZMax. Default=None


## Read and process 4D flow dicom files
```
python dicoms_to_vtk.py
```

## Interactive plane selection and velocity profile extraction
```
python plane_selection.py
```

## Map precomputed velocity profiles to a target inlet shape
```
python mapping.py
```
