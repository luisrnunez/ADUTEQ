
$(document).ready(function () {
    $('#editarmotivo').on('submit', function (event) {
        event.preventDefault();

        var formData = new FormData(this);

        $.ajax({
            url: '/geditmotivo/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                if (response.status === 'error') {
                    Swal.fire({
                        "title": "Falló",
                        "text": response.message,
                        "icon": "warning"
                    })
                } else if (response.status === 'success') {
                    Swal.fire({
                        "title": "¿Desea guardar los cambios de este motivo?",
                        "text": "Luego podrá realizar cambios nuevamente",
                        "icon": "question",
                        "showCancelButton": true,
                        "cancelButtonText": "Cancelar",
                        "confirmButtonText": "Si, guardar",
                        "confirmButtonColor": "red",
                        "cancelButtonColor": "blue"
                    }).then(function (result) {
                        if (result.isConfirmed) {
                            window.location.href = '/motivos/'
                        }
                    })

                }
            },
            error: function (xhr, errmsg, err) {
                Swal.fire('Error', 'Ocurrió un error al procesar la solicitud.', 'error');
            }
        });
    });
});

function eliminarMotivo(id, url, campo) {
    Swal.fire({
        "title": "¿Desea eliminar este "+campo+"?",
        "icon": "question",
        "showCancelButton": true,
        "cancelButtonText": "Cancelar",
        "confirmButtonText": "Si, eliminar",
        "confirmButtonColor": "blue",
        "cancelButtonColor": "red"
    })
        .then(function (result) {
            if (result.isConfirmed) {
                window.location.href = url + id
            }
        })
}

$(document).ready(function () {
    $('#editarayuda').on('submit', function (event) {
        event.preventDefault();

        var formData = new FormData(this);

        $.ajax({
            url: '/editarayudaa/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                if (response.status === 'error') {
                    Swal.fire({
                        "title": "Falló",
                        "text": response.message,
                        "icon": "warning"
                    })
                } else if (response.status === 'success') {
                    Swal.fire({
                        "title": "¿Desea guardar los cambios de esta ayuda?",
                        "text": "Luego podrá realizar cambios nuevamente",
                        "icon": "question",
                        "showCancelButton": true,
                        "cancelButtonText": "Cancelar",
                        "confirmButtonText": "Si, guardar",
                        "confirmButtonColor": "red",
                        "cancelButtonColor": "blue"
                    }).then(function (result) {
                        if (result.isConfirmed) {
                            window.location.href = '/verayudas/'
                        }
                    })

                }
            },
            error: function (xhr, errmsg, err) {
                Swal.fire('Error', 'Ocurrió un error al procesar la solicitud.', 'error');
            }
        });
    });
});

$(document).ready(function () {
    $('#editarfacul').on('submit', function (event) {
        event.preventDefault();

        var formData = new FormData(this);

        $.ajax({
            url: '/editarfacultad/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                if (response.status === 'error') {
                    Swal.fire({
                        "title": "Falló",
                        "text": response.message,
                        "icon": "warning"
                    })
                } else if (response.status === 'success') {
                    Swal.fire({
                        "title": "¿Desea guardar los cambios de esta facultad?",
                        "text": "Luego podrá realizar cambios nuevamente",
                        "icon": "question",
                        "showCancelButton": true,
                        "cancelButtonText": "Cancelar",
                        "confirmButtonText": "Si, guardar",
                        "confirmButtonColor": "red",
                        "cancelButtonColor": "blue"
                    }).then(function (result) {
                        if (result.isConfirmed) {
                            window.location.href = '/listafacultades/'
                        }
                    })

                }
            },
            error: function (xhr, errmsg, err) {
                Swal.fire('Error', 'Ocurrió un error al procesar la solicitud.', 'error');
            }
        });
    });
});