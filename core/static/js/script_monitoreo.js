// === ACTUALIZACIÓN DE DATOS DE MEDIDORES ===
function aplicarColor(valor, elemento, tipo) {
  let color = isNaN(valor) ? "white" :
              valor < 0 ? "yellow" :
              valor === 0 ? "white" :
              valor >= 10000000 ? "red" : "#00ff88";

  elemento.style.color = color;
  const tipoUnidad = tipo === "energia" ? "KWH" : "KW";
  elemento.setAttribute("title", `El valor de ${tipoUnidad} es ${valor}`);
  elemento.textContent = valor.toString().length > 6 ? valor.toString().slice(0, 6) + "…" : valor.toString();
}

function actualizarMedidores() {
  document.querySelectorAll('.medidor-card').forEach(card => {
    const medidor = card.getAttribute('data-medidor');
    fetch(`/api/consumos/${medidor}/`)
      .then(res => res.json())
      .then(data => {
        aplicarColor(parseFloat(data.energia_total_kwh), card.querySelector('.energia_total'), "energia");
        aplicarColor(parseFloat(data.potencia_total_kw), card.querySelector('.potencia_actual'), "potencia");
      })
      .catch(err => console.error(`Error actualizando ${medidor}:`, err));
  });
}

actualizarMedidores();
setInterval(actualizarMedidores, 60000);

// === MONITOREO COMPLETO CON PANZOOM, DRAG, CONEXIONES Y EDICIÓN ===
window.onload = function () {
  gsap.registerPlugin(Draggable);

  const canvas = document.getElementById("canvas");
  const canvasWrapper = document.getElementById("canvas-wrapper");
  const conexiones = [];

  const panzoom = Panzoom(canvas, {
    canvas: true,
    contain: false,
    disablePan: false,
    disableZoom: false
  });

  canvasWrapper.addEventListener("wheel", e =>
    panzoom.zoomWithWheel(e, { step: 0.08 })
  );

  function posicionarMedidoresCentrados() {
    const medidores = document.querySelectorAll('.medidor-card');
    const total = medidores.length;
    if (total === 0) return;

    const cardWidth = 175;
    const cardGap = 20;
    const totalWidth = total * cardWidth + (total - 1) * cardGap;
    const canvasWidth = canvas.offsetWidth;
    const canvasHeight = canvas.offsetHeight;
    const startX = (canvasWidth - totalWidth) / 2;
    const y = canvasHeight / 2 - 100;

    medidores.forEach((card, i) => {
      const id = card.dataset.medidor;
      const saved = JSON.parse(localStorage.getItem("posicionesMedidores") || "{}");
      if (saved[id]) {
        gsap.set(card, { x: saved[id].x, y: saved[id].y });
      } else {
        const x = startX + i * (cardWidth + cardGap);
        gsap.set(card, { x, y });
      }
    });
  }

  function centrarCanvas() {
    const wrapperRect = canvasWrapper.getBoundingClientRect();
    const canvasWidth = canvas.offsetWidth;
    const canvasHeight = canvas.offsetHeight;
    const scale = 1;
    panzoom.zoom(scale, { animate: false });

    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        const panX = (wrapperRect.width / 2) - (canvasWidth * scale / 2);
        const panY = (wrapperRect.height / 2) - (canvasHeight * scale / 2);
        panzoom.pan(panX, panY);
      });
    });
  }

  function conectarMedidores() {
    const conexionesConfig = [
      ['em39', 'em1', 'bottom', 'top'],
      ['em39', 'em2', 'bottom', 'top'],
      ['em39', 'em6', 'bottom', 'top'],
      ['em39', 'em5', 'bottom', 'top'],
      ['em1', 'em3', 'bottom', 'top'],
      ['em1', 'em4', 'bottom', 'top'],
      ['em1', 'em41', 'bottom', 'top'],
      ['em2', 'em3', 'bottom', 'top'],
      ['em2', 'em4', 'bottom', 'top'],
      ['em2', 'em41', 'bottom', 'top'],
      ['em6', 'em40', 'bottom', 'top'],
      ['em6', 'em7', 'bottom', 'top'],
      ['em6', 'em8', 'bottom', 'top']
    ];

    conexionesConfig.forEach(([origenId, destinoId, startSocket, endSocket]) => {
      const origen = document.querySelector(`[data-medidor="${origenId}"]`);
      const destino = document.querySelector(`[data-medidor="${destinoId}"]`);

      if (window.LeaderLine && origen && destino) {
        const linea = new LeaderLine(origen, destino, {
          startSocket,
          endSocket,
          color: '#00ffff',
          size: 4,
          path: 'grid',
          startPlug: 'none',
          endPlug: 'arrow3',
          dropShadow: true,
          gradient: true,
          endPlugColor: '#bd2323',
          outline: true,
          outlineColor: '#f9cf33',
          outlineSize: 2,
          animOptions: {
            duration: 1200,
            timing: 'ease-in-out',
            dash: true,
            animation: true
          },
          dash: {
            animation: true
          }
        });

        conexiones.push(linea);

        let glow = true;
        setInterval(() => {
          linea.outlineColor = glow ? '#fff33a' : '#f9cf33';
          linea.outlineSize = glow ? 3 : 2;
          linea.color = glow ? '#00ffff' : '#29f1fc';
          linea.size = glow ? 4.2 : 4;
          glow = !glow;
        }, 700);
      }
    });
  }

  function actualizarConexiones() {
    if (!window.LeaderLine || !conexiones.length) return;
    conexiones.forEach(linea => linea.position());
  }

  posicionarMedidoresCentrados();
  centrarCanvas();

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        conectarMedidores();
      });
    });
  });

  document.querySelectorAll('.medidor-card').forEach(card => {
    card.addEventListener('dblclick', () => {
      const grafanaUrl = card.getAttribute('data-grafana-url');
      const medidorNombre = card.querySelector('h3').textContent;

      const iframe = document.getElementById('grafanaIframe');
      const modal = document.getElementById('grafanaModal');
      const loader = document.getElementById('loader');
      const loaderText = document.getElementById('loader-text');

      loaderText.textContent = medidorNombre;
      loader.style.display = 'flex';
      modal.style.display = 'flex';
      iframe.src = grafanaUrl;

      iframe.onload = () => loader.style.display = 'none';
    });
  });

  window.cerrarModal = function () {
    document.getElementById('grafanaModal').style.display = 'none';
    document.getElementById('grafanaIframe').src = '';
    document.getElementById('loader').style.display = 'none';
  };

  Draggable.create(".medidor-card", {
    type: "x,y",
    bounds: "#canvas",
    inertia: false,
    onPress: function (e) {
      panzoom.setOptions({ disablePan: true });
      e.stopPropagation();
    },
    onDrag: actualizarConexiones,
    onRelease: function () {
      panzoom.setOptions({ disablePan: false });
      const id = this.target.dataset.medidor;
      const x = this.x;
      const y = this.y;
      const posiciones = JSON.parse(localStorage.getItem("posicionesMedidores") || "{}");
      posiciones[id] = { x, y };
      localStorage.setItem("posicionesMedidores", JSON.stringify(posiciones));
    }
  });

  let isPanning = false;
  let startX = 0, startY = 0;

  canvasWrapper.addEventListener('pointerdown', e => {
    if (e.target.closest('.medidor-card') || e.target.closest('#grafanaModal')) return;
    isPanning = true;
    startX = e.clientX;
    startY = e.clientY;
    canvasWrapper.style.cursor = 'grabbing';
  });

  canvasWrapper.addEventListener('pointermove', e => {
    if (!isPanning) return;
    const dx = e.clientX - startX;
    const dy = e.clientY - startY;
    startX = e.clientX;
    startY = e.clientY;
    panzoom.pan(dx, dy);
    actualizarConexiones();
  });

  canvasWrapper.addEventListener('pointerup', () => {
    isPanning = false;
    canvasWrapper.style.cursor = 'grab';
  });

  canvasWrapper.addEventListener('mouseleave', () => {
    isPanning = false;
    canvasWrapper.style.cursor = 'grab';
  });

  window.toggleModoEdicion = function () {
    const activos = Draggable.getAll();
    const btn = document.getElementById("modoEdicionBtn");
    if (!activos.length || !btn) return;

    if (activos[0].enabled()) {
      activos.forEach(d => d.disable());
      btn.textContent = "✏️ Activar Edición";
      btn.style.backgroundColor = "#444";
    } else {
      activos.forEach(d => d.enable());
      btn.textContent = "✅ Edición Activa";
      btn.style.backgroundColor = "#117a0e";
    }
  };

  setInterval(actualizarConexiones, 100);
};
