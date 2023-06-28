
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

    function eliminarMotivo(id, url) {
        Swal.fire({
            "title": "¿Desea eliminar este proveedor?",
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