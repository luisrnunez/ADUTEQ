
    $(document).ready(function () {
        $('#editarproveedor').on('submit', function (event) {
            event.preventDefault();

            var formData = new FormData(this);

            $.ajax({
                url: '/editarPro/',
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
                            "title": "¿Desea guardar los cambios de este proveedor?",
                            "text": "Esta acción no se puede deshacer",
                            "icon": "question",
                            "showCancelButton": true,
                            "cancelButtonText": "Cancelar",
                            "confirmButtonText": "Si, guardar",
                            "confirmButtonColor": "red",
                            "cancelButtonColor": "blue"
                        }).then(function (result) {
                            if (result.isConfirmed) {
                                window.location.href = '/proveedores/'
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

    function validarEspacios(input) {
        if (input.value.includes(' ')) {
            input.setCustomValidity('No se permiten espacios en blanco');
        } else {
            input.setCustomValidity('');
        }
    }

    function verificarExistenciaNombre(nombre) {
        var csrfToken = '{{ csrf_token }}';
        $.ajax({
            url: '/verificarexiste/',
            type: 'POST',
            data: {
            'nombre': nombre,
            'csrfmiddlewaretoken': csrfToken
        },
            success: function(response) {
            if (response.existe) {
                $('#alerta').text('Ya existe un proveedor con este nombre');
            } else {
                $('#alerta').text('');
            }
        }
        });
    }