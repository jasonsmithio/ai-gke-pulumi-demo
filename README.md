# AI on GKE using Pulumi Demo

Start
## Some Basics

```bash
pulumi stack init dev
```

### Settings some variables

```bash
pulumi config set gcp:project [your-gcp-project-here] 
pulumi config set gcp:zone us-west1-a 
pulumi config set password --secret [your-cluster-password-here] 
pulumi config set master_version
pulumi config set node_count 5
pulumi config set node_machine_type n2d-standard-4
```