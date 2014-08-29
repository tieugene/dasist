function ro_item (item) {			// switch item to readonly
	//console.log(item + " Off");
	$(item).prop("readonly", true);
};
function rw_item (item) {			// switch item to readwrite
	//console.log(item + " On");
	$(item).prop("readonly", false);
};
function enable_suppX (v) {			// switch supplier names enable/disable
	if (v) {
		rw_item("#id_suppname");
		rw_item("#id_suppfull");
	} else {
		ro_item("#id_suppname");
		ro_item("#id_suppfull");
	};
};
function json_to_suppX(url) {
	$.getJSON(url, function(data) {
		if (data != null) {				// if found:
			$('#id_suppname').val(data.name);	// * fill supp*;
			$('#id_suppfull').val(data.fullname);
			$('#id_no').focus();			// * focus to id_billno
		} else {
			enable_suppX(true);
		};
	})
};
