
    var myInput = document.getElementById("senhaNovaCadastrada");
    var letter = document.getElementById("minuscsula");
    var capital = document.getElementById("maiuscula");
    var number = document.getElementById("numero");
    var length = document.getElementById("tamanho");

    // When the user clicks on the password field, show the message box
    myInput.onfocus = function() {
        document.getElementById("mensagem").style.display = "block";
    }

    // When the user clicks outside of the password field, hide the message box
    myInput.onblur = function() {
        document.getElementById("mensagem").style.display = "none";
    }

    // When the user starts to type something inside the password field
    myInput.onkeyup = function() {
    // Validate lowercase letters
    var lowerCaseLetters = /[a-z]/g;
    if(myInput.value.match(lowerCaseLetters)) {  
        minuscsula.classList.remove("invalid");
        minuscsula.classList.add("valid");
    } else {
        minuscsula.classList.remove("valid");
        minuscsula.classList.add("invalid");
    }
  
    // Validate capital letters
    var upperCaseLetters = /[A-Z]/g;
    if(myInput.value.match(upperCaseLetters)) {  
        maiuscula.classList.remove("invalid");
        maiuscula.classList.add("valid");
    } else {
        maiuscula.classList.remove("valid");
        maiuscula.classList.add("invalid");
    }

    // Validate numbers
    var numbers = /[0-9]/g;
    if(myInput.value.match(numbers)) {  
        numero.classList.remove("invalid");
        numero.classList.add("valid");
    } else {
        numero.classList.remove("valid");
        numero.classList.add("invalid");
    }
  
    // Validate length
    if(myInput.value.length >= 8) {
        tamanho.classList.remove("invalid");
        tamanho.classList.add("valid");
    } else {
        tamanho.classList.remove("valid");
        tamanho.classList.add("invalid");
    }
}

