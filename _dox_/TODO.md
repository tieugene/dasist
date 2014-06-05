http://wtforms.simplecodes.com/docs/0.6/fields.html
https://flask-wtf.readthedocs.org/en/latest/

* util (run, shell, wsgi, db_create, db_dump)

Итак - multiples (Address, Email, IM etc):
* Add:
** UI:
-- пустых строк - нет
-- есть педали "Добавить <multiple>"
-- добавлять можно сколько угодно
-- удалять - тоже (только не забыть пересчитать orderno (?))
-- on error - to be continued
** View
-- всё - validate
-- on error - to be continued
-- записать item
-- получить id
-- позаписывать multiplies
(TODO: может - как-то оптом можно)
* Edit:
** UI:
-- Имеющиеся:
--- можно редактировать
--- удаление - вычеркиванием (с восстановлением данных из value; с развратом; и где-то фиксировать их id)
-- Новые:
--- Добавлять - сколько угодно (только в конец; с инкрементом orderno)
--- Удалять - сколько угодно (с обновлением orderno)
** View:
-- всё - validate
-- on error - to be continued
-- вырезать все вычеркнутые id и новые
-- удаленные - прибить (?..)
-- записать
-- новые - добавить

Чтобы добыть id - надо отключить form.addresses и проставить ContactAddressForm's самому (с id)

и всю эту хрень оформить как middleware

Extra row: <input id="addresses-0-value" name="addresses-0-value" type="text" value="">

Right now:
* Add:
-- +add address
-- +del address
-- +process after error (add, del)
* Edit:
-- +add new address (need submit handling)
-- +del new address
-- del existant address
-- recall existant address
-- process after error
