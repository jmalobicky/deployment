from fabric.api import *
from os import path

# grab hosts / mappings from .ssh/config
env.use_ssh_config = True

def selinux():
    run("sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config")

def base():
    selinux()
    run("chkconfig iptables off")
    with settings(warn_only=True):
        run("chkconfig ip6tables off")
        run("chkconfig fcoe off")
        run("chkconfig iscsi off")

def base_pkgs():
    run("yum -y update")
    yum("openssh-server openssh-clients make wget vixie-cron sudo postfix")
    reboot(180)

def change_password(user):
    password = raw_input('Enter a new password for user %s:' % user)
    run('echo "%s:%s" | /usr/sbin/chpasswd' % (user,password))

def bootstrap(repofile, fqdn):
    base()
    base_pkgs()
    epelrepo(repofile)
    hostname(fqdn)
    host_customizations()
    monitoring()

def vmware_tools(filename):
    with settings(warn_only=True):
        put(filename, '/tmp/vmware-tools.tar.gz')
        yum('gcc gcc-c++ kernel-devel perl')
        run('ln -s /usr/src/kernels/`uname -r` /usr/src/linux')
        with cd('/tmp'):
            run('tar -zxf vmware-tools.tar.gz')
            run('vmware-tools-distrib/vmware-install.pl -d')
            run('rm -rf vmware-*')
	
	reboot(180)

def epelrepo(repofile):
    with cd('/etc/pki/rpm-gpg'):
        run('wget http://dl.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL-6')
    put(repofile, '/tmp/epel.repo')
    run('mv -v /tmp/epel.repo /etc/yum.repos.d/')
    run('yum -y update')

def hostname(fqdn):
    run("sed -i '/HOSTNAME=/d' /etc/sysconfig/network")
    run("sed -i -e '$ a\HOSTNAME=%s' /etc/sysconfig/network" % fqdn)
    run("hostname %s" % fqdn)
    run("sed -i '/127.0.0.1/d' /etc/hosts")
    run("sed -i '1 i\\127.0.0.1  %s localhost' /etc/hosts" % fqdn) 
    reboot(180)

def host_customizations():
    bash_customizations()
    system_banners()
    system_timezone(zone='America/Los_Angeles') 
    users()
    reboot(180)

def bash_customizations():
    put('custom-bash-prompt.sh', '/tmp/custom-bash-prompt.sh')
    run("mv /tmp/custom-bash-prompt.sh /etc/profile.d/custom.sh")
    run("chmod +x /etc/profile.d/custom.sh")

def system_banners():
    put('login_banner', '/tmp/login_banner')
    run("sed -i '/#Banner/aBanner /etc/issue' /etc/ssh/sshd_config")
    run('cat /tmp/login_banner > /etc/issue')
    run('cat /tmp/login_banner > /etc/issue.net')
    run('rm -rf /tmp/login_banner')

def system_timezone(zone):
    run('ln -sf /usr/share/zoneinfo/%s /etc/localtime' % zone)

def monitoring():
    yum('nagios-plugins nagios-plugins-all autossh screen')

def users():
    def useradd(username):
        # if the user doesn't exist, add the user, and
        # force a password prompt
        cmd = 'if ! grep -q "^{0}:" /etc/passwd ; then useradd -d /home/{0} -m --shell /bin/bash {0} -g users && passwd {0}; fi'.format(username)
        run(cmd)

    useradd('monitor')
    useradd('sfo00-sys001')

def yum(package):
    run('yum -y install {0}'.format(package))

def buildout_puppetsrv(repofile, fqdn):
    #bootstrap(repofile, fqdn)
    yum('git-core puppet-server')
    run('service puppetmaster start')
    run('chkconfig puppetmaster on')

def puppetclient():
    yum('puppet')
