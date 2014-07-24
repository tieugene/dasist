Requires:
	* python-django-dajax

OnCreate:
	- selected Place = 1
else:
	- get selected Place (<select name="place" id="id_place">)
- clear Subject (<select name="subject" id="id_subject">*</select>
- Fill w/ set #Place (<option value="1">Компрессорная</option>)

= Done =
* +DB struct change:
	* +core.models.FileSeqItem.file: PrimaryKey
	* +scan.model.Scan.events: json?
	* +bills.model.Bill.fileseq: FK => 1-2-1 PrimaryKey
	* +bills.model.Route.state: delete
	* +bills.model.Route.action: delete
	* +bills.model.State: delete
* +Place=>Subject dynafilter
* +summs
* +remake Scan
* +fixtures (JSON, w/ auth.user)
* +0.0.3=>0.1.0 converter

= misc =
http://habrahabr.ru/post/220295/

= browsers =
+ firefox
+ qupzilla
+ chrome
+ rekonq
+ konqueror
+ opera
+ arora
+ midori
* epiphany
* dwb
* kazehakase
* kazehakase-webkit
x Mosaic
