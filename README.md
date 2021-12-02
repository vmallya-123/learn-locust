# learn-locust

This repo contains examples to perform load testing both in a distributed and non distributed manner  

## Example webapp
There is an example web app which you can use to test.  

You can also deploy it locally by running

```
#setup virtual environment  
python3 -m venv myvenv  
source myvenv activate  
#install requirements  
pip install -r webapp/requirements.txt  
#start fast api  
```
You can deploy it on k8s (for distributed load testing) by running

```
kustomize build webapp/k8s | kubectl apply -f -

```

## Single Machine Load Testing  
To run this on local you can run

```
#install requirements  
pip install -r simple/requirements.txt 
locust -f simple/locustfile.py 
```

## Distributed Load Testing
To Deploy locust on k8s to test out distributed load testing run

```
kustomize build distributed/k8s | kubectl apply -f -

```

