#!/bin/bash

# Variables
resourceGroup="indightd7845"
clusterName="udacity-cluster"


echo "AKS CLI installed"

# Create AKS cluster
echo "Step 1 - Creating AKS cluster $clusterName"


# For Cloud Lab users
az aks create \
--resource-group $resourceGroup \
--name $clusterName \
--node-count 1 \
--generate-ssh-keys \
--attach-acr insightacr001 \
--zones 1

# For Cloud Lab users
# This command will is a substitute for "--enable-addons monitoring" option in the "az aks create"
# Use the log analytics workspace - Resource ID
# For Cloud Lab users, go to the existing Log Analytics workspace --> Properties --> Resource ID. Copy it and use in the command below.
az aks enable-addons -a monitoring -n $clusterName -g $resourceGroup --workspace-resource-id "/subscriptions/{subscription-id}/resourcegroups/defaultresourcegroup-wus2/providers/microsoft.operationalinsights/workspaces/defaultworkspace-{subscription-id}-wus2"

echo "AKS cluster created: $clusterName"

# Connect to AKS cluster

echo "Step 2 - Getting AKS credentials"

az aks get-credentials \
--resource-group $resourceGroup \
--name $clusterName \
--verbose

echo "Verifying connection to $clusterName"

kubectl get nodes

# echo "Deploying to AKS cluster"
# The command below will deploy a standard application to your AKS cluster.
# kubectl apply -f azure-vote.yaml
