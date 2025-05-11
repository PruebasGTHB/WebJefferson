let abortController = null;
let seccionActual = 'Planta Congelado';
let panzoom, conexiones = [];
let pendingTooltips = [];

function cambiarCanvas(seccion) {
  seccionActual = seccion;
  const canvas = document.getElementById('canvas');
  const loader = document.getElementById('loader-seccion');
  const overlay = document.getElementById('overlay-canvas');
  const sidebar = document.getElementById('sidebar');

  if (loader.style.display === 'block') {
    console.log('⏳ Esperando carga, no se puede cambiar sección todavía.');
    return;
  }

  document.querySelectorAll('#sidebar ul li').forEach(li => li.classList.remove('active'));
  const activeItem = Array.from(document.querySelectorAll('#sidebar ul li')).find(li => li.textContent.trim() === seccion.trim());
  if (activeItem) activeItem.classList.add('active');

  loader.style.display = 'block';
  overlay.style.display = 'block';
  sidebar.classList.remove('open');

  if (conexiones.length) {
    conexiones.forEach(linea => linea.remove());
    conexiones = [];
  }

  canvas.innerHTML = '';
  panzoom.zoom(1); 
  panzoom.pan(0, 0);
  canvas.innerHTML = '';

  fetch(`/api/posiciones/?seccion=${encodeURIComponent(seccion)}`)
    .then(res => res.json())
    .then(medidores => {
      medidores.forEach(med => {
        const card = document.createElement('div');
        card.className = 'medidor-card';
        card.dataset.medidor = med.medidor_id;
        card.dataset.editable = med.editable ? 'true' : 'false';
        card.dataset.seccion = med.seccion;
        card.dataset.categoria = med.categoria_visual;

        if (med.grafana_url) {
          card.dataset.grafanaUrl = med.grafana_url;
        }

        if (["texto", "contenedor", "contenedor-10", "contenedor-100"].includes(med.categoria_visual)) {
          aplicarEstilosBase(card, med);
          if (["contenedor", "contenedor-10", "contenedor-100"].includes(med.categoria_visual)) {
            switch (med.categoria_visual) {
              case "contenedor":
                card.style.zIndex = "0";
                break;
              case "contenedor-10":
                card.style.zIndex = "-10";
                break;
              case "contenedor-100":
                card.style.zIndex = "-100";
                break;
            }
            card.style.pointerEvents = "none";
          }
          canvas.appendChild(card);
          gsap.set(card, { x: med.x ?? 0, y: med.y ?? 0 });
          return;
        }

        else if (med.categoria_visual === 'titulo') {
          card.classList.add('tarjeta-navegacion');
          card.style.backgroundColor = med.fondo_personalizado || '#1769c6';

          const icono = document.createElement('img');
          icono.src = '../static/icons/titulo.png';
          icono.alt = 'Ir a';
          icono.className = 'icono-navegacion';

          const h3 = document.createElement('h3');
          h3.textContent = med.titulo || med.medidor_id;

          if (med.color_titulo) h3.style.color = med.color_titulo;
          if (med.tamano_titulo) h3.style.fontSize = med.tamano_titulo;
          if (med.fuente_titulo) h3.style.fontFamily = med.fuente_titulo;
          if (med.bold_titulo) h3.style.fontWeight = 'bold';

          if (med.alineacion_vertical) {
            card.style.display = 'flex';
            card.style.flexDirection = 'column';
            card.style.justifyContent =
              med.alineacion_vertical === 'top' ? 'flex-start' :
              med.alineacion_vertical === 'bottom' ? 'flex-end' : 'center';
          }

          const contenedor = document.createElement('div');
          contenedor.className = 'titulo-con-icono';
          contenedor.appendChild(icono);
          contenedor.appendChild(h3);
          card.appendChild(contenedor);

          if (med.seccion_destino) {
            card.dataset.seccionDestino = med.seccion_destino;
            card.ondblclick = () => cambiarCanvas(med.seccion_destino);
          }
        }

        else if (["medidor", "energia_sola", "medidorglp", "medidordiesel","medidorvapor","medidorflujometro"].includes(med.categoria_visual)) {
          const tipoValido = med.tipo && med.tipo !== '-' && med.tipo !== 'null' && med.tipo !== 'undefined';
          if (tipoValido) {
            const chip = document.createElement(med.tipo === 'C' ? 'div' : 'span');
            chip.className = `icon-chip ${med.tipo === 'C' ? 'blue' : 'gray'}`;
            chip.textContent = med.tipo;
            if (med.tipo_descripcion?.trim()) {
              pendingTooltips.push({ element: chip, content: med.tipo_descripcion });
            }
            card.appendChild(chip);
          }

          const h3 = document.createElement('h3');
          h3.textContent = med.titulo || med.medidor_id;
          h3.classList.add('titulo-medidor');

          if (med.mostrar_icono_estado) {
            const icono = document.createElement('img');
            const iconoTipo = med.tipo_icono_estado || 'check';
            icono.src = `/static/icons/${iconoTipo}.png`;
            icono.alt = iconoTipo;
            icono.className = 'icono-estado_soloenergía';

            const tituloWrap = document.createElement('div');
            tituloWrap.className = 'titulo-con-icono_soloenergía';
            tituloWrap.appendChild(icono);
            tituloWrap.appendChild(h3);
            card.appendChild(tituloWrap);
          } else {
            card.appendChild(h3);
          }




// kWh	🔋	Batería / Energía almacenada
// m³/h	📦	Volumen / Flujo volumétrico (caja cúbica)
// L/h	🧴	Líquido / Flujo de litros (botella de fluido)
// kg/h	💨	Flujo de masa (vapor o gas)
// Bar G	⚙️	Presión (sistema técnico, instrumentación)
// kg	⚖️	Peso / Masa (balanza)

          // Datos por categoría
          if (med.categoria_visual === 'medidorglp') {
            card.appendChild(crearBloqueDato('kWh', '🔋', 'energia_total', 'kWh'));
            card.appendChild(crearBloqueDato('kW', '📦', 'potencia_actual', 'm³/h')); 
          } else if (med.categoria_visual === 'medidordiesel') {
            card.appendChild(crearBloqueDato('kWh', '🔋', 'energia_total', 'kWh'));
            card.appendChild(crearBloqueDato('kW', '🧴', 'potencia_actual', 'L/h'));
          } else if (med.categoria_visual === 'medidorvapor') {
            card.appendChild(crearBloqueDato('kWh', '🔋', 'energia_total', 'kWh'));
            card.appendChild(crearBloqueDato('kW', '💨', 'potencia_actual', 'kg/h'));
          } else if (med.categoria_visual === 'medidorflujometro') {
            card.appendChild(crearBloqueDato('kWh', '⚙️', 'energia_total', 'Bar G'));      
            card.appendChild(crearBloqueDato('kW', '💨', 'potencia_actual', 'kg/h'));     
            card.appendChild(crearBloqueDato('flujo', '⚖️', 'kg_total', 'kg'));    
          
       

          } else {
            card.appendChild(crearBloqueDato('kWh', '🔄', 'energia_total', 'kWh'));
            if (med.categoria_visual !== 'energia_sola') {
              card.appendChild(crearBloqueDato('kW', '⚡', 'potencia_actual', 'kW'));
            }
          }
        }

        canvas.appendChild(card);
        gsap.set(card, { x: med.x ?? 0, y: med.y ?? 0 });
      });

      fetch(`/api/bloques/?seccion=${encodeURIComponent(seccion)}`)
        .then(res => res.json())
        .then(bloques => {
          bloques.forEach(b => {
            const div = document.createElement('div');
            div.className = 'bloque-visual';
            div.id = b.div_id;
            div.dataset.editable = b.editable ? 'true' : 'false';
            div.dataset.seccion = b.seccion;
            // estilos omitidos por brevedad
            canvas.appendChild(div);
            gsap.set(div, { x: b.x ?? 0, y: b.y ?? 0 });
          });
        });

      inicializarDrag();
      conectarMedidoresDesdeBD();
      configurarModales();
      actualizarMedidores();
    })
    .finally(() => {
      setTimeout(() => {
        loader.style.display = 'none';
        overlay.style.display = 'none';
        pendingTooltips.forEach(({ element, content }) => {
          tippy(element, { content, placement: 'top', theme: 'mi-tema', animation: 'shift-away', delay: [0, 0], arrow: true });
        });
        pendingTooltips = [];
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            centrarCanvasRobusto();
          });
        });
      }, 1600);
    });
}

function crearBloqueDato(clase, icono, variable, unidad) {
  const div = document.createElement('div');
  div.className = clase;
  div.innerHTML = `${icono} <span class="valor ${variable}"></span><div class="unidad">${unidad}</div>`;
  return div;
}





function aplicarEstilosBase(card, med) {
  card.style.position = 'absolute';
  card.style.width = med.width || '25px';
  card.style.height = med.height || '25px';
  card.style.background = med.background || 'transparent';
  card.style.border = `${med.border_width || '1px'} ${med.border_style || 'solid'} ${med.border_color || '#000'}`;
  card.style.borderRadius = med.border_radius || '0px';
  card.style.display = 'flex';
  card.style.flexDirection = 'column';
  card.style.justifyContent = med.text_vertical_align || 'center';
  card.style.alignItems = med.text_align === 'left'
    ? 'flex-start'
    : med.text_align === 'right'
    ? 'flex-end'
    : 'center';

  card.style.textAlign = med.text_align || 'center';
  card.style.color = med.text_color || '#000';
  card.style.fontSize = med.font_size || '16px';
  card.style.fontWeight = med.font_weight || 'normal';
  card.style.fontStyle = med.font_style || 'normal';
  card.style.textDecoration = med.text_decoration || 'none';
  card.style.padding = '5px';
  card.style.boxShadow = 'none';
  card.style.backgroundImage = 'none';
  card.style.backdropFilter = 'none';
  card.style.webkitBackdropFilter = 'none';

  if (med.text_content) card.innerHTML = med.text_content;
  if (med.animate_class) card.classList.add(med.animate_class);
}







function bloquearSidebar(bloquear) {
  document.querySelectorAll('#sidebar ul li').forEach(li => {
    li.style.pointerEvents = bloquear ? 'none' : 'auto';
    li.style.opacity = bloquear ? '0.5' : '1';
  });
}





function guardarSoloUnBloque(div) {
  const id = div.id;
  if (!id) return;

  const draggable = Draggable.get(div);
  const x = draggable?.x ?? 0;
  const y = draggable?.y ?? 0;

  const payload = [{
    div_id: id,
    x, y
  }];

  fetch('/api/guardar_bloques/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': document.querySelector('[name="csrf-token"]').content
    },
    body: JSON.stringify(payload),
    keepalive: true,
    priority: 'high',
  }).then(res => res.json())
    .then(data => console.log(`✅ Posición bloque ${id} guardada:`, data))
    .catch(err => console.error('❌ Error al guardar bloque:', err));
}



  let snappingActivo = false;

  function snapToGrid(x, y, gridSize = 2) {
    return {
      x: Math.round(x / gridSize) * gridSize,
      y: Math.round(y / gridSize) * gridSize
    };
  }




function activarSnapping() { snappingActivo = true; }
function desactivarSnapping() { snappingActivo = false; }

function aplicarCuadriculaSiCorresponde() {
  fetch('/api/configuracion/')
    .then(res => res.json())
    .then(data => {
      const canvas = document.getElementById('canvas');
      if (data.mostrar_cuadricula) {
        canvas.classList.add('grid-activa');
        activarSnapping();
      } else {
        canvas.classList.remove('grid-activa');
        desactivarSnapping();
      }
    });
}
  
  function inicializarDrag() {
    // Limpiar cualquier instancia anterior
    if (Draggable.get(".medidor-card")) {
      Draggable.getAll().forEach(d => d.kill());
    }
  
    document.querySelectorAll('.medidor-card').forEach(card => {
      const editable = card.dataset.editable === 'true';
      if (!editable) return;
  
      Draggable.create(card, {
        type: "x,y",
        bounds: "#canvas",
        inertia: false,
        dragResistance: 0,
        edgeResistance: 0,
        minimumMovement: 0,
  
        onPress: function () {
          panzoom.setOptions({ disablePan: true });
          this.target.classList.add('dragging');
        },
  
        onDrag: function () {
          const loaderVisible = document.getElementById('loader-seccion').style.display === 'block';
          if (loaderVisible) return;
        
          if (snappingActivo) {
            const snap = snapToGrid(this.x, this.y, 50);
            this.x = snap.x;
            this.y = snap.y;
            this.update(); // 🔁 ajusta visualmente en cada pixel
          }
        
          actualizarConexiones();
        },
  
        onRelease: function () {
          panzoom.setOptions({ disablePan: false });
          this.target.classList.remove('dragging');
          guardarSoloUnMedidor(this.target);
        }
      });
  
      const d = Draggable.get(card);
      if (d) d.update(true);
    });
  }

  
  function guardarSoloUnMedidor(card) {
    const id = card.dataset.medidor;
    const seccion = card.dataset.seccion;
    if (!id || !seccion) return;
  
    const draggable = Draggable.get(card);
    const x = draggable?.x ?? 0;
    const y = draggable?.y ?? 0;
  
    const payload = [{
      medidor_id: id,
      seccion: seccion,
      x,
      y
    }];
  
    fetch('/api/guardar_posiciones/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('[name="csrf-token"]').content
      },
      body: JSON.stringify(payload),
      keepalive: true,
      priority: 'high',
    })
      .then(res => {
        if (!res.ok) {
          throw new Error(`Error al guardar posición (${res.status})`);
        }
        return res.json();
      })
      .then(data => {
        console.log(`✅ Posición guardada para ${id} en sección ${seccion}:`, data);
      })
      .catch(err => {
        console.error('❌ Fallo al guardar posición:', err);
      });
  }
  

  
  function configurarModales() {
    document.querySelectorAll('.medidor-card').forEach(card => {
      card.addEventListener('dblclick', () => {
        const grafanaUrl = card.dataset.grafanaUrl;
        if (!grafanaUrl) return;
  
        const iframe = document.getElementById('grafanaIframe');
        const modal = document.getElementById('grafanaModal');
        const loaderModal = document.getElementById('loader');
        const loaderText = document.getElementById('loader-text');
  
        loaderText.textContent = card.querySelector('h3').textContent;
        loaderModal.style.display = 'flex';
        modal.style.display = 'flex';
        iframe.src = grafanaUrl;
  
        iframe.onload = () => loaderModal.style.display = 'none';
      });
    });
  }
  
  function cerrarModal() {
    document.getElementById('grafanaModal').style.display = 'none';
    document.getElementById('grafanaIframe').src = '';
    document.getElementById('loader').style.display = 'none';
  }
  
  function descargarDatosMensuales() {
    alert('Descargando datos mensuales...');
  }
  
  function cerrarSesion() {
    window.location.href = '/menu';
  }
  






  
  function centrarCanvasRobusto() {
    const wrapper = document.getElementById('canvas-wrapper');
    const zoomDeseado = 0.5;
  
    // Establece el zoom primero de forma explícita
    panzoom.zoom(zoomDeseado);
  
    const canvasCenterX = 25000 / 2;
    const canvasCenterY = 10000 / 2;
  
    const wrapperRect = wrapper.getBoundingClientRect();
    const scale = panzoom.getScale();
  
    // Cálculo de pan para centrar (x, y) relativo al nuevo scale
    const panX = wrapperRect.width / 2 - canvasCenterX * scale;
    const panY = wrapperRect.height / 2 - canvasCenterY * scale;
  
    // Usa pan() por separado, NO setTransform()
    panzoom.pan(panX, panY);
  
    console.log("🎯 Canvas centrado", { zoom: zoomDeseado, panX, panY });
  }
  
  
  
  


  
  













  
  
  
  // Arreglo con estilos predefinidos de conexiones personalizadas
  const estilosConexiones = [
    // === 🧊 ESTÁTICOS (15) ===
    { color: '#1f7cce', size: 2, path: 'grid', endPlug: 'behind' },     // cyan-grid
    { color: '#faee5d', size: 2, path: 'grid', endPlug: 'behind' }, // red-straight
    { color: '#4caf50', size: 3, path: 'fluid', endPlug: 'arrow1' },    // green-fluid
    { color: '#ff9800', size: 6, path: 'arc', endPlug: 'arrow3' },      // orange-arc
    { color: '#3f51b5', size: 4, path: 'magnet', endPlug: 'disc' },     // blue-magnet
    { color: '#9c27b0', size: 5, path: 'arc', endPlug: 'arrow1' },      // purple-curve
    { color: '#607d8b', size: 4, path: 'straight', endPlug: 'arrow3' }, // gray-straight
    { color: '#e91e63', size: 4, path: 'fluid', endPlug: 'disc' },      // pink-line
    { color: '#8bc34a', size: 5, path: 'grid', endPlug: 'arrow3' },     // lime-grid
    { color: '#ffc107', size: 4, path: 'arc', endPlug: 'square' },      // amber-path
    { color: '#cddc39', size: 3, path: 'straight', endPlug: 'dot' },
    { color: '#9e9e9e', size: 3, path: 'fluid', endPlug: 'disc' },
    { color: '#795548', size: 5, path: 'grid', endPlug: 'behind' },
    { color: '#ff5722', size: 5, path: 'magnet', endPlug: 'arrow2' },
    { color: '#673ab7', size: 4, path: 'arc', endPlug: 'behind' },
  
    // === ⚡ ANIMADAS (15) ===
    { color: '#5c5c5c', size: 2, path: 'grid', endPlug: 'behind', dash: { animation: true } }, // ani-pink-grid
    { color: '#f79b40', size: 2, path: 'grid', endPlug: 'behind', dash: { animation: true } },  // ani-orange-arc
    { color: '#1f7cce', size: 2, path: 'grid', endPlug: 'behind', dash: { animation: true } },  // ani-blue-fluid
    { color: '#ff0000', size: 2, path: 'grid', endPlug: 'behind', dash: { animation: true } }, // ani-red-straight
    { color: '#3aff00', size: 2, path: 'grid', endPlug: 'behind', dash: { animation: true } },   // ani-teal-magnet
    { color: '#ffec00', size: 2, path: 'grid', endPlug: 'behind', dash: { animation: true } },     // ani-indigo-dash
    { color: '#ffeb3b', size: 2, path: 'arc', endPlug: 'disc', dash: { animation: true } },        // ani-yellow-blink
    { color: '#00ffff', size: 2, path: 'fluid', endPlug: 'arrow3', dash: { animation: true } },    // ani-cyan-fade
    { color: '#4caf50', size: 2, path: 'grid', endPlug: 'dot', dash: { animation: true } },        // ani-green-pulse
    { color: '#9c27b0', size: 2, path: 'arc', endPlug: 'arrow1', dash: { animation: true } },      // ani-violet-spark
    { color: '#795548', size: 2, path: 'fluid', endPlug: 'square', dash: { animation: true } },    // ani-brown-glow
    { color: '#607d8b', size: 2, path: 'arc', endPlug: 'behind', dash: { animation: true } },      // ani-charcoal-arc
    { color: '#880e4f', size: 2, path: 'fluid', endPlug: 'arrow3', dash: { animation: true } },    // ani-maroon-fluid
    { color: '#f5f5dc', size: 2, path: 'magnet', endPlug: 'disc', dash: { animation: true } },     // ani-beige-magnet
    { color: '#001f3f', size: 2, path: 'arc', endPlug: 'arrow2', dash: { animation: true } },      // ani-navy-curve
  ];
  
  const estilosConexionesMap = {
    "azul-solido": estilosConexiones[0],
    "yellow-straight": estilosConexiones[1],
    "green-fluid": estilosConexiones[2],
    "orange-arc": estilosConexiones[3],
    "blue-magnet": estilosConexiones[4],
    "purple-curve": estilosConexiones[5],
    "gray-straight": estilosConexiones[6],
    "pink-line": estilosConexiones[7],
    "lime-grid": estilosConexiones[8],
    "amber-path": estilosConexiones[9],
  
    "ani-pink-grid": estilosConexiones[15],
    "ani-orange-arc": estilosConexiones[16],
    "ani-blue-fluid": estilosConexiones[17],
    "ani-red-straight": estilosConexiones[18],
    "ani-green-magnet": estilosConexiones[19],
    "ani-yellow-dash": estilosConexiones[20],
    "ani-yellow-blink": estilosConexiones[21],
    "ani-cyan-fade": estilosConexiones[22],
    "ani-green-pulse": estilosConexiones[23],
    "ani-violet-spark": estilosConexiones[24],
    "ani-brown-glow": estilosConexiones[25],
    "ani-charcoal-arc": estilosConexiones[26],
    "ani-maroon-fluid": estilosConexiones[27],
    "ani-beige-magnet": estilosConexiones[28],
    "ani-navy-curve": estilosConexiones[29],
  };
  
  

  // Variable global temporal para seleccionar estilo de prueba
  let estiloSeleccionado = 0;

  function conectarMedidoresDesdeBD() {
      fetch(`/api/conexiones/?seccion=${encodeURIComponent(seccionActual)}`)
      .then(res => res.json())
      .then(conexionesConfig => {
        conexionesConfig.forEach(({ origen_id, destino_id, start_socket, end_socket, seccion, estilo_linea }) => {
          const origen = [...document.querySelectorAll(`[data-medidor="${origen_id}"], [id="${origen_id}"]`)]
            .find(el => el.dataset.seccion === seccion);
          const destino = [...document.querySelectorAll(`[data-medidor="${destino_id}"], [id="${destino_id}"]`)]
            .find(el => el.dataset.seccion === seccion);

          if (!origen || !destino) {
            console.warn(`⚠️ No se encontró origen o destino para sección: ${seccion} (${origen_id} → ${destino_id})`);
            return;
          }

          // Buscar el estilo correspondiente por su "clave"
          const estilo = estilosConexionesMap[estilo_linea] || estilosConexionesMap['cyan-grid'];

          const linea = new LeaderLine(origen, destino, {
            startSocket: start_socket,
            endSocket: end_socket,
            ...estilo
          });

          conexiones.push(linea);
        });
      });
    }

  function actualizarConexiones() {
    if (!window.LeaderLine || !conexiones.length) return;
    conexiones.forEach(linea => linea.position());
  }

  

function actualizarMedidores() {
  document.querySelectorAll('.medidor-card').forEach(card => {
    const categoria = card.dataset.categoria;
    if (!['medidor', 'energia_sola', 'medidorglp', 'medidordiesel','medidorvapor','medidorflujometro' ].includes(categoria)) return;

    const medidorId = card.dataset.medidor;

    fetch(`/api/consumos/${medidorId}/`)
      .then(response => {
        if (!response.ok || response.status === 204) return null;
        return response.json();
      })
      .then(data => {
        if (!data) return;

        const energiaElement = card.querySelector('.energia_total');
        const potenciaElement = card.querySelector('.potencia_actual');
        const kgElement = card.querySelector('.kg_total');

        if (energiaElement && data.energia_total_kwh !== undefined) {
          energiaElement.textContent = data.energia_total_kwh;
        }

        if (potenciaElement && data.potencia_total_kw !== undefined) {
          potenciaElement.textContent = data.potencia_total_kw;
        }

        if (kgElement && data.kg_total !== undefined) {
          kgElement.textContent = data.kg_total;
        }

        actualizarEstadoVisualMedidor(card, data.energia_total_kwh, data.potencia_total_kw);
      })
      .catch(error => {
        console.error(`Error al actualizar medidor ${medidorId}:`, error);
      });
  });
}





function actualizarEstadoVisualMedidor(card, energia, potencia) {
  const energiaVal = potencia === "--" ? 0 : parseFloat(potencia);

  const h3 = card.querySelector('h3');  // 🎯 Capturamos el h3 interno

  if (!h3) return; // Seguridad: si no existe, no falla

  if (energiaVal > 0) {
    card.style.backgroundColor = "#11c414"; // 🟢 fondo verde
    h3.style.background = "linear-gradient(180deg, #000000 0%, #000000 100%)"; // Fondo negro para título
    h3.style.webkitBackgroundClip = "text";
    h3.style.webkitTextFillColor = "transparent";
  } else {
    card.style.backgroundColor = "#909090"; // 🔴 fondo gris
    h3.style.background = "linear-gradient(180deg, #ffffff 0%, #ffffff 100%)"; // Fondo blanco para título
    h3.style.webkitBackgroundClip = "text";
    h3.style.webkitTextFillColor = "transparent";
  }
}

  function bucleConexiones() {
    if (window.LeaderLine && conexiones.length) {
      conexiones.forEach(linea => linea.position());
    }
    requestAnimationFrame(bucleConexiones); // 🚀 constante
  }




  
    
  window.onload = () => {
    document.getElementById('loader-monitoreo').style.display = 'none';
  
    const canvas = document.getElementById('canvas');
    const canvasWrapper = document.getElementById('canvas-wrapper');
  
    panzoom = Panzoom(canvas, {
      canvas: false,
      contain: 'outside',
      disablePan: false,
      disableZoom: false,
      minScale: 0.14,
      maxScale: 1.2,
    });
  
    canvasWrapper.addEventListener('wheel', panzoom.zoomWithWheel);
  
    // 👇 Usa MutationObserver en lugar de panzoom.on()
    const observer = new MutationObserver(() => {
      actualizarConexiones();
    });
  
    observer.observe(canvas, {
      attributes: true,
      attributeFilter: ['style'],
    });
  
    aplicarCuadriculaSiCorresponde();
    cambiarCanvas('Sala de Calderas');
  };
  