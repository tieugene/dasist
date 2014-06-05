Depends:
* python-django14
* httpd
* mod_wsgi
* memcached
* python-memcached
* python-pillow (PIL)
* poppler-utils (pdfimages)
* ghostscript (gs)

0.0.2 to 0.0.3:
* svn up
* ./manage.py syncdb
* ./manage.py loaddata 0.0.3.json

HowTo:
* Все видят всех (круговая порука)
* Цвета:
** Белый - всё чики
** Желтый - никто не брался
** Красный - брался, но неправильно указано подобъект
** Редактировать - только свои
* Ограничения:
** Поле "Подобъект" - следите за руками
** Page size == 25 строк
