# -*- coding: utf-8 -*-
#
# WILL BE RECEIVED FROM THE RUNDECK A FILE, WHICH CONTAINS THE NAMES OF DOMAINS TO BE INCLUDED IN THE RBL OF AMAVIS
# RUNDECK WILL CHANGE ANY NAME GIVEN TO THE FILE TO amavisnewchecklist_toip AND PLACE IT IN / tmp SO
# GUARANTEE THAT THE CONSULTATION FILE WILL BE AVAILABLE TO SCRIPT
import subprocess
from subprocess import check_output, CalledProcessError, PIPE
import os
import sys
import socket

import logging
logging.basicConfig(filename='/opt/pyAntispam/log/pyAddblacklist.log', format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

amavis_domainlist = ""
command_awk2 = "'{print $2}'"
command_sedwhitelines = "'/^$/d'"
command_sednewstart = "'s/^/@/g'"
domain = input(str('Digite o nome do seu dominio: '))
# domain = 'tchucas.net'
####PATH ZIMBRA
blacklist_file = '/opt/zimbra/conf/postfix_blacklist'
recipient_file = '/opt/zimbra/conf/postfix_recipient_access'
postmap = '/opt/zimbra/postfix/sbin/postmap'

####PATH APP
amavis_newchecklist = '/tmp/amavis_newchecklist'
amavisnewchecklist_toip = '/tmp/amavisnewchecklist_toip'
amavisnewchecklist_todomain = '/tmp/amavisnewchecklist_todomain'

#####CODE:
def refresh_newlists():
    try:
        refresh = 'cut -d@ -f2 %s | sort | uniq | sed %s > %s' % (amavis_newchecklist, command_sednewstart, amavisnewchecklist_toip)
        subprocess.check_call(refresh, shell=True)
        refresh = 'cut -d@ -f2 %s | sort | uniq > %s' % (amavis_newchecklist, amavisnewchecklist_todomain)
        subprocess.check_call(refresh, shell=True)
    except TypeError as e:
        print(e)
        logging.error(e)

def getlist_amavis():
    getlist_amavis = 'zmprov gd %s amavisBlacklistSender | grep -v %s | awk %s | sed %s > /tmp/amavis_%s_blacklist' % (domain, domain,command_awk2, command_sedwhitelines, domain)
    subprocess.call(getlist_amavis, shell=True)
    if os.path.exists('/tmp/amavis_%s_blacklist' % (domain)):
        domain_list = ('/tmp/amavis_%s_blacklist' % (domain))
        global amavis_domainlist
        amavis_domainlist = open(domain_list, 'r').read().split('\n')
    else:
        print('Current amavis list file not found please contact support')
        logging.warning('Current amavis list file not found please contact support')
        sys.exit(1)

def search_domain():
    global amavis_domainlist
    if os.path.exists(amavisnewchecklist_todomain):
        new_domainline = open(amavisnewchecklist_todomain, 'r').read().split('\n')
    else:
        print('Query file not found, contact support.')
        logging.warning('Query file not found, contact support.')
        sys.exit(1)
    # f = open('/dev/null', 'w')
    for add_domain in new_domainline:
        for domainlist in amavis_domainlist:
            if domainlist != "":
                path_file = '/tmp/amavis_%s_blacklist' % (domain)
                audit_name = subprocess.Popen(['grep', add_domain, path_file], stdout=subprocess.PIPE)
                audit_name.communicate()[0]
                # sys.stdout = f
                exit_code = audit_name.returncode
                if exit_code == 1:
                    print('Adding the domain: %s' % (add_domain))
                    logging.info('Adding the domain: %s' % (add_domain))
                    action_finder = 'zmprov md %s +amavisBlacklistSender %s' % (domain, add_domain)
                    subprocess.call(action_finder, shell=True)
                    getlist_amavis()

def getipdomain_listcurrent():
    try:
        if os.path.exists(blacklist_file):
            blacklist_current = open(blacklist_file, 'r').read().split('\n')
            current_iplist = []
            for line in blacklist_current:
                if line != "":
                    for ip in line.splitlines():
                        k, v = ip.split(" ", 1)
                        current_iplist.append(k)
            current_iplist = list(dict.fromkeys(current_iplist))
            return current_iplist
    except TypeError as e:
        print(e)
        logging.warning(e)

def getipdomain_liststaging():
    try:
        if os.path.exists(amavisnewchecklist_toip):
            checklist = open(amavisnewchecklist_toip).read().split('\n')
            new_iplist = []
            for domain in checklist:
                if domain != "":
                    if domain.find('@') > -1:
                        for ip in domain.splitlines():
                            k, v = ip.split('@', 1)
                            try:
                                if socket.gethostbyname(v):
                                    v = socket.gethostbyname(v)
                                    new_iplist.append(v)
                            except Exception as e:
                                logging.warning('reverso para %s não encontrado' % (v))
                                # print(e)
            new_iplist = list(dict.fromkeys(new_iplist))
            return new_iplist
    except TypeError as e:
        logging.warning(e)
        # print(e)

def comparation_lists():
    try:
        current_iplist = getipdomain_listcurrent()
        new_iplist = getipdomain_liststaging()
        if len(current_iplist) and len(new_iplist) > 0:
            ipsasereminseridos = []
            for ipnews in new_iplist:
                if ipnews != "":
                    if ipnews not in current_iplist:
                        ipsasereminseridos.append(ipnews)
            print('lista a ser inserida %s' % (ipsasereminseridos))
            logging.info('lista a ser inserida %s' % (ipsasereminseridos))
            ipsasereminseridos = list(dict.fromkeys(ipsasereminseridos))
            return ipsasereminseridos
        else:
            logging.info('não existem novas entradas ip')
    except TypeError as e:
        print(e)
        logging.warning(e)

def refresh_config():
    try:
        update = '%s %s' % (postmap, blacklist_file)
        subprocess.check_call(update, shell=True)
    except TypeError as e:
        print(e)
        logging.error(e)
    try:
        update = '%s %s' % (postmap, recipient_file)
        subprocess.check_call(update, shell=True)
    except TypeError as e:
        print(e)
        logging.error(e)

def production_list():
    try:
        ipsasereminseridos = comparation_lists()
        if len(ipsasereminseridos) > 0:
            logging.info('serão incluidos %s ip' % (len(ipsasereminseridos)))
            for ipadd in ipsasereminseridos:
                insert = open(blacklist_file, 'a')
                insert.write('%s REJECT\n' % (ipadd))
                insert.close()
                print('incluindo ip: %s' % (ipadd))
                logging.info('incluindo ip: %s' % (ipadd))
            print('processo finalizado com sucesso.')
            logging.info('processo finalizado com sucesso.')
            refresh_config()
        else:
            print('não existem novas entradas de ip')
            print('processo finalizado com sucesso.')
            logging.info('não existem novas entradas de ip')
            logging.info('processo finalizado com sucesso.')
    except TypeError as e:
        print(e)
        logging.error(e)

def adddomain_recipiens():
    global amavis_domainlist
    try:
        if os.path.exists(amavisnewchecklist_todomain):
            staging_domainlist = open(amavisnewchecklist_todomain, 'r').read().split('\n')
            domain_list = ('/tmp/amavis_%s_blacklist' % (domain))
            amavis_domainlist = open(domain_list, 'r').read().split('\n')
        else:
            print('Query file not found, contact support.')
            logging.warning('Query file not found, contact support.')
            sys.exit(1)
        print(len(amavis_domainlist))
        print(len(staging_domainlist))
        if len(amavis_domainlist) and len(staging_domainlist) > 0:
            nomesasereminseridos = []
            for namenews in staging_domainlist:
                if namenews != "":
                    if namenews not in amavis_domainlist:
                        nomesasereminseridos.append(namenews)
            print('nome a serem inseridos: %s' % (nomesasereminseridos))
            logging.info('nome a serem inseridos: %s' % (nomesasereminseridos))
            for addname in nomesasereminseridos:
                insert = open(recipient_file, 'a')
                insert.write('%s User 550 Unknown\n' % (addname))
                insert.close()
                print('incluindo nome: %s' % (addname))
                logging.info('incluindo nome: %s' % (addname))
        else:
            print('não existem novas entradas de domino')
            print('processo finalizado com sucesso.')
            logging.info('não existem novas entradas de dominio')
            logging.info('processo finalizado com sucesso.')
    except TypeError as e:
        print(e)
        logging.error(e)

refresh_newlists()
getlist_amavis()
search_domain()
adddomain_recipiens()
production_list()
