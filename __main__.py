import pulumi
import pulumi_gcp as gcp
import pulumi_kubernetes as k8s
#from k8s import mixtral as mixtral

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

# Create a new network
#gke_network = gcp.compute.Network(
#    "gke-network",
#    auto_create_subnetworks=False,
#    description="A virtual network for your GKE cluster(s)"
#)

# Create a subnet in the new network
#gke_subnet = gcp.compute.Subnetwork(
#    "gke-subnet",
#    ip_cidr_range="10.128.0.0/12",
#    network=gke_network.id,
#    private_ip_google_access=True
#)

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
        #guest_accelerators=[gcp.container.ClusterNodeConfigGuestAcceleratorArgs(
        #    type="nvidia-tesla-k80",
        #    count=1,
        #)],
    ),
    node_pool_auto_config=gcp.container.ClusterNodePoolAutoscalingArgs(
        min_node_count=1,
        max_node_count=4,
    ),
)

# Obtain the kubeconfig from our GKE cluster.
#kubeconfig = gke_cluster.kube_config.apply(lambda config: config.raw_kubeconfig_output)

# Create a Kubernetes provider instance that uses our GKE cluster from above.
##k8s_provider = k8s.Provider("k8s_provider", kubeconfig=kubeconfig)

# Create a Kubernetes Service Account.
#ksa = k8s.core.v1.ServiceAccount("ksa", metadata={"namespace": "default"}, opts=pulumi.ResourceOptions(provider=k8s_provider))

# Create a Google Service Account.
#gsa = gcp.service_account.Account("gsa", account_id="my-gsa")

# Create a IAM policy binding between the Google Service Account and the Kubernetes Service Account.
#iam_binding = gcp.service_account.IAMBinding("iam_binding",
#  service_account_id=gsa.name,
#  role="roles/iam.workloadIdentityUser",
#  members=[pulumi.Output.all(gke_cluster.location, gke_cluster.name).apply(lambda lc: f"serviceAccount:{lc[0]}.svc.id.goog[default/{ksa.metadata['name']}]#")])

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
            #"nvidia-driver-installer": "https://us.download.nvidia.com/XFree86/Linux-x86_64/",
            #"nvidia-gpu-driver-version": "390.46",
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

#mixtral =  k8s.yaml.ConfigFile(
#    "mixtral",
#    depends_on=[gke_nodepool],
#    file="k8s/mixtral-huggingface.yaml",
#)

# Create a GCP service account for the nodepool
#gke_nodepool_sa = gcp.serviceaccount.Account(
#    "gke-nodepool-sa",
#    account_id=pulumi.Output.concat(gke_cluster.name, "-np-1-sa"),
#    display_name="Nodepool 1 Service Account",
#
#    depends_on=[gke_cluster]
#)


# Build a Kubeconfig to access the cluster


# Export some values for use elsewhere
#pulumi.export("networkName", gke_network.name)
#pulumi.export("networkId", gke_network.id)
#pulumi.export("clusterName", gke_cluster.name)
#pulumi.export("clusterId", gke_cluster.id)
#pulumi.export("kubeconfig", cluster_kubeconfig)
