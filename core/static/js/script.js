document.addEventListener("DOMContentLoaded", function () {
  const vistaKey = window.location.pathname;
  const iframe = document.getElementById("miIframe");
  const botones = document.querySelectorAll(".botones");
  const iframeDropdown = document.querySelector(".dropdown-menu-container-botones");
  const iframeToggle = iframeDropdown?.querySelector(".dropdown-toggle");
  const iframeButtons = iframeDropdown?.querySelectorAll(".dropdown-boton-iframe");

  // -------------------- MENÚ BANNER --------------------
  const bannerDropdown = document.querySelector(".dropdown-menu-container");
  const bannerToggle = bannerDropdown?.querySelector(".dropdown-toggle");
  const bannerLinks = bannerDropdown?.querySelectorAll(".dropdown-links a");

  const storedBannerText = localStorage.getItem("selectedDropdownText_banner");
  const activoMenu = document.querySelector(".menu-content.activo");

  if (activoMenu && bannerToggle) {
    bannerToggle.textContent = activoMenu.textContent.trim() + " ▾";
    localStorage.setItem("selectedDropdownText_banner", activoMenu.textContent.trim());
  } else if (storedBannerText && bannerToggle) {
    bannerToggle.textContent = storedBannerText + " ▾";
  }

  bannerLinks?.forEach(link => {
    link.addEventListener("click", function () {
      localStorage.setItem("selectedDropdownText_banner", this.textContent.trim());
    });
  });

  // -------------------- BOTÓN IFRAME MENÚ --------------------
  const storedIframeText = sessionStorage.getItem(`iframeText_${vistaKey}`);
  const storedIframeURL = sessionStorage.getItem(`iframeSeleccionado_${vistaKey}`);

  if (storedIframeText && iframeToggle) {
    iframeToggle.textContent = storedIframeText + " ▾";
  }

  if (storedIframeURL && iframe) {
    iframe.src = storedIframeURL;
  }

  iframeButtons?.forEach(button => {
    button.addEventListener("click", function () {
      const newText = this.textContent;
      const newURL = this.getAttribute("onclick").match(/'(.*?)'/)[1];

      iframe.src = newURL;
      if (iframeToggle) iframeToggle.textContent = newText + " ▾";

      sessionStorage.setItem(`iframeText_${vistaKey}`, newText);
      sessionStorage.setItem(`iframeSeleccionado_${vistaKey}`, newURL);

      // Marcar opción activa
      iframeButtons.forEach(btn => btn.classList.remove("iframe-activo"));
      this.classList.add("iframe-activo");

      // Cerrar menú
      iframeDropdown.classList.remove("active");
    });
  });

  // -------------------- BOTONES NORMALES --------------------
  let clicado = null;
  const idGuardado = sessionStorage.getItem(`botonSeleccionado_${vistaKey}`);
  const urlGuardada = sessionStorage.getItem(`iframeSeleccionado_${vistaKey}`);

  if (!idGuardado || !urlGuardada) {
    clicado = botones[0];
    if (clicado) {
      const url = clicado.getAttribute('onclick').match(/'(.*?)'/)[1];
      iframe.src = url;
      clicado.classList.add('clicado');
      sessionStorage.setItem(`botonSeleccionado_${vistaKey}`, clicado.id);
      sessionStorage.setItem(`iframeSeleccionado_${vistaKey}`, url);
      sessionStorage.setItem(`iframeText_${vistaKey}`, clicado.textContent.trim());
      if (iframeToggle) iframeToggle.textContent = clicado.textContent.trim() + " ▾";
    }
  } else {
    clicado = document.getElementById(idGuardado);
    if (clicado) {
      clicado.classList.add('clicado');
      if (iframe && storedIframeURL) iframe.src = storedIframeURL;
    }
  }

  botones.forEach(function (boton) {
    boton.addEventListener('click', function () {
      if (boton === clicado) return;

      if (clicado) clicado.classList.remove('clicado');
      boton.classList.add('clicado');
      const url = boton.getAttribute('onclick').match(/'(.*?)'/)[1];

      iframe.src = url;
      sessionStorage.setItem(`botonSeleccionado_${vistaKey}`, boton.id);
      sessionStorage.setItem(`iframeSeleccionado_${vistaKey}`, url);
      sessionStorage.setItem(`iframeText_${vistaKey}`, boton.textContent.trim());

      if (iframeToggle) iframeToggle.textContent = boton.textContent.trim() + " ▾";

      clicado = boton;
    });
  });

  // -------------------- DROPDOWN CLOSURE --------------------
  const dropdownContainers = document.querySelectorAll(".dropdown-menu-container, .dropdown-menu-container-botones");

  dropdownContainers.forEach(container => {
    const toggleButton = container.querySelector(".dropdown-toggle");

    if (toggleButton) {
      toggleButton.addEventListener("click", function (e) {
        e.stopPropagation();
        dropdownContainers.forEach(other => {
          if (other !== container) other.classList.remove("active");
        });
        container.classList.toggle("active");
      });
    }
  });

  document.addEventListener("click", function (e) {
    dropdownContainers.forEach(container => {
      if (!container.contains(e.target)) container.classList.remove("active");
    });
  });

  // -------------------- EFECTO DE CARGA --------------------
  const contenidoPrincipal = document.getElementById('contenido__principal');
  if (contenidoPrincipal) {
    setTimeout(() => {
      contenidoPrincipal.classList.remove('contenido__principal');
      contenidoPrincipal.classList.add('contenido__principal_visible');
    }, 1000);
  }




  // -------------------- LOGOUT MENU2 --------------------
  const logoutToggle2 = document.getElementById("userMenuToggle2");
  const logoutMenu2 = document.getElementById("userDropdown2");

  if (logoutToggle2 && logoutMenu2) {
    logoutToggle2.addEventListener("click", function (e) {
      e.stopPropagation();
      logoutMenu2.classList.toggle("show");
    });

    document.addEventListener("click", function (e) {
      if (!logoutMenu2.contains(e.target) && e.target !== logoutToggle2) {
        logoutMenu2.classList.remove("show");
      }
    });
  }

  // -------------------- LOGOUT MENU --------------------
  const logoutToggle = document.getElementById("userMenuToggle");
  const logoutMenu = document.getElementById("userDropdown");

  if (logoutToggle && logoutMenu) {
    logoutToggle.addEventListener("click", function (e) {
      e.stopPropagation();
      logoutMenu.classList.toggle("show");
    });

    document.addEventListener("click", function (e) {
      if (!logoutMenu.contains(e.target) && e.target !== logoutToggle) {
        logoutMenu.classList.remove("show");
      }
    });
  }

  // -------------------- MENÚ HORIZONTAL ACTIVO --------------------
  const enlaces = document.querySelectorAll('.menu-content');
  enlaces.forEach(link => {
    link.addEventListener('click', function () {
      enlaces.forEach(el => el.classList.remove('activo'));
      this.classList.add('activo');
    });
  });

  // -------------------- SINCRONIZAR BOTÓN CON IFRAME ACTUAL --------------------
  function sincronizarBotonConIframe() {
    const iframeURL = new URL(iframe.src);
    const baseIframePath = iframeURL.origin + iframeURL.pathname;

    let matched = false;

    botones.forEach(boton => {
      const botonURLRaw = boton.getAttribute("onclick").match(/'(.*?)'/)?.[1];
      const botonURL = new URL(botonURLRaw, window.location.origin);
      const baseBotonPath = botonURL.origin + botonURL.pathname;

      if (baseIframePath === baseBotonPath) {
        boton.classList.add("clicado");
        matched = true;
        sessionStorage.setItem(`botonSeleccionado_${vistaKey}`, boton.id);
        if (iframeToggle) iframeToggle.textContent = boton.textContent.trim() + " ▾";
      } else {
        boton.classList.remove("clicado");
      }
    });

    if (!matched && iframeToggle) {
      iframeToggle.textContent = "Contenido externo ▾";
    }
  }

  // -------------------- MARCAR OPCIÓN ACTIVA EN MENÚ IFRAME --------------------
  function marcarOpcionIframeActual() {
    const iframeURL = new URL(iframe.src);
    const baseIframePath = iframeURL.origin + iframeURL.pathname;

    iframeButtons?.forEach(button => {
      const btnUrlRaw = button.getAttribute("onclick").match(/'(.*?)'/)?.[1];
      const btnURL = new URL(btnUrlRaw, window.location.origin);
      const baseBtnPath = btnURL.origin + btnURL.pathname;

      if (baseIframePath === baseBtnPath) {
        button.classList.add("iframe-activo");
      } else {
        button.classList.remove("iframe-activo");
      }
    });
  }

  sincronizarBotonConIframe();
  marcarOpcionIframeActual();

  iframe.addEventListener("load", () => {
    sincronizarBotonConIframe();
    marcarOpcionIframeActual();
  });
});

// Manejar apertura del modal al hacer clic en el ojo
document.querySelectorAll('.ver-panel').forEach(btn => {
  btn.addEventListener('click', () => {
      const card = btn.closest('.medidor-card');
      const grafanaUrl = card.getAttribute('data-grafana-url');
      document.getElementById('grafanaIframe').src = grafanaUrl;
      document.getElementById('grafanaModal').style.display = 'flex';
  });
});

function cerrarModal() {
  document.getElementById('grafanaModal').style.display = 'none';
  document.getElementById('grafanaIframe').src = '';
}


function cerrarModal() {
  document.getElementById('grafanaModal').style.display = 'none';
  document.getElementById('grafanaIframe').src = '';
  document.getElementById('loader').style.display = 'none';
}

document.querySelectorAll('.ver-panel').forEach(btn => {
  btn.addEventListener('click', () => {
      const card = btn.closest('.medidor-card');
      const grafanaUrl = card.getAttribute('data-grafana-url');
      const medidorNombre = card.querySelector('h3').textContent; // capturamos el nombre del medidor

      const iframe = document.getElementById('grafanaIframe');
      const modal = document.getElementById('grafanaModal');
      const loader = document.getElementById('loader');
      const loaderText = document.getElementById('loader-text');

      //Cambiar texto del loader dinámicamente
      loaderText.textContent = `${medidorNombre}`;

      loader.style.display = 'flex';
      modal.style.display = 'flex';
      iframe.src = grafanaUrl;

      iframe.onload = () => {
          loader.style.display = 'none';
      };
  });
});
