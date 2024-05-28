$(document).ready(function() {
    const link = document.getElementById('confirmDelete');
    if (link) {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            Swal.fire({
            title: '¿Estás seguro?',
            text: 'Esta acción no se puede deshacer',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Sí, continuar',
            cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = link.href;
                }
            });
        });
    }

    $('#datatable').DataTable({
        order: []
    });

    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    });
});