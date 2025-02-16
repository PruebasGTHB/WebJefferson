// Elemento del foco
const foco = document.getElementById('foco');

// Simulación de niveles de energía desde "base de datos"
async function obtenerEnergiaDeBaseDeDatos() {
    // Aquí se simula un valor que se obtendría de una base de datos
    const energiaSimulada = [20, 50, 80, 100]; // Valores de energía
    const indice = Math.floor(Math.random() * energiaSimulada.length);
    return energiaSimulada[indice]; // Devolver un valor aleatorio
}

// Función para cambiar el color del foco basado en energía
function cambiarColorPorEnergia(energiaActual) {
    if (energiaActual < 40) {
        // Rojo
        foco.style.background = "radial-gradient(circle, rgba(255, 255, 255, 1) 0%, rgba(255, 0, 0, 1) 50%, rgba(139, 0, 0, 0.8) 70%, rgba(0, 0, 0, 0.9) 95%, rgba(0, 0, 0, 1) 100%)";
        foco.style.boxShadow = "0 0 50px rgba(255, 0, 0, 0.7), 0 0 15px rgba(255, 255, 255, 0.8)";
    } else if (energiaActual < 80) {
        // Amarillo
        foco.style.background = "radial-gradient(circle, rgba(255, 255, 255, 1) 0%, rgba(255, 255, 0, 1) 50%, rgba(204, 204, 0, 0.8) 70%, rgba(0, 0, 0, 0.9) 95%, rgba(0, 0, 0, 1) 100%)";
        foco.style.boxShadow = "0 0 50px rgba(255, 255, 0, 0.7), 0 0 15px rgba(255, 255, 255, 0.8)";
    } else {
        // Verde
        foco.style.background = "radial-gradient(circle, rgba(255, 255, 255, 1) 0%, rgba(0, 255, 0, 1) 50%, rgba(0, 139, 0, 0.8) 70%, rgba(0, 0, 0, 0.9) 95%, rgba(0, 0, 0, 1) 100%)";
        foco.style.boxShadow = "0 0 50px rgba(0, 255, 0, 0.7), 0 0 15px rgba(255, 255, 255, 0.8)";
    }
}

// Función para obtener energía y actualizar el foco
async function actualizarFoco() {
    const energia = await obtenerEnergiaDeBaseDeDatos(); // Simular obtener datos de la base de datos
    console.log("Energía actual:", energia); // Log para verificar
    cambiarColorPorEnergia(energia);

    // Repetir cada 2 segundos (o el tiempo que desees)
    setTimeout(actualizarFoco, 2000);
}

// Iniciar simulación
actualizarFoco();


////////////////////////////////////FLECHAS///////////////////////////////
document.addEventListener("DOMContentLoaded", function () {
    const contenedor = document.querySelector(".graficos__scrollh");
    const btnIzquierda = document.querySelector(".flecha.izquierda");
    const btnDerecha = document.querySelector(".flecha.derecha");

    let desplazamiento = 0;
    const paso = contenedor.offsetWidth; // Desplazamiento de 4 imágenes

    btnDerecha.addEventListener("click", () => {
        desplazamiento += paso;
        contenedor.scrollTo({ left: desplazamiento, behavior: "smooth" });

        btnIzquierda.classList.remove("oculto"); // Muestra el botón izquierdo
        if (desplazamiento >= contenedor.scrollWidth - paso) {
            btnDerecha.classList.add("oculto"); // Oculta el botón derecho si llegamos al final
        }
    });

    btnIzquierda.addEventListener("click", () => {
        desplazamiento -= paso;
        contenedor.scrollTo({ left: desplazamiento, behavior: "smooth" });

        btnDerecha.classList.remove("oculto"); // Muestra el botón derecho si nos devolvemos
        if (desplazamiento <= 0) {
            btnIzquierda.classList.add("oculto"); // Oculta el botón izquierdo si volvemos al inicio
        }
    });
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



//////////////////////////////////////DASHBOARDS/////////////////////////////////////////

document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("modal");
    const closeModal = document.querySelector(".close-modal");
    const dashboardFrame = document.getElementById("dashboard-frame");

    // Manejo de los botones de apertura del modal
    document.querySelectorAll(".open-modal").forEach(button => {
        button.addEventListener("click", function () {
            const dashboardUrl = this.getAttribute("data-src"); // Obtiene la URL
            if (dashboardUrl) {
                dashboardFrame.src = dashboardUrl; // Establece la URL en el iframe
                modal.style.display = "flex"; // Muestra el modal
            }
        });
    });

    // Cerrar el modal
    closeModal.addEventListener("click", function () {
        modal.style.display = "none"; 
        dashboardFrame.src = ""; // Limpia el iframe al cerrar
    });

    // Cerrar modal si se hace clic fuera del contenido
    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
            dashboardFrame.src = ""; // Limpia el iframe al cerrar
        }
    });
});

/////////////////////////////minidashboard/////////////////////////
let miniaturas = {}; // Guardará los gráficos en miniatura

function actualizarMiniatura(dashboardId) {
    fetch(`/api/dashboard/${dashboardId}/`)
        .then(response => response.json())
        .then(data => {
            if (!data || Object.keys(data).length === 0) {
                console.error(`Error: Datos vacíos para Dashboard ${dashboardId}`);
                return;
            }

            let ctx = document.getElementById(`miniatura${dashboardId}`).getContext('2d');
            let labels = Object.keys(data); // ["potencia", "frecuencia"]
            let valores = Object.values(data); // [723.45, 49.8]

            let datasets = [{
                label: `Dashboard ${dashboardId}`,
                data: valores,
                backgroundColor: "rgba(75, 192, 192, 0.5)",
                borderColor: "rgba(75, 192, 192, 1)",
                borderWidth: 1
            }];

            if (miniaturas[dashboardId]) {
                miniaturas[dashboardId].data.labels = labels;
                miniaturas[dashboardId].data.datasets = datasets;
                miniaturas[dashboardId].update(); 
            } else {
                miniaturas[dashboardId] = new Chart(ctx, {
                    type: 'line', // Puedes cambiar a 'line' si prefieres
                    data: {
                        labels: labels,
                        datasets: datasets
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false } // Oculta leyendas para miniatura
                        },
                        scales: {
                            y: { display: false }, // Oculta eje Y para miniatura
                            x: { display: false }  // Oculta eje X para miniatura
                        }
                    }
                });
            }
        })
        .catch(error => console.error(`Error al obtener datos de Miniatura ${dashboardId}:`, error));
}

// Cargar miniaturas cada 5 segundos
setInterval(() => {
    for (let i = 1; i <= 5; i++) {
        actualizarMiniatura(i);
    }
}, 5000);

// Cargar miniaturas al inicio
window.onload = function () {
    for (let i = 1; i <= 5; i++) {
        actualizarMiniatura(i);
    }
};

