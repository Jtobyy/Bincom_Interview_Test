/*
$(document).ready( function () {a
    $('#myTable').DataTable();
} );*/

window.onload = function () {
    $('#selectId').on('change', () => {
        let option = $('#selectId option:selected').val()
        $('#reload').attr('href', `/polling_results/total_result/${option}`)
        reload = document.getElementById('reload')
        reload.click()
    })
}