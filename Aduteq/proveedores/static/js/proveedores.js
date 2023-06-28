
    function eliminarProveedor(id) {
        Swal.fire({
            "title": "¿Desea eliminar este proveedor?",
            "text": "Luego podrá editar al proveedor nuevamente",
            "icon": "question",
            "showCancelButton": true,
            "cancelButtonText": "Cancelar",
            "confirmButtonText": "Si, eliminar",
            "confirmButtonColor": "blue",
            "cancelButtonColor": "red"
        })
            .then(function (result) {
                if (result.isConfirmed) {
                    window.location.href = "/deleteProveedor/" + id
                }
            })
    }

    $(document).ready(function () {
        $('#barbusqueda').on('input', function () {
            var query = $(this).val().trim();
            if (query !== '') {
                $.ajax({
                    url: '/busqueda/',
                    type: 'GET',
                    data: { 'query': query },
                    success: function (response) {
                        $('#searchResults').html(response);
                        $('#searchResults').show();
                    }
                });
            } else {
                $('#searchResults').empty();
                $('#searchResults').hide();
            }
        });
    });

