// === MONITOREO FUNCIONAL CON LOADER FOODCORP ===
window.onload = function () {
  gsap.registerPlugin(Draggable);

  const canvas = document.getElementById("canvas");
  const canvasWrapper = document.getElementById("canvas-wrapper");
  const conexiones = [];
  const csrftoken = document.querySelector('[name="csrf-token"]').content;

  // Loader personalizado
  const loader = document.getElementById("loader-monitoreo");
  loader.style.display = "flex";

  const panzoom = Panzoom(canvas, {
    canvas: true,
    contain: false,
    disablePan: false,
    disableZoom: false,
  });

  canvasWrapper.addEventListener("wheel", e =>
    panzoom.zoomWithWheel(e, { step: 0.08 })
  );

  function centrarCanvas() {
    const wrapperRect = canvasWrapper.getBoundingClientRect();
    const canvasWidth = canvas.offsetWidth;
    const canvasHeight = canvas.offsetHeight;
    const scale = 1;
    panzoom.zoom(scale, { animate: false });
    requestAnimationFrame(() => {
      const panX = (wrapperRect.width / 2) - (canvasWidth / 2);
      const panY = (wrapperRect.height / 2) - (canvasHeight / 2);
      panzoom.pan(panX, panY);
    });
  }

  function aplicarColor(valor, elemento, tipo) {
    if (!elemento) return;
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

  function guardarSoloUnMedidor(card) {
    const id = card.dataset.medidor;
    if (!id) return;
    const draggable = Draggable.get(card);
    const x = draggable?.x ?? 0;
    const y = draggable?.y ?? 0;
    const payload = [{ medidor_id: id, x, y }];
    fetch('/api/guardar_posiciones/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify(payload)
    }).then(res => res.json())
      .then(data => console.log(`✅ Posición guardada (${id}):`, data))
      .catch(err => console.error('❌ Error al guardar posición:', err));
  }

  function guardarConexionesActuales() {
    if (conexiones.length === 0) return;
    const conexionesData = conexiones.map(linea => ({
      origen_id: linea.start.dataset.medidor,
      destino_id: linea.end.dataset.medidor,
      start_socket: linea.startSocket,
      end_socket: linea.endSocket
    }));
    fetch('/api/guardar_conexiones/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify(conexionesData)
    }).then(res => res.json())
      .then(data => console.log('✅ Conexiones guardadas automáticamente:', data))
      .catch(err => console.error('❌ Error al guardar conexiones:', err));
  }

  function posicionarMedidoresCentrados(callback) {
    fetch('/api/posiciones/')
      .then(res => res.json())
      .then(posiciones => {
        const mapa = {};
        posiciones.forEach(p => {
          mapa[p.medidor_id] = { x: p.x, y: p.y };
        });
        const cards = document.querySelectorAll('.medidor-card');
        const total = cards.length;
        const cardWidth = 175;
        const cardGap = 20;
        const totalWidth = total * cardWidth + (total - 1) * cardGap;
        const canvasWidth = canvas.offsetWidth;
        const canvasHeight = canvas.offsetHeight;
        const startX = (canvasWidth - totalWidth) / 2;
        const y = canvasHeight / 2 - 100;
        cards.forEach((card, i) => {
          const id = card.dataset.medidor;
          if (mapa[id]) {
            gsap.set(card, { x: mapa[id].x, y: mapa[id].y });
          } else {
            const x = startX + i * (cardWidth + cardGap);
            gsap.set(card, { x, y });
          }
        });
        if (callback) callback();
      });
  }

  function conectarMedidoresDesdeBD(callback) {
    fetch('/api/conexiones/')
      .then(res => res.json())
      .then(conexionesConfig => {
        conexiones.length = 0;
        conexionesConfig.forEach(({ origen_id, destino_id, start_socket, end_socket }) => {
          const origen = document.querySelector(`[data-medidor="${origen_id}"]`);
          const destino = document.querySelector(`[data-medidor="${destino_id}"]`);
          if (window.LeaderLine && origen && destino) {
            const linea = new LeaderLine(origen, destino, {
              startSocket: start_socket,
              endSocket: end_socket,
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
              dash: { animation: true }
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
        if (callback) callback();
      });
  }

  function actualizarConexiones() {
    if (!window.LeaderLine || !conexiones.length) return;
    conexiones.forEach(linea => linea.position());
  }

  posicionarMedidoresCentrados(() => {
    setTimeout(() => {
      centrarCanvas();
      conectarMedidoresDesdeBD(() => {
        guardarConexionesActuales();
        loader.style.display = 'none'; // Oculta loader al finalizar
      });
    }, 500);
  });

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
      guardarSoloUnMedidor(this.target);
      guardarConexionesActuales();
    }
  });

  actualizarMedidores();
  setInterval(actualizarMedidores, 60000);
};
