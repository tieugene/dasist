== TODO ==
* split media
* move to python3
* unittests
* Headless browser for test (htmlunit ?)
* docker kubernets dasist2sdv

= Requires =
* python-django
* mariadb-server
* MySQL-python
* ImageMagick (mogrify)
* python-pillow
* ghostscript
* poppler-utils (pdfimages)
* django-autocomplete-light (https://github.com/yourlabs/django-autocomplete-light)
* Magnific-popup: http://dimsemenov.com/plugins/magnific-popup/

= Starting =
* httpd
* MySQL; create database, user ()
CREATE DATABASE `dasist` CHARACTER SET utf8 COLLATE utf8_general_ci;
CREATE USER 'dasist'@'localhost' IDENTIFIED BY 'dasist';
GRANT ALL PRIVILEGES ON dasist.* TO 'dasist'@'localhost' WITH GRANT OPTION;
