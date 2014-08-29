function INN10crc (v) {
	return (v[9] == (
		(
			 2 * v[0] +
			 4 * v[1] +
			10 * v[2] +
			 3 * v[3] +
			 5 * v[4] +
			 9 * v[5] +
			 4 * v[6] +
			 6 * v[7] +
			 8 * v[8]
		) % 11) % 10
	);
};

function INN12crc (v) {
	return (
		(v[10] == (
			(
				 7 * v[0] +
				 2 * v[1] +
				 4 * v[2] +
				10 * v[3] +
				 3 * v[4] +
				 5 * v[5] +
				 9 * v[6] +
				 4 * v[7] +
				 6 * v[8] +
				 8 * v[9]
			) % 11) % 10
		) &&
		(v[11] == (
			(
				 3 * v[0] +
				 7 * v[1] +
				 2 * v[2] +
				 4 * v[3] +
				10 * v[4] +
				 3 * v[5] +
				 5 * v[6] +
				 9 * v[7] +
				 4 * v[8] +
				 6 * v[9] +
				 8 * v[10]) % 11) % 10
		)
	);
};

function checkINN (v) {
	// Check input string as INN:
	// 1. empty
	// 2. digits only
	// 3. 10 or 12 symbols
	// 4. checksumms
	// Returns:
	// ok: null
	// err: string
	var pattern = /^\d+$/;
	v = "" + v;	// convert to str
	// 1. length
	if (v.length == 0) {
		return "ИНН не может быть пустым";
	}
	// 2. digits only
	if (!pattern.test(v)) {
		return "Только цифры";
	};
	// 3. length
	if ((v.length != 10) && (v.length != 12)) {
		return "10 или 12 символов";
	};
	v = v.split('');
	if (((v.length == 10) && (INN10crc(v) == false)) || ((v.length == 12) && (INN12crc(v) == false))) {
		return "Такого ИНН не может быть";
	};
	return null;
};
