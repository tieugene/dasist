Done:
* CRUD Bill (w/o m2ms)
* CRUD Route to Bill (as m2m) - views, forms, tpl
* Route Bills (w/ comments)
* Filter list by Role (comment out)
* admin
* ACL by Role and Bill (views, buttons)

ACL:
* List: all
* View: all
* Add: root | Исполнитель
* Edit: root | (Исполнитель + Draft)
* Del: root | (Исполнитель + (Draft|Rejected))
* Accept: (Исполнитель + Draft) | (Согласователь + OnWay)
* Reject: Согласователь + OnWay

Idea:
* DasIst must be socnet-like:
-- Like
-- Unlike
-- Comment
-- Advanced