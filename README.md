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
	- 

= Starting =
* httpd
* MySQL; create database, user
CREATE DATABASE `dasist` CHARACTER SET utf8 COLLATE utf8_general_ci;
CREATE USER 'dasist'@'localhost' IDENTIFIED BY 'dasist';
GRANT ALL PRIVILEGES ON dasist.* TO 'dasist'@'localhost' WITH GRANT OPTION;

= Berg =
* После Ксении
