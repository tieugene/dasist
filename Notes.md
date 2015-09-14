# Org #

JS inn:
> ? при начале редактирования (onfocus()/ready()?) - disable supp**> При покидании поля (onchange):
> > clear error
> > проверить: символы, длину, CRC
> > if (ok):
> > > ajax(suppinn)
> > > if exists:
> > > > set suppname, suppfull
> > > > cursor => next field

> > > else: // not exists
> > > > enable suppname, suppfull

> > else: // bad inn
> > > print error**

# Suppliers #
  * core:
    * +models: Org
    * +admin: OrgAdmin
    * +views:
      * +AJAX (get Org)
      * +org**_* +urls: org_**
  * scan:
    * +models: add Scan.shipper
    * +admin: shipper
    * +forms:
      * +check inn
    * +views: scan\_edit
    * +template:
      * +list: shipper
      * +detail: shipper
      * +form: shipper AJAX
  * bills:
    * +models: add Bill.shipper
    * +admin: shipper
    * +forms:
      * +check inn
    * +views:
      * +add
      * +edit
      * +toscan
    * template:
      * +list: shipper
      * +detail: shipper
      * +form: js

# Etc #

OnCreate:

> - selected Place = 1
else:
> - get selected Place (

&lt;select name="place" id="id\_place"&gt;

)
- clear Subject (

&lt;select name="subject" id="id\_subject"&gt;

**&lt;/select&gt;


- Fill w/ set #Place (**

&lt;option value="1"&gt;

Компрессорная

&lt;/option&gt;

)

# Done #
  * DB struct change:
    * core.models.FileSeqItem.file: PrimaryKey
    * scan.model.Scan.events: json?
    * bills.model.Bill.fileseq: FK => 1-2-1 PrimaryKey
    * bills.model.Route.state: delete
    * bills.model.Route.action: delete
    * bills.model.State: delete
  * Place=>Subject dynafilter
  * summs
  * remake Scan
  * fixtures (JSON, w/ auth.user)
  * 0.0.3=>0.1.0 converter

# misc #
http://habrahabr.ru/post/220295/

# browsers #
  * firefox
  * qupzilla
  * chrome
  * rekonq
  * konqueror
  * opera
  * arora
  * midori
  * epiphany
  * dwb
  * kazehakase
  * kazehakase-webkit
  * --Mosaic--

# ajax #
  * http://stackoverflow.com/questions/3233850/django-jquery-cascading-select-boxes
  * http://djangosteps.wordpress.com/2012/01/12/filtered-menus-in-django/
  * http://dustindavis.me/dynamic-filtered-drop-down-choice-fields-with-django.html
  * http://bradmontgomery.blogspot.ru/2008/11/simple-django-example-with-ajax.html
  * http://formerlyconversal.wordpress.com/2009/11/01/dynamic-select-fields-with-jquery-and-django/

  * dajaxice
  * http://django-ru.blogspot.ru/2010/07/django-ajax.html
  * https://github.com/joestump/django-ajax
  * http://mitchfournier.com/2011/06/06/getting-started-with-ajax-in-django-a-simple-jquery-approach/
  * https://www.djangopackages.com/grids/g/ajax/
  * https://github.com/FinalsClub/django-ajax-selects-cascade