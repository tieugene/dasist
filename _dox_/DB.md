* firstname:str[1]
* lastname:str[?]
* midname:str[?]
* birthdate:date[?]
* org:str[?]
* department:str[?] (depends on org)
* jobtitle:str[?] (depends on org)
* notes:text[?]
* phone[]:
	- countrycode
	- trunk
	- phone
	- ext
* email[]:
	- email:URI
	- type
* IM[]:
	- im:str
	- type
* Address[]:
	- type
* URL[]:
	- URL
	- type

= Address =
* country:str[const]
* zip:str[?]
* область, край (СРФ)
* city:str[?]
* address (x2)
- or -
* country
* zip
* etc

= enums =
* phonetype
* emailtype
* imtype
* addresstype
* urltype

