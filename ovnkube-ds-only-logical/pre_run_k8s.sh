cp /root/99-loopback.conf /etc/cni/net.d/
cp /etc/kubernetes/admin.conf /root/
export KUBECONFIG=/root/admin.conf
kubectl taint nodes --all node-role.kubernetes.io/master-
kubectl label node nd-sjc3a-c18-cpu-06 node-role.kubernetes.io/master=true --overwrite
