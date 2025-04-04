//CAMBIAR_COLOR-MENU//
document.addEventListener('DOMContentLoaded', function () {
    const enlaces = document.querySelectorAll('.menu-content');

    enlaces.forEach(link => {
      link.addEventListener('click', function () {
        enlaces.forEach(el => el.classList.remove('activo'));
        this.classList.add('activo');
      });
    });
  });




//CAMBIAR_COLOR-BOTONES//



document.addEventListener('DOMContentLoaded', function () {
    const botones = document.querySelectorAll('.botones');
    const iframe = document.getElementById('miIframe');

    // Recuperar desde localStorage
    const idGuardado = localStorage.getItem('botonSeleccionado');
    const urlGuardada = localStorage.getItem('iframeSeleccionado');
    let clicado = null;

    // Buscar el botón guardado
    if (idGuardado) {
        clicado = document.getElementById(idGuardado);
    }

    // Si no hay ninguno, usar el primero
    if (!clicado) {
        clicado = botones[0];
    }

    // Marcar visualmente el botón activo
    clicado.classList.add('clicado');

    // Si hay URL guardada, cargarla en el iframe
    if (urlGuardada) {
        iframe.src = urlGuardada;
    }

    botones.forEach(function (boton) {
        boton.addEventListener('click', function () {
            if (boton === clicado) return;

            // Actualizar clases
            clicado.classList.remove('clicado');
            boton.classList.add('clicado');

            // Guardar en localStorage
            localStorage.setItem('botonSeleccionado', boton.id);
            localStorage.setItem('iframeSeleccionado', boton.getAttribute('onclick').match(/'(.*?)'/)[1]);

            // Cambiar iframe
            cambiarIframe(boton.getAttribute('onclick').match(/'(.*?)'/)[1]);

            // Actualizar referencia del botón clicado
            clicado = boton;
        });
    });
});

// Función externa para cambiar el iframe
function cambiarIframe(nuevaURL) {
    document.getElementById("miIframe").src = nuevaURL;
}



////////////////////////////////////////MOSTRAR CONTENIDO//////////////////////////////////////////


// Usamos el evento 'DOMContentLoaded' para asegurarnos de que el DOM esté cargado antes de ejecutar el código
document.addEventListener('DOMContentLoaded', function() {
    // Seleccionamos el elemento que vamos a modificar
    var elemento = document.getElementById('contenido__principal');

    // Usamos setTimeout para ejecutar una función después de 3 segundos (3000 milisegundos)
    setTimeout(function() {
        // Agregamos la clase 'visible' al elemento, lo que hará que se muestre
        elemento.classList.remove('contenido__principal'); // Quitamos la clase 'invisible' (si está)
        elemento.classList.add('contenido__principal_visible'); // Añadimos la clase 'visible' para que aparezca
    }, 1000); // 3000 milisegundos = 3 segundos
});




////////////////////////////////////////HORA//////////////////////////////////////////



function cambiarColor(botonSeleccionado) {
    console.log("Botón presionado:", botonSeleccionado.innerText);

    // Selecciona todos los botones
    const botones = document.querySelectorAll(".botones");

    // Elimina la clase 'boton-activo' de todos los botones
    botones.forEach(b => b.classList.remove("boton-activo"));

    // Agrega la clase solo al botón presionado
    botonSeleccionado.classList.add("boton-activo");

    // Cambia el texto del <h2>
    const titulo = document.querySelector(".principal__inferior-der h2");
    if (titulo) {
        titulo.textContent = botonSeleccionado.innerText;
    }
}





function cambiarIframe(nuevaURL) {
    document.getElementById("miIframe").src = nuevaURL;
}

// Marcar el primer botón como activo al cargar la página
document.addEventListener("DOMContentLoaded", function () {
    const primerBoton = document.querySelector(".inferior-izq__selector .botones");
    if (primerBoton) {
        primerBoton.classList.add("boton-activo");
    }
});

function cambiarContenido(tipo) {
    var iframe = document.getElementById('miIframe');
    
    // Cambiar el src del iframe dependiendo del botón presionado
    if (tipo === 'consumos') {
        iframe.src = "http://localhost:3000/d-solo/eeeq935b21i4gb/dashboard1?orgId=1&from=1741182822830&to=1741204422830&timezone=browser&panelId=1&__feature.dashboardSceneSolo";
    } else if (tipo === 'producciones') {
        iframe.src = "http://localhost:3000/d-solo/eeeq935b21i4gb/dashboard2?orgId=1&from=1741182822830&to=1741204422830&timezone=browser&panelId=1&__feature.dashboardSceneSolo";
    } else if (tipo === 'costos') {
        iframe.src = "http://localhost:3000/d-solo/eeeq935b21i4gb/dashboard3?orgId=1&from=1741182822830&to=1741204422830&timezone=browser&panelId=1&__feature.dashboardSceneSolo";
    }
}


////////////////////////////////////////mostrar/ocultar menú al hacer clic//////////////////////////////////////////


const toggle = document.getElementById('userMenuToggle');
const dropdown = document.getElementById('userDropdown');

toggle.addEventListener('click', () => {
  dropdown.classList.toggle('show');
  toggle.classList.toggle('active');
});

document.addEventListener('click', function(event) {
  if (!toggle.contains(event.target) && !dropdown.contains(event.target)) {
    dropdown.classList.remove('show');
    toggle.classList.remove('active');
  }
});