starts_checked = [
    "RMI",
    "RS",
    "RBS",
    "BS",
    "BTree",
    "FAST",
    "PGM",
    "ART",
]

for (const indexName of starts_checked) {
    document.getElementById(indexName).checked = true;
}

$(document).ready(function() {
    var filter_magic = function(e) {
        var trs = jQuery(`.tables tr:not(:first)`);
        trs.hide();
        jQuery('input[type="checkbox"][name="filter"]').each(function() {
            if (jQuery(this).is(':checked')) {
                var val = jQuery(this).val();
                trs.each(function() {
                    var tr = jQuery(this);
                    var td = tr.find('td:nth-child(1)');
                    var dataset = tr.find('td:nth-child(7)');
                    if (td.text().trim() === val && dataset.text().trim() === $("#dataswitch").val()) {
                        tr.show();
                    }
                });
            }
        });
        annotate();
    };

    jQuery('input[type="checkbox"][name="filter"]').on('change', filter_magic);
    $("#dataswitch").on('change', filter_magic);
    $('.tables td:nth-child(7), tr:nth-child(7), th:nth-child(7)').hide();
    filter_magic();
});