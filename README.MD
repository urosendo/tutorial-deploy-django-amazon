# Deploy de uma aplicação Django #Django #uWSGI #Nginx #Amazon #Ubuntu 

Aplicação no ar: http://52.15.78.92:8000/


Acesse a instância, atualize e instale as dependências:
```
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install nginx
sudo apt-get install build-essential python3.6-dev
sudo apt-get install python3 
sudo apt-get install python3-venv
```

Crie um ambiente virtual para o projeto Django:
```
python3 -m venv venv
```

Ative o ambiente virtual:
```
source venv/bin/activate
```

Altere as variáveis abaixo do settings.py do projeto Django para separar as variáveis de ambiente do seu código utilizando o python-decouple:
```
from decouple import config, Csv
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
```

Clone o repositório do projeto Django do GitHub:
```
git clone https://github.com/urosendo/tutorial-deploy-django-amazon.git
```

Acesse o diretório do projeto:
```
cd tutorial-deploy-django-amazon
```

Atualize o diretório:
```
git pull origin master
```

Use o pip para instalar as dependências do projeto
```
pip install -r requirements.txt
pip install wheel
pip install uwsgi
```

Crie um arquivo .env na pasta do projeto e altere de acordo com seu projeto:
```
SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(chave secreta do projeto)
DEBUG=FALSE 
ALLOWED_HOSTS=127.0.0.1,xxx.xxx.xxx.xxx(ip da instancia)
```

Teste se o projeto esta no ar via servidor de desenvolvimento do Django:
```
python manage.py runserver 0:8000
```

O Django não serve arquivos estáticos, adicione ao settings.py do projeto o código abaixo:
```
STATIC_URL = '/static/'
STATIC_ROOT = Path.joinpath(BASE_DIR, 'static/')
```

 Utilize o comando abaixo para coletar os arquivos estáticos do projeto:
```
python manage.py collectstatic
```

Teste se o projeto esta no ar via uWSGI:
```
uwsgi --http :8000 --module deploy.wsgi
```

Para colocar o projeto no ar com NGinx + uWSGI crie um arquivo de parâmetros chamado 'uwsgi_params' dentro da pasta do projeto e cole o código abaixo:
```
uwsgi_param  QUERY_STRING       $query_string; 
uwsgi_param  REQUEST_METHOD     $request_method; 
uwsgi_param  CONTENT_TYPE       $content_type; 
uwsgi_param  CONTENT_LENGTH     $content_length; 
uwsgi_param  REQUEST_URI        $request_uri; 
uwsgi_param  PATH_INFO          $document_uri; 
uwsgi_param  DOCUMENT_ROOT      $document_root; 
uwsgi_param  SERVER_PROTOCOL    $server_protocol; 
uwsgi_param  REQUEST_SCHEME     $scheme; 
uwsgi_param  HTTPS              $https if_not_empty; 
uwsgi_param  REMOTE_ADDR        $remote_addr; 
uwsgi_param  REMOTE_PORT        $remote_port; 
uwsgi_param  SERVER_PORT        $server_port; 
uwsgi_param  SERVER_NAME        $server_name;
```

Dentro da pasta '/etc/nginx/sites-available/' crie um arquivo de configuração do NGinx chamado 'deploy.conf', cole o código abaixo e modifique de acordo com seu projeto:
```
# mysite_nginx.conf 
# the upstream component nginx needs to connect to 
upstream django { 
    server unix:///home/ubuntu/tutorial-deploy-django-amazon/deploy.sock; # for a file socket 
    #server 127.0.0.1:8001; # for a web port socket (we'll use this first) 
} 
# configuration of the server 
server { 
    # the port your site will be served on 
    listen      8080; 
    # the domain name it will serve for 
    server_name xxx.xxx.xxx; # substitute your machine's IP address or FQDN 
    charset     utf-8; 
    # max upload size 
    client_max_body_size 75M;   # adjust to taste 
    # Django media 
    location /media  { 
        alias /home/ubuntu/tutorial-deploy-django-amazon/media;  # your Django project's media files - amend as required 
    } 
    location /static { 
        alias /home/ubuntu/tutorial-deploy-django-amazon/static; # your Django project's static files - amend as required 
    } 
    # Finally, send all non-media requests to the Django server. 
    location / { 
        uwsgi_pass  django; 
        include     /home/ubuntu/tutorial-deploy-django-amazon/uwsgi_params; # the uwsgi_params file you installed 
    } 
}
```

Crie um link entre os arquivos do nginx:
```
sudo ln -s /etc/nginx/sites-available/deploy.conf /etc/nginx/sites-enabled/
```

Dentro da pasta do projeto execute o comando abaixo:
```
uwsgi --socket deploy.sock --module deploy.wsgi --chmod-socket=666
```

Reinicie Nginx:
```
sudo /etc/init.d/nginx restart
```

Crie um arquivo de parâmetros chamado 'deploy.ini' dentro da pasta do projeto, cole o código abaixo e modifique de acordo com o projeto:
```
[uwsgi] 
chdir           = /home/ubuntu/tutorial-deploy-django-amazon 
module          = deploy.wsgi 
home            = /home/ubuntu/venv 
master          = true 
processes       = 10 
socket          = /home/ubuntu/tutorial-deploy-django-amazon/deploy.sock 
vacuum          = true 
chmod-socket    = 666
```

Execute o comando:
```
uwsgi --ini deploy.ini
```

Configurando emperor mode para as instancias reiniciarem automaticamente caso aconteça algum travamento:
```
sudo mkdir /etc/uwsgi

sudo mkdir /etc/uwsgi/vassals

sudo ln -s /home/ubuntu/tutorial-deploy-django-amazon/deploy.ini /etc/uwsgi/vassals

/home/ubuntu/venv/bin/uwsgi --emperor /etc/uwsgi/vassals --uid www-data --gid www-data
```

Configurando systemctl para a aplicação iniciar no boot caso a máquina desligue
```
cd /etc/systemd/system/
sudo vim uwsgi_deploy.service
```

```
[Unit]

Description= Descrição do serviço
After=syslog.target

[Service]
ExecStart=/home/ubuntu/venv/bin/uwsgi --emperor /etc/uwsgi/vassals --uid www-data --gid www-data
RuntimeDirectory=uwsgi
Restart=always
KillSignal=SIGNQUIT
Type=notify
StandardError=syslog
NotifyAcess=all
User=ubuntu

[Install]
WantedBy=multi-user.target
```

Conceda autorização para o serviço criado:
```
sudo chmod 666 /etc/systemd/system/uwsgi_deploy.service
```

Reinicie regras do systemctl:
```
sudo systemctl daemon-reload
```

Ative o serviço:
```
sudo systemctl enable uwsgi_deploy.service
```

Inicie o serviço:
```
sudo systemctl start uwsgi_deploy.service
```

Reinicie a instância:
```
sudo reboot
```

Pronto, a aplicação Django esta no ar e iniciando automaticamente caso a instância reinicie.

Outros comandos:
```
#Parar o serviço
sudo systemctl stop uwsgi_deploy.service

#Status do serviço
sudo systemctl status uwsgi_deploy.service

#Log do serviço
sudo journalctl -u uwsgi_deploy.service
```



#### Referências:
https://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html

https://uwsgi-docs.readthedocs.io/en/latest/Systemd.html

https://github.com/nginx/nginx/blob/master/conf/uwsgi_params

https://github.com/henriquebastos/python-decouple 
