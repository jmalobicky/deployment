README for deployment repository

Utilizes python fabric

Fabric deployment server needs the git repository which contains
epel.repo
custom-bash-prompt.sh
login_banner
fabfile.py

The additional file needed if deploying against a virtual machine running on VMware
Get a copy of the tar.gz for the vmware tools installation

Executing:
Allow options shown:
    fab --user=root --hosts=[ips] change_password:root bootstrap:epel.repo,server1.example.local vmware_tools:VMwareTools-8.3.12-493255.tar.gz puppetclient

The fabfile looks for a system that is on the network that has been installed by absolute minimal settings
hostname: localhost.localdomain

change_password
    This takes a user that you want to change the default password for, in this case it is the root user from the base installation

bootstrap
    This take two parameters
        A repository file located in the base directory, epel.repo
        Server fqdn that the system will get renamed to, server1.example.local

vmware_tools
    This takes the tar.gz that comes from the VMware version that your are running on the hypervisor.

puppetclient
    This installs the puppet client pkg and any necessary components


fab --user=root --hosts=[ips] change_password:root buildout_puppetsrv:epel.repo,puppet.example.local vmware_tools:VMwareTools-8.3.12-493255.tar.gz

Replacement of the bootstrap with buildout_puppetsrv
    buildout_puppetsrv includes the bootstrap function, this is why the file parameters are the same.
