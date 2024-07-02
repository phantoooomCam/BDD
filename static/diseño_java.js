const formulario=document.getElementById('formulario');
const inputs = document.querySelectorAll('#formulario input');

const expresiones ={
    usuario: /^[a-zA-Z0-9\_\-]{4,16}$/, // Letras, numeros, guion y guion_bajo
	nombre: /^[a-zA-ZÀ-ÿ\s]{1,40}$/, // Letras y espacios, pueden llevar acentos.
	password: /^.{8,12}$/, // 8 a 12 digitos.
	correo: /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/,
	telefono: /^\d{10}$/, // 10 numeros.
    matricula: /^.\d{10}$/ //10 caracteres numericos
}

const validarform= (e)=>{
    switch(e.target.name){
        case "nombre":
           valiadarCampo(expresiones.nombre, e.target, 'nombre');
        break;
        case "apellidos":
           valiadarCampo(expresiones.nombre, e.target,'apellidos');
        break;
        case "telefono":
            valiadarCampo(expresiones.telefono, e.target, 'telefono');
        break;
        case "matricula":
            valiadarCampo(expresiones.telefono, e.target,'matricula');
        break;
        case "email": 
            valiadarCampo(expresiones.correo, e.target, 'email');
        break;
        case "password":
            valiadarCampo(expresiones.password, e.target, 'password');
        break;
    } 
}
const valiadarCampo = (expresion,input,campo) => {
    if(expresion.test(input.value)){
        document.getElementById(`grupo_${campo}`).classList.remove('formulario_grupo-incorrecto');
        document.getElementById(`grupo_${campo}`).classList.add('formulario_grupo-correcto');
        document.querySelector(`#grupo_${campo} i`).classList.add('fa-check-circle');
        document.querySelector(`#grupo_${campo} i`).classList.remove('fa-times-circle');  
        document.querySelector(`#grupo_${campo} .formulario_input-error`).classList.remove('formulario_input-error-activo');
        
        }
       else{
            document.getElementById(`grupo_${campo}`).classList.add('formulario_grupo-incorrecto');
            document.getElementById(`grupo_${campo}`).classList.remove('formulario_grupo-correcto');
            document.querySelector(`#grupo_${campo} i`).classList.add('fa-times-circle');
            document.querySelector(`#grupo_${campo} i`).classList.remove('fa-check-circle');  
            document.querySelector(`#grupo_${campo} .formulario_input-error`).classList.add('formulario_input-error-activo');
        }
}

inputs.forEach((input)=>{
    input.addEventListener('keyup', validarform)
    input.addEventListener('blur', validarform)
}); 
document.addEventListener("DOMContentLoaded", function(){
    var btn1 = document.querySelector('.sing');

    btn1.addEventListener("click", function(){
        window.location.href="/registro"
    });
})

