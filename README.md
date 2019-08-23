# Add Blacklist(postfix and amavis)
## Instalando
```bash
git clone https://github.com/danieljones0028/addAmavisBlacklistZimbra.git --dissociate /opt/pyAntispam && \
mkdir -p /opt/pyAntispam/log && \
touch /opt/pyAntispam/log/pyaddblacklist.log && \
chown -R zimbra. /opt/pyAntispam
```
## Trabalhando
O arquivo /tmp/amavis_novalistadeverificacao será lido pelo script criando varias listas e as comparando com os dados atuais do Zimbra. Os novos dominio/ips encontrados serão adicionados ao amavis(dominio) e ao postfix no arquivo /opt/zimbra/conf/postfix_blacklist.
### /tmp/amavis_novalistadeverificacao
* O arquivo podera ser enviado ao servidor de 'N' maneiras, eu particularmente gosto de utilizar a ferramenta [Rundeck](https://www.rundeck.com/open-source) *(Ele te permite auditar as execuções, quem executa, quem tem acesso ao JOB, API entre outra features)* onde é criando um JOB e o mesmo solicita um arquivo para ser executado, o JOB é configurado para modificar o nome do arquivo que lhe for dado para amavis_novalistadeverificacao e deixo-lo no /tmp apos isto executa o script.
### Amavis
* É criada uma lista com todas as entradas atuais do amavis(zmprov gd meudominio.com.br amavisBlacklistSenders).
* Esta lista sera comparada com a lista gerada a partir do arquivo /tmp/amavis_novalistadeverificacao gerando uma nova lista com os dominio que serão adicionados ao amavis.
* Caso a lista do amavis esteja vazia será adicionado todos os dominios que estão listados no arquivo /tmp/amavis_novalistadeverificacao
### Postfix
* É criada uma lista com todos os MX dos dominios contidos no arquivo /tmp/amavis_novalistadeverificacao.
* Esta lista será comparada com a lista atual do arquivo /opt/zimbra/conf/postfix_blacklist gerando uma nova lista com os IPs que serão adicionados ao arquivo /opt/zimbra/conf/postfix_blacklist
* Caso o arquivo /opt/zimbra/conf/postfix_blacklist não exista será criado e todos os IPs que estão na lista serão adicionados ao arquivo.
## Observações
* Esse script segue a documentação do [Zimbra](https://wiki.zimbra.com/wiki/Specific_Whitelist/Blacklist_per_IP) que recomenda deixa o arquivo /opt/zimbra/conf/postfix_blacklist no seguinte formato 1.2.3.4 REJECT por linha.
* A função de aceitar ou rejeitar e-mails de um endereço expecifico ainda não foi integrada ao script.(Ver mais sobre a função [aqui](https://wiki.zimbra.com/wiki/New_Features_ZCS_8.5))
