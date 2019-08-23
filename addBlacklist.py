# -*- coding: utf-8 -*-

import subprocess
import os
import sys
import socket
import logging
import dns.resolver #pip install dnspython

dominio = input(str('Digite o nome do seu dominio, entre aspas: '))

# Path's
amavis_novalistadeverificacao = '/tmp/amavis_novalistadeverificacao'
amavis_novalistadeverificacaoip = '/tmp/amavis_novalistadeverificacaoip'

# Zimbra Path's
if os.path.exists('/opt/zimbra/conf/postfix_blacklist'):
    postfix_blacklistfile = '/opt/zimbra/conf/postfix_blacklist'
else:
    subprocess.call(['touch', '/opt/zimbra/conf/postfix_blacklist'], shell=True)
# Postmap
if os.path.exists('/opt/zimbra/postfix/sbin/postmap'):
    postmap = '/opt/zimbra/postfix/sbin/postmap'
elif os.path.exists('/opt/zimbra/common/sbin/postmap'):
    postmap = '/opt/zimbra/common/sbin/postmap'
else:
    logging.error('postmap nao encontrado...')
    print('caminho para o postmap nao encontrado, o Zimbra esta instalado?')
    sys.exit(1)
# Zmprov
if os.path.exists('/opt/zimbra/bin/zmprov'):
    zmprov = '/opt/zimbra/bin/zmprov'
else:
    logging.error('zmprov nao encontrado...')
    print('caminho para o zmprov nao encontrado, o Zimbra esta instalado?')
    sys.exit(1)

# Commands
cmd_awk2 = "'{print $2}'"
cmd_apagalinhasembranco = "'/^$/d'"

# Logs
logging.basicConfig(filename='/opt/pyAntispam/log/pyaddblacklist.log', format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

# 1
def listadeverificacao_tratada():
    try:

        if os.path.exists(amavis_novalistadeverificacao):
            amavis_listadeverificacao = open(amavis_novalistadeverificacao, 'r').read().split('\n')
            amavis_novalista = []
            amavis_listadeverificacao = sorted(amavis_listadeverificacao)
            for item in amavis_listadeverificacao:
                try:
                    for dominio in item.splitlines():
                        k, v = dominio.split("@", 2)
                        amavis_novalista.append(v)
                        logging.info('adicionando item a lista de verificacao: %s' % (v))
                except ValueError as e:
                    logging.error(e)
                    amavis_novalista.append(dominio)
                    logging.info('adicionando item a lista de verificacao: %s' % (dominio))

        lista_unica = []

        for item in amavis_novalista:
            if item not in lista_unica:
                logging.info('removendo itens repetidos na lista: %s' % (item))
                lista_unica.append(item)

        lista_unica = sorted(lista_unica)

    except Exception as e:
        print('definicao listadeverificacao_tratada erro: %s' % (e))
        logging.error('definicao listadeverificacao_tratada erro: %s' % (e))

    return lista_unica
# 2
def amavis_listatual():
    amavis_coletalistatual = 'zmprov gd %s amavisBlacklistSender | grep -v %s | awk %s | sed %s > /tmp/amavis_%s_blacklist' % (dominio, dominio, cmd_awk2, cmd_apagalinhasembranco, dominio)
    subprocess.call(amavis_coletalistatual, shell=True)
    try:
        if os.path.exists('/tmp/amavis_%s_blacklist' % (dominio)):
            amavis_listatual_dominios = ('/tmp/amavis_%s_blacklist' % (dominio))
            amavis_listatual_bruta = open(amavis_listatual_dominios, 'r').read().split('\n')
            amavis_listatual_bruta = sorted(amavis_listatual_bruta)

            amavis_listatual = []

            for item in amavis_listatual_bruta:
                if item != "":
                    amavis_listatual.append(item)
                    logging.info('adicionando item a lista atual: %s' % (item))
        else:
            print('Lista atual não encontrada. Chame o suporte.')
            logging.error('Lista atual não encontrada. Chame o suporte.')
            sys.exit(1)

        amavis_listatual = sorted(amavis_listatual)

        return amavis_listatual

    except Exception as e:
        print('definicao amavis_listatual erro: %s' % (e))
        logging.error('definicao amavis_listatual erro: %s' % (e))
# 3
def comparando_listas(atual, checagem):
    listapara_adesao = []
    try:
        for item in checagem:
            if item not in atual:
                logging.info('adicionando item para lista de adesao: %s' % (item))
                listapara_adesao.append(item)
    except Exception as e:
        print('definicao comparando_listas erro: %s' % (e))
        logging.error('definicao comparando_lista erro: %s' % (e))

    listapara_adesao = sorted(listapara_adesao)

    return listapara_adesao
# 4
def lista_ips(data):
    try:
        lista_ips = []
        lista_mx = []
        lista_unica = []
        for mxs in data:
            for mx in dns.resolver.query(mxs, 'MX'):
                mx = mx.to_text()
                try:
                    for nome_mx in mx.splitlines():
                        k, v = nome_mx.split(" ", 2)
                        lista_mx.append(v)
                        logging.info('MX coletado: %s' % (v))
                except ValueError as e:
                    logging.error(e)

            for ips in lista_mx:
                try:
                    if socket.gethostbyname(ips):
                        ip = socket.gethostbyname(ips)
                        lista_ips.append(ip)
                except Exception as e:
                    logging.warning('nao foi possivel resolver o ip do dominio: %s' % (ips))
                    print('nao foi possivel resolver o ip do dominio: %s' % (ips))
    except Exception as e:
        print('definicao lista_ips erro: %s' % (e))
        logging.error('definicao lista_ips erro: %s' % (e))

    for item in lista_ips:
        if item not in lista_unica:
            logging.info('removendo itens repetidos na lista: %s' % (item))
            lista_unica.append(item)

    lista_ip = sorted(lista_unica)

    return lista_ip
# 5
def postfix_blacklist(data):
# pegar a lista atual
    arquivo_blacklist = 'cat %s > %s' % (postfix_blacklistfile, amavis_novalistadeverificacaoip)
    subprocess.call(arquivo_blacklist, shell=True)
    blacklist_atual = open(amavis_novalistadeverificacaoip, 'r').read().split('\n')
    blacklist_atual = sorted(blacklist_atual)
    del blacklist_atual [0]

    lista_unica = []
    lista_ipatual = []
    lista_ipadesao = []
# O arquivo é alimentado IP REJECT por linha. Exemplo 1.1.1.1 REJECT
    try: # Separa IP REJECT
        for ip in blacklist_atual:
            if ip != '':
                for ip_atual in ip.splitlines():
                    k, v = ip_atual.split(" ", 1)
                    lista_ipatual.append(k)

        for item in lista_ipatual:
            if item not in lista_unica:
                logging.info('removendo itens repetidos caso existam na lista: %s' % (item))
                lista_unica.append(item)

        for ip_novo in data:
            if ip_novo not in lista_unica:
                lista_ipadesao.append(ip_novo)
                logging.info('adicionando ip: %s a lista de adesao.' % (ip_novo))

        if not len(lista_ipadesao) == 0:
            for ip_adesao in lista_ipadesao:
                print('incluindo ip: %s' % (ip_adesao))
                cmd_shell = "echo '%s REJECT' >> %s" % (ip_adesao, postfix_blacklistfile)
                subprocess.call(cmd_shell, shell=True)
                logging.info('incluindo ip: %s' % (ip_adesao))

            cmd_postmap = '%s %s' % (postmap, postfix_blacklistfile)
            subprocess.call(cmd_postmap, shell=True)

        else:
            logging.warning('nao existem novas entradas ips')
            print('nao existem novas entradas ips.')

    except Exception as e:
        print('definicao postfix_blacklist erro: %s' % (e))
        logging.error('definicao postfix_blacklist erro: %s' % (e))
# 6
def amavis_blacklistsender(data):
    try:
        if not len(data) == 0:
            for dominio_adesao in data:
                cmd_zmprov = '%s md %s +amavisBlacklistSender %s' % (zmprov, dominio, dominio_adesao)
                subprocess.call(cmd_zmprov, shell=True)
        else:
            logging.info('nao existem novas entradas dominio.')
            print('nao existem novas entradas dominio.')
    except Exception as e:
        print('definicao amavis_blacklistsender erro: %s' % (e))
        logging.error('definicao amavis_blacklistsender erro: %s' % (e))

lista_ips(comparando_listas(amavis_listatual(), listadeverificacao_tratada()))
postfix_blacklist(lista_ips(comparando_listas(amavis_listatual(), listadeverificacao_tratada())))
amavis_blacklistsender(comparando_listas(amavis_listatual(), listadeverificacao_tratada()))
