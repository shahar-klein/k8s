FROM ubuntu:18.04

USER root

# get a reasonable version of openvswitch
RUN apt-get update
RUN apt-get install -y iproute2 vim 

COPY monitor_pfs.sh /root
RUN chmod +x /root/monitor_pfs.sh


LABEL io.k8s.display-name="nv monitor pfs" \
      io.k8s.description="monitor pfs and set reps accordingly" 

WORKDIR /root
ENTRYPOINT /root/monitor_pfs.sh
