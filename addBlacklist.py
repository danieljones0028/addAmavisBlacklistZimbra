# -*- coding: utf-8 -*-
#
# WILL BE RECEIVED FROM THE RUNDECK A FILE, WHICH CONTAINS THE NAMES OF DOMAINS TO BE INCLUDED IN THE RBL OF AMAVIS
# RUNDECK WILL CHANGE ANY NAME GIVEN TO THE FILE TO amavis_newchecklist AND PLACE IT IN / tmp SO
# GUARANTEE THAT THE CONSULTATION FILE WILL BE AVAILABLE TO SCRIPT
import subprocess
from subprocess import check_output,CalledProcessError,PIPE
import os
import sys

global domain
global command_awk2
amavis_domainlist = ""
command_awk2 = "'{print $2}'"
command_sedwhitelines = "'/^$/d'"
domain = 'YOUDOMAIN.COM'

def getlist_amavis():
    getlist_amavis = 'zmprov gd %s amavisBlacklistSender | grep -v %s | awk %s | sed %s > /tmp/amavis_%s_blacklist' % (domain, domain,command_awk2, command_sedwhitelines, domain)
    subprocess.call(getlist_amavis, shell=True)
    if os.path.exists('/tmp/amavis_%s_blacklist' % (domain)):
        domain_list = ('/tmp/amavis_%s_blacklist' % (domain))
        global amavis_domainlist
        amavis_domainlist = open(domain_list, 'r').read().split('\n')
    else:
        print('Current amavis list file not found please contact support')
        sys.exit(1)


def search_domain():
    global amavis_domainlist
    if os.path.exists('/tmp/amavis_newchecklist'):
        new_domainline = open('/tmp/amavis_newchecklist', 'r').read().split('\n')
    else:
        print('Query file not found, contact support.')
        sys.exit(1)
    
    f = open('/dev/null', 'w')

    for add_domain in new_domainline:
        for domainlist in amavis_domainlist:
            if domainlist != "":
                path_file = '/tmp/amavis_%s_blacklist' % (domain)
                audit_name = subprocess.Popen(['grep', add_domain, path_file], stdout=subprocess.PIPE)
                audit_name.communicate()[0]
                sys.stdout = f
                exit_code = audit_name.returncode
                if exit_code == 1:
                    print('Adding the domain: %s' % (add_domain))
                    action_finder = 'zmprov md %s +amavisBlacklistSender %s' % (domain, add_domain)
                    subprocess.call(action_finder, shell=True)
                    getlist_amavis()



getlist_amavis()
search_domain()