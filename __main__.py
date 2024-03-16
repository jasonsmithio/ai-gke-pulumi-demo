import pulumi
import pulumi_gcp as gcp

# Get some provider-namespaced configuration values
config = pulumi.Config()
gcp_project = config.get("projects")
gcp_region = config.get("region", "us-central1")
gcp_zone = config.get("zone", "us-central1-a")
gke_network = config.get("gkeNetwork", "default")
gke_cluster_name = config.get("clusterName", "mixtral-cluster")
gke_master_version =config.get("master_version", 1.27)
gke_master_node_count = config.get_int("nodesPerZone", 1)

#setting unique values for the nodepool
gke_nodepool_name = config.get("nodepoolName", "mixtral-nodepool")
gke_nodepool_node_count = config.get_int("nodesPerZone", 1)
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
    location = gcp_region,
    network = gke_network,
    initial_node_count = gke_master_node_count,
    remove_default_node_pool = True,
    min_master_version = gke_master_version,
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
        guest_accelerators=[gcp.compute.InstanceGuestAcceleratorArgs(
            type="nvidia-l4",
            count=2,
        )],
        metadata = {
            "install-nvidia-driver": "True"
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
        max_node_count = 3
    ),
    # Set the Nodepool Management configuration
    management = gcp.container.NodePoolManagementArgs(
        auto_repair  = True,
        auto_upgrade = True
    )
)

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
