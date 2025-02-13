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

const semaforoBtn = document.querySelector(".semaforo__btn");

semaforoBtn.addEventListener("mouseenter", () => {
    semaforoBtn.textContent = "Verde";
});

semaforoBtn.addEventListener("mouseleave", () => {
    semaforoBtn.textContent = "Normal";
});