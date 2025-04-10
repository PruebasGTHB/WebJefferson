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
    });
  });

  // -------------------- BOTONES NORMALES --------------------
  let clicado = null;
  const idGuardado = sessionStorage.getItem(`botonSeleccionado_${vistaKey}`);
  const urlGuardada = sessionStorage.getItem(`iframeSeleccionado_${vistaKey}`);

  // Al loguearse por primera vez, forzar el botón 1
  if (!idGuardado || !urlGuardada) {
    clicado = botones[0];
    if (clicado) {
      const url = clicado.getAttribute('onclick').match(/'(.*?)'/)[1];
      iframe.src = url;
      sessionStorage.setItem(`botonSeleccionado_${vistaKey}`, clicado.id);
      sessionStorage.setItem(`iframeSeleccionado_${vistaKey}`, url);
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
});
