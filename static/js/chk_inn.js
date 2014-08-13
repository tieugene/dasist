function checkINN(inputNumber){
    //преобразуем в строку
    inputNumber = "" + inputNumber;
    //преобразуем в массив
    inputNumber = inputNumber.split('');
    //для ИНН в 10 знаков
    if((inputNumber.length == 10) && (inputNumber[9] == ((2 * inputNumber[  0] + 4 * inputNumber[1] + 10 * inputNumber[2] + 3 * inputNumber[3] + 5 * inputNumber[4] + 9 * inputNumber[5] + 4 * inputNumber[6] + 6 * inputNumber[7] + 8 * inputNumber[8]) % 11) % 10)){
        return true;
    //для ИНН в 12 знаков
    }else if((inputNumber.length == 12) && ((inputNumber[10] == ((7 * inputNumber[ 0] + 2 * inputNumber[1] + 4 * inputNumber[2] + 10 * inputNumber[3] + 3 * inputNumber[4] + 5 * inputNumber[5] + 9 * inputNumber[6] + 4 * inputNumber[7] + 6 * inputNumber[8] + 8 * inputNumber[9]) % 11) % 10) && (inputNumber[11] == ((3 * inputNumber[ 0] + 7 * inputNumber[1] + 2 * inputNumber[2] + 4 * inputNumber[3] + 10 * inputNumber[4] + 3 * inputNumber[5] + 5 * inputNumber[6] + 9 * inputNumber[7] + 4 * inputNumber[8] + 6 * inputNumber[9] + 8 * inputNumber[10]) % 11) % 10))){
        return true;
    }else{
        return false;
    }
}
//
$.validator.addMethod("checkINN", function(value, elem) {
    var inputNumber = $(elem).val();  // или value
    //преобразуем в строку
    inputNumber = "" + inputNumber;
    //преобразуем в массив
    inputNumber = inputNumber.split('');
    //для ИНН в 10 знаков
    if((inputNumber.length == 10) &&
        (inputNumber[9] ==
            ((2 * inputNumber[  0] + 4 * inputNumber[1] + 10 *
             inputNumber[2] + 3 * inputNumber[3] + 5 *
             inputNumber[4] + 9 * inputNumber[5] + 4 *
             inputNumber[6] + 6 * inputNumber[7] + 8 *
             inputNumber[8]) % 11) % 10))
    {
        return true;
    //для ИНН в 12 знаков
    }
    else if((inputNumber.length == 12) &&
        ((inputNumber[10] == ((7 * inputNumber[ 0] + 2 *
        inputNumber[1] + 4 * inputNumber[2] + 10 *
        inputNumber[3] + 3 * inputNumber[4] + 5 *
        inputNumber[5] + 9 * inputNumber[6] + 4 *
        inputNumber[7] + 6 * inputNumber[8] + 8 *
        inputNumber[9]) % 11) % 10) &&
        (inputNumber[11] == ((3 * inputNumber[ 0] + 7 *
         inputNumber[1] + 2 * inputNumber[2] + 4 *
         inputNumber[3] + 10 * inputNumber[4] + 3 *
         inputNumber[5] + 5 * inputNumber[6] + 9 *
         inputNumber[7] + 4 * inputNumber[8] + 6 *
         inputNumber[9] + 8 * inputNumber[10]) % 11) % 10)))
    {
        return true;
    }
    else
    {
        return false;
    }

    },"Введите корректный ИНН");
