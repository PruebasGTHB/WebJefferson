document.addEventListener('DOMContentLoaded', function () {
  const categoriaField = document.getElementById('id_categoria_visual');

  if (!categoriaField) return;

  const secciones = {
    medidor: "Configuración de Medidor",
    titulo: "Configuración de Título",
    "solo energía": "Configuración de Solo Energía",
    texto: "Configuración de Texto",
  };

  function normalizar(texto) {
    return texto.trim().toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  }

  function toggleSecciones() {
    const categoriaSeleccionada = normalizar(categoriaField.value);

    // Recorre todos los fieldsets colapsables
    document.querySelectorAll('fieldset.collapse').forEach(fs => {
      const leyenda = fs.querySelector('h2, .fieldset-heading');
      if (!leyenda) return;

      const textoLeyenda = normalizar(leyenda.textContent);

      let debeExpandir = false;
      Object.entries(secciones).forEach(([clave, textoEsperado]) => {
        if (clave === categoriaSeleccionada && textoLeyenda.includes(normalizar(textoEsperado))) {
          debeExpandir = true;
        }
      });

      if (debeExpandir) {
        fs.classList.remove('collapsed');
      } else {
        fs.classList.add('collapsed');
      }
    });
  }

  // Ejecutar al cargar y al cambiar la categoría
  toggleSecciones();
  categoriaField.addEventListener('change', toggleSecciones);
});
