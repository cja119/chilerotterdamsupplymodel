# Chile-Rotterdam Supply Chain Model
Open Source Model for a Hydrogen Supply Chain from Chile to Rotterdam

## Dependancies
In order to run this model, a licence for gurobi is required, as is an installation of conda. 

## Quick Start
To quick start this, clone the repository and run the following bash command to set up the conda environment:

```
conda env create -f MIPSupplyChain.yml
```

Then activate the environment using the following:

```
source activate MIPSupplyChain
```
To run the sample formulation, execute the bash script as follows

```
bash SolveModel.sh
```
