from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register

import models

@dajaxice_register
def updatecombo(request, option):
    dajax = Dajax()
    options = [['Madrid', 'Barcelona', 'Vitoria', 'Burgos'],
               ['Paris', 'Evreux', 'Le Havre', 'Reims'],
               ['London', 'Birmingham', 'Bristol', 'Cardiff']]
    out = []
    for option in options[int(option)]:
        out.append("<option value='#'>%s</option>" % option)

    dajax.assign('#combo2', 'innerHTML', ''.join(out))
    return dajax.json()

@dajaxice_register
def updatesubj(request, place):
	dajax = Dajax()
	out = []
	if (place):
		out.append('<option value="">---</option>')
		for i in models.Scan.objects.filter(place=place).order_by('subject').distinct().values_list('subject', flat=True):
			if i:
				out.append('<option value="%s">%s</option>' % (i, i))
	dajax.assign('#id_subject', 'innerHTML', ''.join(out))
	return dajax.json()
