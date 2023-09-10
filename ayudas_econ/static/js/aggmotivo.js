
$(document).ready(function () {
    $('#registromotivo-form').on('submit', function (event) {
        event.preventDefault();
        
        var formData = new FormData(this);

        $.ajax({
            url: '/aggmotivos/',
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
                        "title": "Éxito",
                        "text": response.message,
                        "icon": "success"
                    }).then(function (result) {
                        if (result.isConfirmed) {
                            window.location.href = "/motivos/"
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
    $('#registro-formayuda').on('submit', function (event) {
        event.preventDefault();
        
        var formData = new FormData(this);

        Swal.fire({
            title: 'Confirmación',
            text: '¿Estás seguro de que deseas guardar la aportación?',
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: 'Guardar',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: '/aggAyuda/',
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
                                "title": "Éxito",
                                "text": response.message,
                                "icon": "success"
                            }).then(function (result) {
                                if (result.isConfirmed) {
                                    window.location.href = "/verayudas/"
                                }
                            })
                        }
                    },
                    error: function (xhr, errmsg, err) {
                        Swal.fire('Error', 'Ocurrió un error al procesar la solicitud.', 'error');
                    }
                });
            }
        });
    });
});

$(document).ready(function () {
    $('#regisfacultad').on('submit', function (event) {
        event.preventDefault();
        
        var formData = new FormData(this);

        $.ajax({
            url: '/aggFacultad/',
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
                        "title": "Éxito",
                        "text": response.message,
                        "icon": "success"
                    }).then(function (result) {
                        if (result.isConfirmed) {
                            window.location.href = "/listafacultades/"
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