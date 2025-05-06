document.addEventListener('DOMContentLoaded', function () {
    const seccionField = document.querySelector('select[name="seccion_ui"]');
    if (seccionField) {
        seccionField.addEventListener('change', function () {
            this.form.submit();  // recarga el form al cambiar sección
        });
    }
});
