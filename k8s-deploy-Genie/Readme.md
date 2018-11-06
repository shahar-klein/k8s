Basic setup for this example are two Ubuntu 18.04 hosts, k8s-master(nd-sjc3a-c18-cpu-06) at 10.0.2.18 and one worker node(nd-sjc3a-c18-cpu-07) at 10.0.2.19.

we start with clean Kubernetes on two hosts and install mlnx_ofed on both.
This use case shows how to provision 1 pv and 4 sriov devices on each pod
For the pv part, install ovn-kubernetes namespace, policy, config and daemonsets
Label the worker node as ovn-host
# kubectl label nodes nd-sjc3a-c18-cpu-07 role=ovn-host
Create ovn-namespace
yaml file is here: https://gitlab-master.nvidia.com/sklein/k8s/blob/master/k8s-deploy-Genie/ovn-namespace.yaml
#kubectl create -f ovn-namespace.yaml
Create ovn policy
yaml file is here: https://gitlab-master.nvidia.com/sklein/k8s/blob/master/k8s-deploy-Genie/ovn-policy.yaml
# kubectl create -f  ovn-policy.yaml
Create ovn config
yaml file us here: https://gitlab-master.nvidia.com/sklein/k8s/blob/master/k8s-deploy-Genie/ovnkube-config.yaml
# kubectl create -f ovnkube-config.yaml
Create the sdn-ovn daemonset
yaml file is here: https://gitlab-master.nvidia.com/sklein/k8s/blob/master/k8s-deploy-Genie/sdn-ovs.yaml
# kubectl create -f sdn-ovs.yaml
Create the ovnkube-master daemon set.
yaml file is here: https://gitlab-master.nvidia.com/sklein/k8s/blob/master/k8s-deploy-Genie/ovnkube-master.yaml
# kubectl create -f ovnkube-master.yaml
Create the ovnkube-node daemon set.
yaml file is here:https://gitlab-master.nvidia.com/sklein/k8s/blob/master/k8s-deploy-Genie/ovnkube.yaml
# kubectl create -f ovnkube.yaml

After the 2 steps above the ovn CNI plugin and a conf file are installed on all hosts.
Rename the conf file created by the ovn daemonset, this is needed on all the cluster hosts because of the way genie works
conf file is here: https://gitlab-master.nvidia.com/sklein/k8s/blob/master/k8s-deploy-Genie/10-ovn-k8s-cni-overlay.conf
# mv /etc/cni/net.d/10-ovn-kubernetes.conf /etc/cni/net.d/10-ovn-k8s-cni-overlay.conf
For the sriov part, we need the sriov plugin.
First install the binaries and conf
yaml file is here: https://gitlab-master.nvidia.com/sklein/k8s/blob/master/k8s-deploy-Genie/k8s-sriov-cni-installer.yaml
# kubectl create -f k8s-sriov-cni-installer.yaml
Create the sriov node config
yaml file is here: https://gitlab-master.nvidia.com/sklein/k8s/blob/master/k8s-deploy-Genie/rdma-sriov-node-config.yml
# kubectl create -f rdma-sriov-node-config.yml
Run the device plugin(it takes few minutes time since it's exposing all the VFs)
yaml file is here: https://gitlab-master.nvidia.com/sklein/k8s/blob/master/k8s-deploy-Genie/sriov-device-plugin.yaml
# kubectl create -f sriov-device-plugin.yaml
As in the ovn case, rename and if needed, edit the conf file on all hosts
yaml file is here: https://gitlab-master.nvidia.com/sklein/k8s/blob/master/k8s-deploy-Genie/20-sriov.conf
# cp 20-sriov.conf /etc/cni/net.d/
# rm /etc/cni/net.d/10-sriov-cni.conf


Genie
Genie creates a conf file in /etc/cni/net.d/00-genie.conf based on the genie-plugin yaml file.
Later, whn the pods are deployed. It will run all the cni annotated in the pods configuration.
Run the genie plugin config and daemonset, Make sure you edit the yaml file and set the k8s_api_root correctly.
#kubectl config view --minify | grep server | cut -f 2- -d ":" | tr -d " "
set the correct address in gennie_plugin.yaml. in this case "k8s_api_root": "https://10.0.2.18:6443"
yaml file is here: https://gitlab-master.nvidia.com/sklein/k8s/blob/master/k8s-deploy-Genie/genie-plugin.yaml
# kubectl create -f genie-plugin.yaml
Lets run some pods, for sriov we need the mofed pods.
Note the annotations part.
yaml is here: https://gitlab-master.nvidia.com/sklein/k8s/blob/master/k8s-deploy-Genie/ub-mofed-5-devs-dp.yaml
# kubectl create -f ub-mofed-5-devs-dp.yaml
Examine the devices on one of the nodes
# kubectl exec -it ub-mofed-deployment-7c78cb66f6-25lkh  -- ip l
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
3: eth0@if155: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1400 qdisc noqueue state UP mode DEFAULT group default
    link/ether 0a:00:00:00:00:16 brd ff:ff:ff:ff:ff:ff link-netnsid 0
59: eth4: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP mode DEFAULT group default qlen 1000
    link/ether f6:56:95:d5:7e:83 brd ff:ff:ff:ff:ff:ff
62: eth2: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP mode DEFAULT group default qlen 1000
    link/ether ae:bb:73:27:3a:2a brd ff:ff:ff:ff:ff:ff
77: eth3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP mode DEFAULT group default qlen 1000
    link/ether d2:ee:d1:53:ac:b7 brd ff:ff:ff:ff:ff:ff
80: eth1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP mode DEFAULT group default qlen 1000
    link/ether b6:df:0d:cb:8f:cc brd ff:ff:ff:ff:ff:ff
 
 
# for i in {0..4}; do echo -n "eth$i: " ; kubectl exec -it ub-mofed-deployment-7c78cb66f6-25lkh  -- ethtool -i  eth$i| grep driver ; done
eth0: driver: veth
eth1: driver: mlx5_core
eth2: driver: mlx5_core
eth3: driver: mlx5_core
eth4: driver: mlx5_core



