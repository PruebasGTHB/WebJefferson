const filtros = {
  compresores: new Set(["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"]),
  tuneles: new Set(["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10"])
};

const coloresPorTag = {
  C1: '#E53935', C2: '#43A047', C3: '#FB8C00', C4: '#1E88E5',
  C5: '#8E24AA', C6: '#FDD835', C7: '#00ACC1', C8: '#EC407A',
  T1: '#3949AB', T2: '#7CB342', T3: '#F4511E', T4: '#6D4C41',
  T5: '#5E35B1', T6: '#26C6DA', T7: '#C0CA33', T8: '#D81B60',
  T9: '#039BE5', T10: '#FFB300'
};

document.addEventListener("DOMContentLoaded", () => {
  inicializarTarjetas();
  inicializarFecha();
  cargarDatos();
  actualizarPotencias();

  // Dropdown menú volver al menú
  const toggle = document.getElementById("userMenuToggle2");
  const dropdown = document.getElementById("userDropdown2");

  toggle?.addEventListener("click", (e) => {
    e.stopPropagation();
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
  });

  document.addEventListener("click", (e) => {
    if (!toggle.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.style.display = "none";
    }
  });

  // Botones selección masiva
  document.getElementById("deselect-all-comp").addEventListener("click", () => {
    toggleGroup("compresores", false);
    actualizarCheckboxGrupo("compresores");
  });
  document.getElementById("deselect-all-tun").addEventListener("click", () => {
    toggleGroup("tuneles", false);
    actualizarCheckboxGrupo("tuneles");
  });
  document.getElementById("select-all-comp").addEventListener("change", (e) => {
    setTimeout(() => toggleGroup("compresores", e.target.checked), 0);
  });
  document.getElementById("select-all-tun").addEventListener("change", (e) => {
    setTimeout(() => toggleGroup("tuneles", e.target.checked), 0);
  });
});

function inicializarTarjetas() {
  document.querySelectorAll('.card-equipo').forEach(card => {
    const tag = card.querySelector('.card-header').textContent.trim().split('-')[0];
    const tipo = tag.startsWith("C") ? "compresores" : "tuneles";
    const estadoEl = card.querySelector('.estado-color');

    estadoEl.classList.add(`estado-${tag}`);
    estadoEl.style.color = '#b0b0b0';

    let clickTimeout = null;

    card.addEventListener('click', (e) => {
      if (e.detail === 1) {
        clearTimeout(clickTimeout);
        clickTimeout = setTimeout(() => {
          const estaSeleccionado = card.classList.toggle('selected');
    
          if (estaSeleccionado) {
            filtros[tipo].add(tag);
            estadoEl.style.color = coloresPorTag[tag];
          } else {
            filtros[tipo].delete(tag);
            estadoEl.style.color = '#b0b0b0';
          }
    
          recargarDatosConDelay();
          actualizarPotencias();
          actualizarCheckboxGrupo(tipo);
        }, 250);
      }
    });
    
    card.addEventListener('dblclick', () => {
      clearTimeout(clickTimeout);
    
      const grafanaUrl = urlsPorTag[tag];
      if (!grafanaUrl) {
        alert("No se encontró una URL de Grafana para este equipo.");
        return;
      }
    
      const modal = document.getElementById('modalGrafana');
      const frame = document.getElementById('grafanaFrame');
      const spinner = document.getElementById('spinnerModal');
    
      frame.style.display = 'none';
      spinner.style.display = 'block';
      frame.src = grafanaUrl;
      modal.style.display = 'flex';
    
      frame.onload = () => {
        spinner.style.display = 'none';
        frame.style.display = 'block';
      };
    });

    if (card.classList.contains('selected')) {
      estadoEl.style.color = coloresPorTag[tag];
    }
  });
}

function inicializarFecha() {
  const hoy = new Date();
  const hoyISO = hoy.toISOString().split("T")[0];

  const inicioInput = document.getElementById("fecha-inicio");
  const finInput = document.getElementById("fecha-fin");

  if (inicioInput && !inicioInput.value) {
    inicioInput.value = "2025-01-01"; // o cualquier fecha por defecto deseada
  }

  if (finInput) {
    finInput.value = hoyISO;  // <---- Establece la fecha de fin como hoy
  }

  inicioInput.addEventListener("change", cargarDatos);
  finInput.addEventListener("change", cargarDatos);
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
        borderColor: coloresPorTag[s.nombre] || '#000000',
        backgroundColor: coloresPorTag[s.nombre] || '#000000',
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
          onClick: null
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

function actualizarPotencias() {
  const tags = [...filtros.compresores, ...filtros.tuneles];
  if (tags.length === 0) return;

  const query = tags.map(tag => `tags[]=${tag}`).join("&");

  fetch(`/api/ultima_potencia/?${query}`)
    .then(res => res.json())
    .then(data => {
      const cards = document.querySelectorAll('.card-equipo');

      cards.forEach(card => {
        const header = card.querySelector('.card-header');
        const potenciaEl = card.querySelector('.potencia');
        const estadoEl = card.querySelector('.estado-color');

        if (!header || !potenciaEl || !estadoEl) return;

        const tag = header.textContent.split('-')[0];
        const valor = data[tag];
        const estaSeleccionado = card.classList.contains("selected");

        // Mostrar potencia siempre (incluso si no hay datos)
        if (valor !== undefined) {
          const valorMostrar = valor < 0 ? 0 : valor;
          potenciaEl.textContent = `${valorMostrar} kW`;
        } else {
          potenciaEl.textContent = "– kW";
        }

        // Limpiar clases visuales
        potenciaEl.classList.remove("estado-activo", "estado-inactivo", "estado-gris");
        card.classList.remove("estado-activo", "estado-inactivo");

        // Mostrar borde y color solo si está seleccionado
        if (estaSeleccionado) {
          estadoEl.style.color = coloresPorTag[tag] || "#000";
          if (valor > 0) {
            potenciaEl.classList.add("estado-activo");
            card.classList.add("estado-activo");
          } else {
            potenciaEl.classList.add("estado-inactivo");
            card.classList.add("estado-inactivo");
          }
        } else {
          estadoEl.style.color = "#b0b0b0";
          potenciaEl.classList.add("estado-gris");
        }
      });
    })
    .catch(err => console.error("❌ Error al cargar potencia:", err));
}

function toggleGroup(tipo, seleccionar) {
  const containerId = tipo === "compresores" ? "compresores-cards" : "tuneles-cards";
  const cards = document.querySelectorAll(`#${containerId} .card-equipo`);

  filtros[tipo].clear();

  cards.forEach(card => {
    const tag = card.querySelector('.card-header').textContent.split('-')[0];
    const estadoEl = card.querySelector('.estado-color');

    if (seleccionar) {
      card.classList.add("selected");
      filtros[tipo].add(tag);
      if (estadoEl) estadoEl.style.color = coloresPorTag[tag] || "#000";
    } else {
      card.classList.remove("selected");
      if (estadoEl) estadoEl.style.color = "#b0b0b0";
    }
  });

  cargarDatos();
  actualizarPotencias();
}

// BOTÓN DE DESCARGA CON SPINNER
document.querySelector(".btn-descarga").addEventListener("click", () => {
  const inicio = document.getElementById("fecha-inicio").value;
  const fin = document.getElementById("fecha-fin").value;
  const spinner = document.querySelector(".btn-descarga .spinner");

  spinner.style.display = "inline-block";

  fetch(`/api/descargar_datos/?inicio=${inicio}&fin=${fin}`)
    .then(response => {
      if (!response.ok) throw new Error("No se pudo descargar el archivo.");
      return response.blob();
    })
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `datos_refrigeracion_${inicio}_a_${fin}.xlsx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    })
    .catch(error => {
      console.error("❌ Error en descarga:", error);
      alert("Hubo un problema al descargar el archivo.");
    })
    .finally(() => {
      spinner.style.display = "none";
    });
});


function actualizarCheckboxGrupo(tipo) {
  const containerId = tipo === "compresores" ? "compresores-cards" : "tuneles-cards";
  const checkbox = document.getElementById(`select-all-${tipo === "compresores" ? "comp" : "tun"}`);
  const total = document.querySelectorAll(`#${containerId} .card-equipo`).length;
  const seleccionados = filtros[tipo].size;

  checkbox.checked = seleccionados === total;
}


const urlsPorTag = {
  C1: "https://foodcorp.sgen.ingero.cloud:3000/public-dashboards/893cb27ef22d4bafa84508458fce9d49",
  C2: "https://foodcorp.sgen.ingero.cloud:3000/public-dashboards/f389a2bf37cc4865b66a32d1e31a92d0",
  C3: "https://foodcorp.sgen.ingero.cloud:3000/public-dashboards/37faf41b22c24e76b3e5ace23502af0f",
  C4: "https://foodcorp.sgen.ingero.cloud:3000/public-dashboards/4550a528fa724502ab0ea71f390fce4d",
  C5: "https://foodcorp.sgen.ingero.cloud:3000/public-dashboards/ef312b94e291419a92447f072d2f5a49",
  C6: "https://foodcorp.sgen.ingero.cloud:3000/public-dashboards/98e74337e2b3400fbf1b25a4140a6833",
  C7: "https://foodcorp.sgen.ingero.cloud:3000/public-dashboards/ff2db98492ba4c77ba64ff4e5a98edbd",
  C8: "https://foodcorp.sgen.ingero.cloud:3000/public-dashboards/c0b2e158d26c4716acf94e628232796d",
  T1: "https://foodcorp.sgen.ingero.cloud:3000/public-dashboards/b635fd31e0854b87b8921b2eb55220a2",
  T2: "https://foodcorp.sgen.ingero.cloud:3000/public-dashboards/bd1b4a26b2be4d6f94ce99d034128091",
  T3: "https://foodcorp.sgen.ingero.cloud:3000/public-dashboards/28119de0878944cfa398942270d5a998",
  T4: "https://foodcorp.sgen.ingero.cloud:3000/public-dashboards/21ade213565d4864ac628c8f5e70a1d2",
  T5: "https://foodcorp.sgen.ingero.cloud:3000/public-dashboards/65e5d4f67f95465ab63cea02731f4c9c",
  T6: "https://foodcorp.sgen.ingero.cloud:3000/public-dashboards/539d2b1b9a6d434798405fbfbc96579e",
  T7: "https://foodcorp.sgen.ingero.cloud:3000/public-dashboards/54945a3a4d914658934b701e87f96b3e",
  T8: "https://foodcorp.sgen.ingero.cloud:3000/public-dashboards/5a61f70a5b2a48fc81bf3f6002fa4708",
  T9: "https://foodcorp.sgen.ingero.cloud:3000/public-dashboards/17ccc228e20f427d8b006d91ce6a23b8",
  T10: "https://foodcorp.sgen.ingero.cloud:3000/public-dashboards/7fcc8251c05140439eda21e3e9c54ddf"
};

document.querySelectorAll('.card-equipo').forEach(card => {
  card.addEventListener('dblclick', () => {
    const tag = card.querySelector('.card-header').textContent.trim().split('-')[0];

    const grafanaUrl = urlsPorTag[tag];
    if (!grafanaUrl) {
      alert("No se encontró una URL de Grafana para este equipo.");
      return;
    }

    const modal = document.getElementById('modalGrafana');
    const frame = document.getElementById('grafanaFrame');
    const spinner = document.getElementById('spinnerModal');

    frame.style.display = 'none';
    spinner.style.display = 'block';
    frame.src = grafanaUrl;
    modal.style.display = 'flex';

    frame.onload = () => {
      spinner.style.display = 'none';
      frame.style.display = 'block';
    };
  });
});

// Cerrar modal al hacer clic fuera del contenido
window.addEventListener('click', e => {
  const modal = document.getElementById('modalGrafana');
  if (e.target === modal) {
    modal.style.display = 'none';
    document.getElementById('grafanaFrame').src = '';
  }
});



document.querySelectorAll(".btn-grafana").forEach(button => {
  button.addEventListener("click", () => {
    const tipo = button.dataset.grafana;

    const urlsGenerales = {
      "general-compresores": "https://foodcorp.sgen.ingero.cloud:3000/public-dashboards/1eda289e19e94577bb7585ceca36feda",
      "general-tuneles": "https://foodcorp.sgen.ingero.cloud:3000/public-dashboards/fb3cd63b378f4545b3f620f8be0e683e"
    };

    const url = urlsGenerales[tipo];
    if (!url) return;

    const modal = document.getElementById('modalGrafana');
    const frame = document.getElementById('grafanaFrame');
    const spinner = document.getElementById('spinnerModal');

    frame.style.display = 'none';
    spinner.style.display = 'block';
    frame.src = url;
    modal.style.display = 'flex';

    frame.onload = () => {
      spinner.style.display = 'none';
      frame.style.display = 'block';
    };
  });
});

let datosTimeout;
function recargarDatosConDelay() {
  clearTimeout(datosTimeout);
  datosTimeout = setTimeout(() => {
    cargarDatos();
  }, 400);
}


