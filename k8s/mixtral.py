import pulumi
import pulumi_kubernetes as kubernetes

class Mixtral:

    def __init__(self, provider):
        self.provider = provider

    def mixtral8x7b(self):
        deployment = kubernetes.apps.v1.Deployment("mixtral8x7b",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="mixtral-8x7b",
            ),
            spec=kubernetes.apps.v1.DeploymentSpecArgs(
                replicas=1,
                selector=kubernetes.meta.v1.LabelSelectorArgs(
                    match_labels={
                        "app": "mixtral-8x7b",
                    },
                ),
                template=kubernetes.core.v1.PodTemplateSpecArgs(
                    metadata=kubernetes.meta.v1.ObjectMetaArgs(
                        labels={
                            "app": "mixtral-8x7b",
                        },
                    ),
                    spec=kubernetes.core.v1.PodSpecArgs(
                        containers=[kubernetes.core.v1.ContainerArgs(
                            env=[
                                kubernetes.core.v1.EnvVarArgs(
                                    name="MODEL_ID",
                                    value="mistralai/Mixtral-8x7B-v0.1",
                                ),
                                kubernetes.core.v1.EnvVarArgs(
                                    name="NUM_SHARD",
                                    value="2",
                                ),
                                kubernetes.core.v1.EnvVarArgs(
                                    name="MAX_BATCH_TOTAL_TOKENS",
                                    value="1024000",
                                ),
                                kubernetes.core.v1.EnvVarArgs(
                                    name="MAX_BATCH_TOKENS",
                                    value="32000",
                                ),
                                kubernetes.core.v1.EnvVarArgs(
                                    name="PYTORCH_CUDA_ALLOC_CONF",
                                    value="max_split_size_mb:512",
                                ),
                                kubernetes.core.v1.EnvVarArgs(
                                    name="QUANTIZE",
                                    value="bitsandbytes-nf4",
                                ),
                            ],
                            image="ghcr.io/huggingface/text-generation-inference:1.4.2",
                            name="mixtral-8x7b",
                            ports=[kubernetes.core.v1.ContainerPortArgs(
                                container_port=80,
                                name="server-port",
                            )],
                            resources=kubernetes.core.v1.ResourceRequirementsArgs(
                                limits={
                                    "nvidia.com/gpu": "2",
                                },
                            ),
                            volume_mounts=[
                                kubernetes.core.v1.VolumeMountArgs(
                                    mount_path="/dev/shm",
                                    name="dshm",
                                ),
                                kubernetes.core.v1.VolumeMountArgs(
                                    mount_path="/data",
                                    name="data",
                                ),
                            ],
                        )],
                        volumes=[
                            kubernetes.core.v1.VolumeArgs(
                                empty_dir=kubernetes.core.v1.EmptyDirVolumeSourceArgs(
                                    medium="Memory",
                                ),
                                name="dshm",
                            ),
                            kubernetes.core.v1.VolumeArgs(
                                host_path=kubernetes.core.v1.HostPathVolumeSourceArgs(
                                    path="/mnt/stateful_partition/kube-ephemeral-ssd/mistral-data",
                                ),
                                name="data",
                            ),
                        ],
                    ),
                ),
            ), opts=pulumi.ResourceOptions(provider=self.provider))
        
    def mixtralService(self):
        service = kubernetes.core.v1.Service("mixtral8x7bService",
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                name="mixtral-8x7b-service",
                namespace="default",
            ),
            spec=kubernetes.core.v1.ServiceSpecArgs(
                ports=[kubernetes.core.v1.ServicePortArgs(
                    port=80,
                    target_port=80,
                )],
                selector={
                    "app": "mixtral-8x7b",
                },
                type="LoadBalancer",
            ),opts=pulumi.ResourceOptions(provider=self.provider))
        
        return service