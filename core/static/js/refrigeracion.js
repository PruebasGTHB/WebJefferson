const coloresPorTag = {
  C1: '#D32F2F', C2: '#388E3C', C3: '#FBC02D', C4: '#1976D2',
  C5: '#F57C00', C6: '#7B1FA2', C7: '#0097A7', C8: '#C2185B',
  T1: '#303F9F', T2: '#00796B', T3: '#512DA8', T4: '#455A64',
  T5: '#E64A19', T6: '#5D4037', T7: '#C62828', T8: '#0288D1',
  T9: '#2E7D32', T10: '#AFB42B'
};

document.addEventListener("DOMContentLoaded", () => {
  const filtros = {
    compresores: new Set(["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"]),
    tuneles: new Set(["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10"])
  };

  inicializarChips();
  inicializarFecha();
  cargarDatos();

  function inicializarChips() {
    document.querySelectorAll(".chip").forEach((chip) => {
      const tipo = chip.dataset.tipo;
      const id = chip.dataset.id;

      chip.addEventListener("click", () => {
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

    document.querySelectorAll(".chip-action").forEach((btn) => {
      const tipo = btn.dataset.tipo;
      const accion = btn.dataset.action;

      btn.addEventListener("click", () => {
        const chips = document.querySelectorAll(`.chip[data-tipo="${tipo}"]`);
        filtros[tipo].clear();

        if (accion === "all") {
          chips.forEach(chip => {
            chip.classList.add("selected");
            filtros[tipo].add(chip.dataset.id);
          });
        } else if (accion === "none") {
          chips.forEach(chip => chip.classList.remove("selected"));
        }

        cargarDatos();
      });
    });
  }

  function inicializarFecha() {
    document.getElementById("fecha-inicio").addEventListener("change", cargarDatos);
    document.getElementById("fecha-fin").addEventListener("change", cargarDatos);
  }

  function cargarDatos() {
    const inicio = document.getElementById("fecha-inicio").value;
    const fin = document.getElementById("fecha-fin").value;

    if (!inicio || !fin) return;

    fetch(`/api/datos_refrigeracion/?inicio=${inicio}&fin=${fin}`)
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          console.error("⚠️ Error del servidor:", data.error);
          return;
        }

        const compSel = Array.from(filtros.compresores);
        const tunSel = Array.from(filtros.tuneles);

        actualizarTablas("comp", compSel, data.compresores);
        actualizarTablas("tun", tunSel, data.tuneles);

        renderizarGrafico("voltaje-comp-grafico", data.grafico_voltaje_compresores, compSel);
        renderizarGrafico("amperaje-comp-grafico", data.grafico_amperaje_compresores, compSel);
        renderizarGrafico("demanda-comp-grafico", data.grafico_demanda_compresores, compSel);

        renderizarGrafico("voltaje-tun-grafico", data.grafico_voltaje_tuneles, tunSel);
        renderizarGrafico("amperaje-tun-grafico", data.grafico_amperaje_tuneles, tunSel);
        renderizarGrafico("demanda-tun-grafico", data.grafico_demanda_tuneles, tunSel);
      })
      .catch(err => console.error("❌ Error al cargar datos:", err));
  }

  function actualizarTablas(tipo, seleccionados, datos) {
    if (!datos) return;

    ["voltaje", "amperaje", "demanda"].forEach(metrica => {
      const tablaId = `${metrica}-${tipo}-tabla`;
      const tbody = document.getElementById(tablaId);
      tbody.innerHTML = "";

      const lista = datos[metrica];
      if (!lista) return;

      lista
        .filter(d => seleccionados.includes(d.tag))
        .forEach(dato => {
          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td>${dato.tag}</td>
            <td>${dato.min}</td>
            <td>${dato.max}</td>
            <td>${dato.prom}</td>
          `;
          tbody.appendChild(tr);
        });
    });
  }

  function renderizarGrafico(canvasId, graficoData, seleccionados) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !graficoData || !graficoData.series) return;

    const ctx = canvas.getContext("2d");

    if (window[canvasId] && typeof window[canvasId].destroy === "function") {
      window[canvasId].destroy();
    }

    const series = graficoData.series.filter(s => seleccionados.includes(s.nombre));
    if (series.length === 0) return;

    const fechasUnicas = new Set(graficoData.fechas.map(f => f.split(" ")[0]));
    const usarFechaYHora = fechasUnicas.size > 1;

    window[canvasId] = new Chart(ctx, {
      type: "line",
      data: {
        labels: graficoData.fechas,
        datasets: series.map(s => ({
          label: s.nombre,
          data: s.valores,
          borderColor: generarColor(s.nombre),
          backgroundColor: generarColor(s.nombre),
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.3,
          fill: false
        }))
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: {
              usePointStyle: true,
              pointStyle: 'line',
              boxWidth: 25,
              font: { size: 12 }
            },
            onClick: null  // desactiva ocultar series con clic
          },
          tooltip: {
            mode: 'nearest',
            intersect: false,
            callbacks: {
              label: function(context) {
                const label = context.dataset.label || '';
                const value = context.formattedValue || '-';
                return `${label}: ${value}`;
              }
            }
          }
        },
        interaction: {
          mode: 'nearest',
          axis: 'x',
          intersect: false
        },
        scales: {
          x: {
            title: { display: true, text: "Tiempo" },
            ticks: {
              autoSkip: true,
              maxTicksLimit: 10,
              maxRotation: 45,
              minRotation: 0,
              callback: function (value) {
                const label = this.getLabelForValue(value);
                if (!label.includes(" ")) return label;
                const [fecha, hora] = label.split(" ");
                return usarFechaYHora ? `${fecha}\n${hora}` : hora;
              }
            }
          },
          y: {
            title: { display: true, text: "Valor" }
          }
        }
      }
    });
  }

  function generarColor(tag) {
    return coloresPorTag[tag] || '#000000';
  }
});
