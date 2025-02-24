document.addEventListener("DOMContentLoaded", function () {
    const focoRojo = document.getElementById("foco-1");
    const focoAmarillo = document.getElementById("foco-2");
    const focoVerde = document.getElementById("foco-3");

    function encenderFoco(focoEncender, claseEncendido, focosApagar) {
        // Apagar los demás focos
        focosApagar.forEach(foco => {
            foco.classList.remove("foco-1-encendido", "foco-2-encendido", "foco-3-encendido");
            foco.classList.add(foco.id + "-apagado");
        });

        // Encender el foco correspondiente
        focoEncender.classList.remove(focoEncender.id + "-apagado");
        focoEncender.classList.add(claseEncendido);
    }

    function generarEstadoAleatorio() {
        const estados = [
            { foco: focoRojo, clase: "foco-1-encendido", apagar: [focoAmarillo, focoVerde] },
            { foco: focoAmarillo, clase: "foco-2-encendido", apagar: [focoRojo, focoVerde] },
            { foco: focoVerde, clase: "foco-3-encendido", apagar: [focoRojo, focoAmarillo] }
        ];

        // Seleccionar un estado aleatorio
        const estadoSeleccionado = estados[Math.floor(Math.random() * estados.length)];

        // Encender el foco seleccionado
        encenderFoco(estadoSeleccionado.foco, estadoSeleccionado.clase, estadoSeleccionado.apagar);
    }

    // Inicializar todos los focos en apagado al cargar la página
    focoRojo.classList.add("foco-1-apagado");
    focoAmarillo.classList.add("foco-2-apagado");
    focoVerde.classList.add("foco-3-apagado");

    // Ejecutar el primer cambio de estado al cargar la página
    generarEstadoAleatorio();

    // Luego, continuar con los cambios cada 10 segundos
    setInterval(generarEstadoAleatorio, 10000);
});









////////////////////////////////////////HORA//////////////////////////////////////////

document.addEventListener("DOMContentLoaded", function () {
    console.log("El DOM ha cargado. Iniciando actualizarHora()");
    actualizarHora();
    setInterval(actualizarHora, 1000); // Actualiza cada segundo
});

async function actualizarHora() {
    console.log("Intentando obtener la hora del servidor...");

    try {
        let response = await fetch('/hora-servidor/');
        console.log("Respuesta del servidor recibida:", response);

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        let data = await response.json();
        console.log("Hora recibida:", data.hora_servidor);

        let relojElemento = document.getElementById('reloj');
        if (relojElemento) {
            relojElemento.innerText = data.hora_servidor;
        } else {
            console.error("No se encontró el elemento con id 'reloj'");
        }
    } catch (error) {
        console.error("Error al obtener la hora:", error);
    }
}


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

// Marcar el primer botón como activo al cargar la página
document.addEventListener("DOMContentLoaded", function () {
    const primerBoton = document.querySelector(".inferior-izq__selector .botones");
    if (primerBoton) {
        primerBoton.classList.add("boton-activo");
    }
});
