import pulumi
import pulumi_gcp as gcp
import pulumi_kubernetes as kubernetes
from k8s.mixtral import Mixtral as mixtral

# Get some provider-namespaced configuration values
config = pulumi.Config()
gcp_project = config.get("project")
gcp_region = config.get("region", "us-central1")
gcp_zone = config.get("zone", "us-central1-a")
gke_network = config.get("gkeNetwork", "default")
gke_cluster_name = config.get("clusterName", "mixtral-cluster")
gke_master_version =config.get("master_version", 1.27)
gke_master_node_count = config.get_int("nodesPerZone", 1)

#setting unique values for the nodepool
gke_nodepool_name = config.get("nodepoolName", "mixtral-nodepool")
gke_nodepool_node_count = config.get_int("nodesPerZone", 2)
gke_ml_machine_type = config.get("mlMachines", "g2-standard-24")

# Create a cluster in the new network and subnet
gke_cluster = gcp.container.Cluster("cluster-1", 
    name = gke_cluster_name,
    deletion_protection=False,
    location = gcp_region,
    network = gke_network,
    networking_mode="VPC_NATIVE",
    initial_node_count = gke_master_node_count,
    remove_default_node_pool = True,
    min_master_version = gke_master_version,
    workload_identity_config=gcp.container.ClusterWorkloadIdentityConfigArgs(
        workload_pool=str(gcp_project)+".svc.id.goog",
    ),
    addons_config=gcp.container.ClusterAddonsConfigArgs(
        gcs_fuse_csi_driver_config={
            "enabled": "True",
        }, 
    ),
    node_config=gcp.container.ClusterNodeConfigArgs(
        oauth_scopes=["https://www.googleapis.com/auth/cloud-platform"],
        shielded_instance_config={
            "enable_secure_boot" : "True",
            "enable_integrity_monitoring": "True",
        },
    ),
)

# Defining the GKE Node Pool
gke_nodepool = gcp.container.NodePool("nodepool-1",
    name = gke_nodepool_name,
    location = gcp_region,
    node_locations = [gcp_zone],
    cluster = gke_cluster.id,
    node_count = gke_nodepool_node_count,
    node_config = gcp.container.NodePoolNodeConfigArgs(
        preemptible = False,
        machine_type = gke_ml_machine_type,
        disk_size_gb = 20,
        ephemeral_storage_local_ssd_config={
            "local_ssd_count":"2",
        },
        guest_accelerators=[gcp.container.NodePoolNodeConfigGuestAcceleratorArgs(
            type="nvidia-l4",
            count=2,
            gpu_driver_installation_config={
                "gpu_driver_version" : "LATEST",
            },
        )],
        metadata = {
            "install-nvidia-driver": "True",
        },
        oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"],
        shielded_instance_config = gcp.container.NodePoolNodeConfigShieldedInstanceConfigArgs(
            enable_integrity_monitoring = True,
            enable_secure_boot = True
        )
    ),
    # Set the Nodepool Autoscaling configuration
    autoscaling = gcp.container.NodePoolAutoscalingArgs(
        min_node_count = 1,
        max_node_count = 2
    ),
    # Set the Nodepool Management configuration
    management = gcp.container.NodePoolManagementArgs(
        auto_repair  = True,
        auto_upgrade = True
    )
)

# Manufacture a GKE-style Kubeconfig. Note that this is slightly "different" because of the way GKE requires
# gcloud to be in the picture for cluster authentication (rather than using the client cert/key directly).
k8s_info = pulumi.Output.all(gke_cluster.name, gke_cluster.endpoint, gke_cluster.master_auth)
k8s_config = k8s_info.apply(
    lambda info: """apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: {0}
    server: https://{1}
  name: {2}
contexts:
- context:
    cluster: {2}
    user: {2}
  name: {2}
current-context: {2}
kind: Config
preferences: {{}}
users:
- name: {2}
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1beta1
      command: gke-gcloud-auth-plugin
      installHint: Install gke-gcloud-auth-plugin for use with kubectl by following
        https://cloud.google.com/blog/products/containers-kubernetes/kubectl-auth-changes-in-gke
      provideClusterInfo: true
""".format(info[2]['cluster_ca_certificate'], info[1], '{0}_{1}_{2}'.format(gcp_project, gcp_zone, info[0])))

# Make a Kubernetes provider instance that uses our cluster from above.
kubeconfig = kubernetes.Provider('gke_k8s', kubeconfig=k8s_config, opts=pulumi.ResourceOptions(depends_on=[gke_nodepool]))

# Create a GCP service account for the nodepool
#gke_nodepool_sa = gcp.serviceaccount.Account(
#    "gke-nodepool-sa",
#    account_id=pulumi.Output.concat(gke_cluster.name, "-np-1-sa"),
#    display_name="Nodepool 1 Service Account",
#
#    depends_on=[gke_cluster]
#)

#mixtral =  kubernetes.yaml.ConfigFile(
#    "mixtral",
#    file="k8s/mixtral-huggingface.yaml",
#    opts=pulumi.ResourceOptions(provider=kubeconfig,depends_on=[gke_nodepool]),
#)

deploy = mixtral(kubeconfig)

service = deploy.mixtralService()
deployment = deploy.mixtral8x7b()

# Export the Service's IP address
service_ip = service.status.apply(
    lambda status: status.load_balancer.ingress[0].ip if status.load_balancer.ingress else None
)

pulumi.export('service_ip', service_ip)
pulumi.export("clusterName", gke_cluster.name)
pulumi.export("clusterId", gke_cluster.id)