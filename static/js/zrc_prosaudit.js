




$(document).ready(function() {
    
        var table = new DataTable("#zrc_prosaudit", {
            paging: false,
            searching: false,
            info: false,
            ordering: false,
            layout: {
                bottomStart: null,
                topStart: null
            },
        });
    

    // Add event listener for opening and closing details
    $('#zrc_prosaudit tbody').on('click', 'td.details-control', function() {
        var tr = $(this).closest('tr');
        var row = table.row(tr);
        var detailsContent = $(this).find('.hidden-details').html();
        if (row.child.isShown()) {
            // Close the details
            row.child.hide();
            tr.removeClass('shown');
        } else {
            // Open the details
            row.child(detailsContent).show();
            tr.addClass('shown');
        }
    });
});