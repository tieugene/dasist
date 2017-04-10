Requires:
* python-django
* mariadb-server
* MySQL-python
* ImageMagick (mogrify)
* ?python-pillow
* ghostscript
* poppler-utils (pdfimages)
* django-autocomplete-light
X django-simple-autocomplete (https://github.com/praekelt/django-simple-autocomplete/)

= Starting =
* httpd
* MySQL; create database, user ()
CREATE DATABASE `dasist` CHARACTER SET utf8 COLLATE utf8_general_ci;
CREATE USER 'dasist'@'localhost' IDENTIFIED BY 'dasist';
GRANT ALL PRIVILEGES ON dasist.* TO 'dasist'@'localhost' WITH GRANT OPTION;

= Ledger =
== TODO ==
* filter by payer
* views visibility

= Notes =
* .frm - table description
* .ibd - InnoDB file-per-table

= Dump/Restore =
== Remote ==
* ./dothis dump
== Local ==
* recreate DB (drop database dasist; CREATE DATABASE `dasist` CHARACTER SET utf8 COLLATE utf8_general_ci;)
* settings.INSTALLED_APPS - disable 'bills'
* ./dothis sync
* settings.INSTALLED_APPS - enable 'bills'
* ./dothis clean
* ./dothis restore <dump.sql.gz>

== Upgrading ==
= Contracts =
* exclude contract from settings and urls
* del contract/migrations/*.*
* rmdir contract
* ./manage.py dbshell: drop table contract_*
* ./dothis clean
* ./dothis restore ...sql.gz
* ./manage.py migrate --fake sites 0002
* ./manage.py migrate
* UPDATE scan_scan SET depart=NULL where depart="";
* restore contract in settings and urls
* restore contract folder
* ./manage.py makemigrations contracts
* ./manage.py squashmigrations contract 0001 contracts > contract.sql
* ./manage.py sqlmigrate contract 0001 > contract.sql
* change SQL:
    ALTER TABLE `contract_contract` ADD CONSTRAINT ... FOREIGN KEY (`...`) REFERENCES `bills_approver` (`id` > `user_id`);
* ./manage.py dbshell < contract.sql
# ./manage.py migrate --fake-initial contract 0001

Changing passwords:
./manage.py shell
from django.contrib.auth.models import User
u = User.objects.get(username='user02')
u.set_password('pass02')
u.save()