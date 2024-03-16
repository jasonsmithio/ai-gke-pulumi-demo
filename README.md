# AI on GKE using Pulumi Demo

Start
## Some Basics

```bash
pulumi stack init dev
```

### Settings some variables

```bash
pulumi config set gcp:project [your-gcp-project-here] 

pulumi config set gcp:region us-central1
pulumi config set gcp:zone us-central1-a 
pulumi config set gcp:gkeNetwork gke-main
pulumi config set password --secret [your-cluster-password-here] 
pulumi config set gcp:clusterName [cluster-name]
pulumi config set gcp:master_version 1.27
pulumi config set gcp:node_count 5
pulumi config set gcp:node_machine_type n2d-standard-4
```