
This pyhton script takes a list of PFs as an argument and start monitor them.
When Carrier state is changed, the script will set the PFs repersentor accordignly.

Use make py to create an ubuntu docker image and use the monitor_pfs.yaml DaemonSet to
run it in k8s.

There is an older bash version(make bash) - kept it just in case

you can run it directly on the host: 
i.e. # python monitorPfs.py --pfs enp12s0 enp132s0
