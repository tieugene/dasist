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

= Modules =
* core - common things
* bills - Счета
* scan - Архив
* ledger - Счета+Архив

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
