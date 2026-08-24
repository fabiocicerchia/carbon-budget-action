#!/bin/sh
# Devtron — carbon budget gate as a Pre-Deployment task.
#
# Paste this into a task of type "Execute custom script" / Shell on the
# Pre-Deployment stage of the CD pipeline (App -> Workflow -> Pre-Deployment
# stage -> Add task). A non-zero exit fails the stage, so the deployment never
# happens. Put it on Pre-Build instead if you want the gate at CI time.
#
# The four numbers below are the whole model. Either hardcode them here, or
# declare them as Input Variables on the task and delete the defaults — the
# script reads whatever is already in the environment.
set -eu

export BUDGET_GCO2E="${BUDGET_GCO2E:-5000}"
export GRID_INTENSITY="${GRID_INTENSITY:-480}" # world average; 56 = eu-north-1
export HOURS="${HOURS:-720}"                   # 30d — the window the budget covers

# Devtron deploys a Helm chart, so the replica count and the resource requests
# are already declared in the app's values. Point MANIFEST_PATH at a rendered
# Deployment and the estimator reads replicas/cpu/memory from it instead of
# being told them twice:
#   helm template ./chart -f values.yaml > /tmp/rendered.yaml
#   export MANIFEST_PATH=/tmp/rendered.yaml
export REPLICAS="${REPLICAS:-4}"
export CPU_REQUEST="${CPU_REQUEST:-500m}"
export MEMORY_REQUEST="${MEMORY_REQUEST:-1Gi}"

curl -fsSL -o /tmp/carbon_budget.py \
  https://raw.githubusercontent.com/fabiocicerchia/carbon-budget-action/v0.2.0/carbon_budget.py

# Exit 1 over budget in gate mode — that is the whole gate.
python3 /tmp/carbon_budget.py
