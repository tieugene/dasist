2014-11-10:
  * tags/0.1.4
  * bill: magnific-popup for img preview
  * bill: default payer == None
  * bill: special draft&locked color (lime)
  * bill.detail: Approver - FIO | Role | ---
  * bill: ACL
  * bill: Fixed: multiple OK

2014-09-02:
  * scan: magnific-popup for img preview

2014-09-01:
  * atomic: bill**2014-08-31:
  * MySQL**

2014-08-29:
  * trunk => tags/0.1.3
  * trunk == 0.1.4
  * scan.list.filter.supplier returned back
  * indices on
  * org\_edit

2014-08-27:
  * scan.list.filter.shipper == select

2014-08-24:
  * tags/0.1.2
  * trunk == 0.1.3

2014-08-21:
  * branches/dasist:
  * core.Org
  * scan.shipper
  * bill.shipper
  * 0.1.3

2014-08-06:
  * double reject for accounter
  * Bill.lock:bool added
  * state => 1..5 + locked
  * 0.1.2

2014-08-04:
  * 0.1.1 tagged

2014-07-30:
  * Scan.list: pure subj AJAX select

2014-07-25:
  * django 1.6 compatible

2014-06-30:
  * Scan list: subj AJAX filter added

2014-06-23:
  * FileSeq: add, move\_up, move\_down item
  * Bills: add, del, move\_up, move\_down item

2014-06-22:
  * New SVN
  * Accounter can move bill to scan
  * some UI chages
  * FileSeq: del item and self

2014-06-03:
  * Bill list: tr == URL
  * Bill list: vertical padding: 0
  * Bill list: autorefresh 5 min
  * 32 px icons
  * scan: clean\_spaces
  * scan: replace\_depart
  * scan: search/replace place/subj

2014-06-02:
  * Action comment string must be longer
  * "Print" button (4 Accounter)
  * Bill detail: formsets
  * Bill list: state as icon

2014-05-06:
  * 0.0.3 + конвертер
  * 0.1.0
  * Суммы - с копейками
  * place, subject, depart - order by name
  * Иконку фильтра - справа
  * В список: плательщик, сумма к оплате
  * Сканы - исправить колонки
  * Контроль сумм при вводе:
    * Сумма счета - 0
    * Оплачено > СуммыСчета
    * К оплате > (Сумма-Оплачено)
  * При оплате - пересчет сумм
  * Состояния: доплата
  * new state machine
  * bill\_edit (restarated)
  * to scan
  * Дубль - завернуть