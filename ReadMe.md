Requires:
  * httpd
  * mod\_wsgi
  * python-django
  * python-pillow
  * [memcached](memcached.md)
  * [python-memcached]

MySQL howto:
(Fedora 20 specific)
  * sudo yum install mariadb-server
  * sudo chkconfig mariadb on
  * sudo service mariadb start
  * mysql [-u root -p]:
  * CREATE DATABASE dasist CHARACTER SET utf8;
  * CREATE USER 'dasist'@'localhost' IDENTIFIED BY '...';
  * GRANT ALL ON dasist.