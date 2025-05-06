let panzoom, conexiones = [];
let pendingTooltips = []; // ✅ Acumulamos tooltips que se activarán después del loader
  function cambiarCanvas(seccion) {
  const canvas = document.getElementById('canvas');
  const loader = document.getElementById('loader-seccion');
  const overlay = document.getElementById('overlay-canvas');
  const sidebar = document.getElementById('sidebar');

  

  // 🚨 Si el loader está visible, no permitimos cambiar sección
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
  



  // canvas.innerHTML = '';

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
      
        // === ✏️ CATEGORÍA TEXTO personalizada ===
        if (med.categoria_visual === 'texto') {
          const card = document.createElement('div');
          card.className = 'medidor-card'; // 👈 Necesario para que se pueda mover
          card.dataset.medidor = med.medidor_id;
          card.dataset.editable = med.editable ? 'true' : 'false';
          card.dataset.seccion = med.seccion;
          card.dataset.categoria = 'texto'; // por si quieres filtrar después
        
          // ⚙️ Estilos personalizados
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
          card.style.boxShadow = 'none'; // ✅ quitar sombra
          card.style.backgroundImage = 'none'; // ✅ quitar gradientes si existen

          card.style.backdropFilter = 'none';           // ❌ Elimina desenfoque
          card.style.webkitBackdropFilter = 'none';     // ❌ Para compatibilidad con Safari
          card.style.backgroundImage = 'none';          // ❌ Elimina gradientes heredados
          card.style.background = 'transparent';        // ✅ Fondo realmente transparente
          card.style.boxShadow = 'none';                // ❌ Quita sombra si existe

        
          if (med.text_content) card.innerHTML = med.text_content;
          if (med.animate_class) card.classList.add(med.animate_class);
        
          canvas.appendChild(card);
          gsap.set(card, { x: med.x ?? 0, y: med.y ?? 0 });
        
          return; // ⛔ importante para evitar continuar con lógica de medidores normales
        }
      
        // === 🔷 TÍTULO ===
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
              med.alineacion_vertical === 'bottom' ? 'flex-end' :
              'center';
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
      
        // === ⚡ SOLO ENERGÍA o NORMAL ===
        else {
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
      
          const kWh = document.createElement('div');
          kWh.className = 'kWh';
          kWh.innerHTML = `🔄 <span class="valor energia_total"></span><div class="unidad">kWh</div>`;
          card.appendChild(kWh);
      
          if (med.categoria_visual !== 'energia_sola') {
            const kW = document.createElement('div');
            kW.className = 'kW';
            kW.innerHTML = `⚡ <span class="valor potencia_actual"></span><div class="unidad">kW</div>`;
            card.appendChild(kW);
          }
        }
      
        canvas.appendChild(card);
        gsap.set(card, { x: med.x ?? 0, y: med.y ?? 0 });
      });









      // Cargar bloques visuales personalizados
      console.log("🔍 Cargando bloques para la sección:", seccion);
      fetch(`/api/bloques/?seccion=${encodeURIComponent(seccion)}`)
        .then(res => res.json())
        .then(bloques => {
          bloques.forEach(b => {
            const div = document.createElement('div');
            div.className = 'bloque-visual';
            div.id = b.div_id;
            div.dataset.editable = b.editable ? 'true' : 'false';
            div.dataset.seccion = b.seccion;

            // Estilos básicos
            div.style.position = 'absolute';
            div.style.width = b.width || '100px';
            div.style.height = b.height || '100px';
            div.style.background = b.background || 'transparent';

            // Nuevo: incluir estilo de borde
            const borderWidth = b.border_width || '0px';
            const borderColor = b.border_color || '#000';
            const borderStyle = b.border_style || 'solid'; // 🚀 NUEVO
            div.style.border = `${borderWidth} ${borderStyle} ${borderColor}`;
            
            div.style.borderRadius = b.border_radius || '0px';

            // Estilos de texto
            div.style.display = 'flex';
            div.style.flexDirection = 'column'; // para que justifyContent sea vertical
            div.style.justifyContent = b.text_vertical_align || 'center'; // vertical (arriba, centro, abajo)

            // Ajuste de alineación horizontal
            if (b.text_align === 'left') div.style.alignItems = 'flex-start';
            else if (b.text_align === 'center') div.style.alignItems = 'center';
            else if (b.text_align === 'right') div.style.alignItems = 'flex-end';

            div.style.textAlign = b.text_align || 'center'; // Alineación de texto dentro del bloque
            div.style.color = b.text_color || '#000';
            div.style.fontSize = b.font_size || '16px';

            // 🚀 NUEVOS estilos de decoración de texto:
            div.style.fontWeight = b.font_weight || 'normal';   // normal o bold
            div.style.fontStyle = b.font_style || 'normal';      // normal o italic
            div.style.textDecoration = b.text_decoration || 'none'; // none o underline

            div.style.padding = '5px'; // Opcional: para separación interna

            // Contenido interno del div
            if (b.text_content) {
                div.innerHTML = b.text_content;
            }

            // Animación si existe
            if (b.animate_class) {
                div.classList.add(b.animate_class);
            }

            // Posición inicial en el canvas
            gsap.set(div, { x: b.x ?? 0, y: b.y ?? 0 });

            canvas.appendChild(div);
          });


        });



        
      inicializarDrag();
      conectarMedidoresDesdeBD();
      configurarModales();
      actualizarMedidores();

      
       // ⏳ Esperar a que DOM termine de renderizar, luego centrar
      setTimeout(() => {
        requestAnimationFrame(() => {
          centrarCanvas();
        });
      }, 100);
      


    })

      
    .finally(() => {
      // ⏳ Espera que el loader desaparezca
      setTimeout(() => {
        loader.style.display = 'none';
        overlay.style.display = 'none';

        // ✅ Ahora activamos todos los tooltips pendientes
        pendingTooltips.forEach(({ element, content }) => {
          tippy(element, {
            content: content,
            placement: 'top',
            theme: 'mi-tema',
            animation: 'shift-away',
            delay: [0, 0],
            arrow: true,
          });
        });

        pendingTooltips = []; // 🧹 limpieza
      }, 3000);
    });
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
  
  function centrarCanvas() {
    const wrapper = document.getElementById('canvas-wrapper');
    const canvas = document.getElementById('canvas');
  
    requestAnimationFrame(() => {
      const wrapperRect = wrapper.getBoundingClientRect();
  
      const zoomDeseado = 0.6;
      panzoom.zoom(zoomDeseado); // ✅ Primero aplicar el zoom deseado
  
      const scale = panzoom.getScale();
  
      const canvasWidth = canvas.scrollWidth;
      const canvasHeight = canvas.scrollHeight;
  
      const panX = (wrapperRect.width / 2 - canvasWidth * scale / 2);
      const panY = (wrapperRect.height / 2 - canvasHeight * scale / 2);
  
      panzoom.pan(panX, panY); // ✅ Luego centrar el canvas en base al nuevo zoom
  
      console.log('🎯 Canvas centrado en:', { panX, panY, scale, canvasWidth, canvasHeight });
    });
  }
  
  
  
  // Arreglo con estilos predefinidos de conexiones personalizadas
  const estilosConexiones = [
    // === 🧊 ESTÁTICOS (15) ===
    { color: '#00ffff', size: 4, path: 'grid', endPlug: 'arrow3' },     // cyan-grid
    { color: '#f44336', size: 5, path: 'straight', endPlug: 'arrow2' }, // red-straight
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
    { color: '#343534', size: 3, path: 'grid', endPlug: 'behind', dash: { animation: true } }, // ani-pink-grid
    { color: '#ff9800', size: 4, path: 'arc', endPlug: 'arrow2', dash: { animation: true } },  // ani-orange-arc
    { color: '#2196f3', size: 3, path: 'fluid', endPlug: 'disc', dash: { animation: true } },  // ani-blue-fluid
    { color: '#f44336', size: 5, path: 'straight', endPlug: 'behind', dash: { animation: true } }, // ani-red-straight
    { color: '#009688', size: 4, path: 'magnet', endPlug: 'square', dash: { animation: true } },   // ani-teal-magnet
    { color: '#3f51b5', size: 3, path: 'grid', endPlug: 'arrow1', dash: { animation: true } },     // ani-indigo-dash
    { color: '#ffeb3b', size: 4, path: 'arc', endPlug: 'disc', dash: { animation: true } },        // ani-yellow-blink
    { color: '#00ffff', size: 5, path: 'fluid', endPlug: 'arrow3', dash: { animation: true } },    // ani-cyan-fade
    { color: '#4caf50', size: 3, path: 'grid', endPlug: 'dot', dash: { animation: true } },        // ani-green-pulse
    { color: '#9c27b0', size: 4, path: 'arc', endPlug: 'arrow1', dash: { animation: true } },      // ani-violet-spark
    { color: '#795548', size: 5, path: 'fluid', endPlug: 'square', dash: { animation: true } },    // ani-brown-glow
    { color: '#607d8b', size: 4, path: 'arc', endPlug: 'behind', dash: { animation: true } },      // ani-charcoal-arc
    { color: '#880e4f', size: 3, path: 'fluid', endPlug: 'arrow3', dash: { animation: true } },    // ani-maroon-fluid
    { color: '#f5f5dc', size: 4, path: 'magnet', endPlug: 'disc', dash: { animation: true } },     // ani-beige-magnet
    { color: '#001f3f', size: 4, path: 'arc', endPlug: 'arrow2', dash: { animation: true } },      // ani-navy-curve
  ];
  
  const estilosConexionesMap = {
    "cyan-grid": estilosConexiones[0],
    "red-straight": estilosConexiones[1],
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
    "ani-teal-magnet": estilosConexiones[19],
    "ani-indigo-dash": estilosConexiones[20],
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
      fetch('/api/conexiones/')
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
    if (card.dataset.categoria === 'titulo') return; // ⛔ saltar títulos
    const medidorId = card.dataset.medidor;

    fetch(`/api/consumos/${medidorId}/`)  // 🚀 Llamamos a tu vista en Django
      .then(response => response.json())
      .then(data => {
        const energiaElement = card.querySelector('.energia_total');
        const potenciaElement = card.querySelector('.potencia_actual');

        if (energiaElement && data.energia_total_kwh !== undefined) {
          energiaElement.textContent = data.energia_total_kwh;
        }

        if (potenciaElement && data.potencia_total_kw !== undefined) {
          potenciaElement.textContent = data.potencia_total_kw;
        }

        // 🔥 Aquí llamamos a la función que decide el color
        actualizarEstadoVisualMedidor(card, data.energia_total_kwh, data.potencia_total_kw);
      })
      .catch(error => {
        console.error(`Error al actualizar medidor ${medidorId}:`, error);
      });
  });
}


function actualizarEstadoVisualMedidor(card, energia, potencia) {
  const energiaVal = energia === "--" ? 0 : parseFloat(energia);

  const h3 = card.querySelector('h3');  // 🎯 Capturamos el h3 interno

  if (!h3) return; // Seguridad: si no existe, no falla

  if (energiaVal === 0) {
    card.style.backgroundColor = "#a83232"; // 🔴 fondo rojo
    h3.style.background = "linear-gradient(180deg, #ffffff 0%, #ffffff 100%)"; // Fondo blanco para título
    h3.style.webkitBackgroundClip = "text";
    h3.style.webkitTextFillColor = "transparent";
  } else {
    card.style.backgroundColor = "#11c414"; // 🟢 fondo verde
    h3.style.background = "linear-gradient(180deg, #000000 0%, #000000 100%)"; // Fondo negro para título
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
  
    panzoom = Panzoom(document.getElementById('canvas'), {
      canvas: true,
      contain: 'outside',
      disablePan: false,
      disableZoom: false,
      minScale: 0.5,     // 🔻 Qué tanto puedes alejar
      maxScale: 1.2,     // 🔺 Qué tanto puedes acercar
    });
  
    const canvasWrapper = document.getElementById('canvas-wrapper');
    canvasWrapper.addEventListener('wheel', panzoom.zoomWithWheel);
  


    cambiarCanvas('Vista General Planta');
    aplicarCuadriculaSiCorresponde();
    bucleConexiones();
    // setInterval(() => {
    //   actualizarMedidores(); 
    // }, 5000);
  };