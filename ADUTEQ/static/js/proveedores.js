
function eliminarProveedor(id, estado) {

    var valor;

    if (estado == 'True') {
        valor = 1;
        Swal.fire({
            "title": "¿Desea dar de baja a este proveedor?",
            "text": "Luego podrá editar al proveedor nuevamente",
            "icon": "question",
            "showCancelButton": true,
            "cancelButtonText": "Cancelar",
            "confirmButtonText": "Si",
            "confirmButtonColor": "blue",
            "cancelButtonColor": "red"
        })
            .then(function (result) {
                if (result.isConfirmed) {
                    window.location.href = "/deleteProveedor/" + id + '/' + valor + '/';
                }
            })
    }
    else {
        valor = 0;

        Swal.fire({
            "title": "¿Desea habilitar a este proveedor?",
            "icon": "question",
            "showCancelButton": true,
            "cancelButtonText": "Cancelar",
            "confirmButtonText": "Si",
            "confirmButtonColor": "blue",
            "cancelButtonColor": "red"
        })
            .then(function (result) {
                if (result.isConfirmed) {
                    window.location.href = "/deleteProveedor/" + id + '/' + valor + '/';
                }
            })
    }

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

