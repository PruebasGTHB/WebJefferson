// refrigeracion.js

document.addEventListener("DOMContentLoaded", () => {
  const compresores = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"];
  const tuneles = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10"];

  const filtros = {
    compresores: new Set(compresores),
    tuneles: new Set(tuneles),
    fecha_inicio: document.getElementById("fecha-inicio").value,
    fecha_termino: document.getElementById("fecha-fin").value,
  };

  inicializarChips();
  inicializarBotones();
  cargarDatos();

  function inicializarChips() {
    document.querySelectorAll(".chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        const tipo = chip.dataset.tipo;
        const id = chip.dataset.id;

        if (filtros[tipo].has(id)) {
          filtros[tipo].delete(id);
          chip.classList.remove("selected");
        } else {
          filtros[tipo].add(id);
          chip.classList.add("selected");
        }

        cargarDatos();
      });
    });
  }

  function inicializarBotones() {
    document.getElementById("btn-compresores").addEventListener("click", () => {
      scrollToSeccion("voltaje-compresores");
    });

    document.getElementById("btn-tuneles").addEventListener("click", () => {
      scrollToSeccion("voltaje-tuneles");
    });

    document.getElementById("descargar-datos").addEventListener("click", () => {
      alert("📥 Descarga iniciada (esto es un placeholder)");
    });
  }

  function scrollToSeccion(id) {
    const seccion = document.getElementById(id);
    if (seccion) {
      window.scrollTo({
        top: seccion.offsetTop - 100,
        behavior: "smooth",
      });
    }
  }

  function cargarDatos() {
    const payload = {
      compresores: Array.from(filtros.compresores),
      tuneles: Array.from(filtros.tuneles),
      fecha_inicio: filtros.fecha_inicio,
      fecha_termino: filtros.fecha_termino,
    };

    fetch("/api/refrigeracion_dashboard/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": document.querySelector('[name="csrf-token"]').content,
      },
      body: JSON.stringify(payload),
    })
      .then((res) => res.json())
      .then((data) => {
        actualizarTablasYGraficos(data);
      })
      .catch((err) => console.error("❌ Error cargando datos:", err));
  }

  function actualizarTablasYGraficos(data) {
    renderTabla("tabla-voltaje-compresores", data.compresores.voltaje);
    renderTabla("tabla-amperaje-compresores", data.compresores.amperaje);
    renderTabla("tabla-demanda-compresores", data.compresores.demanda);
  
    renderTabla("tabla-voltaje-tuneles", data.tuneles.voltaje);
    renderTabla("tabla-amperaje-tuneles", data.tuneles.amperaje);
    renderTabla("tabla-demanda-tuneles", data.tuneles.demanda);
  
    renderizarGrafico("grafico-demanda-compresores", data.compresores.grafico_demanda);
    renderizarGrafico("grafico-demanda-tuneles", data.tuneles.grafico_demanda);
  }
  
  function renderTablaFija(tablaId, tags, datos) {
    const tbody = document.getElementById(tablaId).querySelector("tbody") || document.getElementById(tablaId);
    tbody.innerHTML = "";
  
    tags.forEach(tag => {
      const filaData = datos.find(d => d.tag === tag) || {};
      const tr = document.createElement("tr");
  
      ["tag", "min", "max", "promedio"].forEach(key => {
        const td = document.createElement("td");
        td.textContent = key === "tag" ? tag : (filaData[key] ?? "--");
        tr.appendChild(td);
      });
  
      tbody.appendChild(tr);
    });
  }
  

  // Placeholder de renderizado Chart.js (a reemplazar por lógica real)
  function renderizarGrafico(canvasId, dataset) {
    const ctx = document.getElementById(canvasId).getContext("2d");
    if (window[canvasId]) window[canvasId].destroy();  // limpiar gráfico previo
  
    window[canvasId] = new Chart(ctx, {
      type: "line",
      data: {
        labels: dataset.fechas,
        datasets: dataset.series.map(serie => ({
          label: serie.nombre,
          data: serie.valores,
          borderColor: serie.color || "#000",
          fill: false
        }))
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'top' } },
        scales: { x: { display: true }, y: { beginAtZero: true } }
      }
    });
  }
  
});
