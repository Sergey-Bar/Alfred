#!/bin/bash

# Script to configure autoscaling policies for Kubernetes deployments

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null
then
    echo "kubectl not found. Please install kubectl to proceed."
    exit 1
fi

# Define the deployment name and namespace
DEPLOYMENT_NAME="my-app"
NAMESPACE="default"

# Apply Horizontal Pod Autoscaler (HPA)
echo "Applying Horizontal Pod Autoscaler..."
kubectl autoscale deployment $DEPLOYMENT_NAME \
    --cpu-percent=50 \
    --min=2 \
    --max=10 \
    --namespace=$NAMESPACE

echo "Horizontal Pod Autoscaler applied."

# Apply Cluster Autoscaler (if using a cloud provider)
echo "Configuring Cluster Autoscaler..."
cat <<EOL | kubectl apply -f -
apiVersion: autoscaling/v1
kind: ClusterAutoscaler
metadata:
  name: cluster-autoscaler
  namespace: kube-system
spec:
  scaleDown:
    enabled: true
    delayAfterAdd: 10m
    delayAfterDelete: 1m
    delayAfterFailure: 3m
EOL

echo "Cluster Autoscaler configured."

echo "Autoscaling setup complete."