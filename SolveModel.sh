#!/bin/bash

reconversion="False"
vector="LH2"
grid_connection="False"

key='SampleModel'

python ExecutionScripts/BuildModel.py "$reconversion" "$vector" "$grid_connection" "$key"
python ExecutionScripts/SolveModel.py "$key" 
