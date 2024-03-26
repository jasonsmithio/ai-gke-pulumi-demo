# AI on GKE using Pulumi Demo

This is a very basic tutorial on how to get started with GCP on Cloud. This is based on another tutorial I made with regards to [AI on GKE](https://github.com/jasonsmithio/ai-on-gke/tree/main/mixtral-on-gke).

## Some Pre-requesites 

### Some Environment Variables

Before we get started, we will set a few basic environment variables in our terminal. This will make things easier for us as we move forward. Copy and paste the below snippet into your terminal. Be sure to set your `PROJECT_ID` and `NETWORK`. You may be able to set the network to *default* as there is usually a default network in a brand new environment.  

```bash
export PROJECT_ID=<your-project-id>
export REGION=<your region>
export ZONE=${REGION}-a 
export CLUSTER_NAME=mixtral-cluster
export NETWORK=<your network>
```

### Configuring the Google Cloud Platform (GCP) environment

Now that the variables are set, let's make sure that your GCP environment is setup and that you are authenticated. 

```bash
gcloud auth login 
gcloud config set project $PROJECT_ID 
gcloud config set compute/region $REGION
gcloud config set compute/zone $ZONE
gcloud auth application-default login
```

Now that we are authenticated, let's enable some APIs. Every resource in Google Cloud has an API that needs to be enabled. By default, new projects have all APIs turned off so if you are just getting started, it's important to turn them on. You only need to do this once. 

```bash
gcloud services enable \
	  cloudresourcemanager.googleapis.com \
	  compute.googleapis.com \
	  container.googleapis.com \
	  cloudbuild.googleapis.com \
	  containerregistry.googleapis.com
```

And finally, we'll do some IAM binding. In short, this will give our Kubernetes cluster the ability to write logs. 

```bash
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
GCE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
--member=serviceAccount:${GCE_SA} --role=roles/monitoring.metricWriter
gcloud projects add-iam-policy-binding $PROJECT_ID \
--member=serviceAccount:${GCE_SA} --role=roles/stackdriver.resourceMetadata.writer
```
This CAN be configured in Pulumi but for the purposes of this demo, we will set it in terminal. 



### Clone Demo Code from GitHub

In whatever directory you want to execute this code, run the below command in the terminal. It will pull down this GitHub repo and place you in the folder

```bash
git clone https://github.com/jasonsmithio/ai-gke-pulumi-demo
cd ai-gke-pulumi-demo
```

### Staging Pulumi Environment

The first thing we need to do is setup a Pulumi Stack

```bash
pulumi stack init
```

### Settings some variables

In our Python demo, we will be standing up a GKE Cluster. Pulumi allows us to [configur](https://www.pulumi.com/docs/concepts/config/) environment variables in a `Pulumi.<env>.yaml` file. While you can manually build the file, you can also just execute the commands below.

```bash
pulumi config set gcp:project $PROJECT_ID
pulumi config set gcp:projectNumber $PROJECT_NUMBER
pulumi config set gcp:gceSA $GCE_SA  
pulumi config set gcp:region $REGION
pulumi config set gcp:zone $ZONE
pulumi config set gcp:gkeNetwork $NETWORK
pulumi config set gcp:clusterName mixtral-gke-cluster
pulumi config set gcp:master_version 1.27
pulumi config set gcp:node_count 5
pulumi config set gcp:node_machine_type n2d-standard-4
```

Notice how we are using some of the variables we set earlier.


## Standing Up Our Pulumi Environment

We will execute Pulumi.

```bash
pulumi up
```