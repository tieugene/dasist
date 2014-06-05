Depends:
* python-django14
* httpd
* mod_wsgi
* memcached
* python-memcached
* python-pillow (PIL)
* poppler-utils (pdfimages)
* ghostscript (gs)

Idea:
* DasIst must be socnet-like:
-- Like/Unlike
-- Comment
-- Advanced

ACL:
* List: all (?)
* View: all (?)
* Add: Исполнитель
* Edit: Исполнитель + Draft
* Del: root | (Исполнитель + (Draft|Rejected))
* Accept: (Исполнитель + Draft) | (Согласователь + OnWay)
* Reject: Согласователь + OnWay
