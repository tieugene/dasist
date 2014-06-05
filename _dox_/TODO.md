= Done =
+ create users
+ CRUD bill
+ route bill
+ convert: PDF
+ list: filter

+ cyrillic scans
+ remove Files and FileSeq
+ Значки исполнено/завернуто
+ colorify Ok/Reject
+ colorify lines (lightgrey/white, yellow, green, red)
+ paging
+ PDF - add gs
+ download image
+ remove route from Accepted
+ filters (who see what)
= 20140327 =
+ Обратный порядок счетов
+ Управление кол-вом счетов на странице (10/15/20/25/50).
+ Входящие - выделить
+ login redirect
+ Route ended w/ Бухгалтер
+ mailto

= 20140329 =
+ Все/Входящие:
	* Исполнитель: Все=свои, Входящие=свои Исполнено/Завернуто
	* НачОМТС, Директор, ГенДир, Бульгахтер: Все=все, Входящие=На подпись
	* Руководитель - только Входящие
+ Перезапуск счета
= 20140404 =
+ Бухгалтеру - 2 педали: Принято и Исполнено
= 201403.. =
* Объекты и Направления - справочники
* автоподстановка Поставщика
* ?Поставщик - справочник (с fullname)

= FIXME =
* bills.model.Bill.fileseq: FK => OneToOne, pk
* Security:
	* https
	* session timeout
	* change passwords
	* logging
* about
* add img to bill
* convert: tiff not deleted
* files not deleted:
	https://docs.djangoproject.com/en/dev/ref/signals/#django.db.models.signals.pre_delete
	http://stackoverflow.com/questions/2747118/django-deleting-models-and-overriding-delete-method
* fullscreen images:
-- open in new window (popup, 100%)
-- show scaled
-- click switch to full/100%

= Tuning =
* обязательность камментов - в форме

= Feature requests =
* GDrive
* permissions
* Убрать в архив
* Уведомления (mailto)
* Сортировка по направлению и по ответственному
* Filters (state & user; view bill by intermediate approver)
* Project and Depart as models (?)
* перехват счетов в пути
* Перезапуск несогласованного счет
* thunderbird-lightning.Tasks
* webp
* ерунда с этим done и rpoint получается...

----
Format-specific tools:
optipng.i686 : PNG optimizer and converter (optipng)
pngcrush.i686 : Optimizer for PNG (Portable Network Graphics) files (pngcrush)
gif2png
