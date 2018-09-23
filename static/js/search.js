$(function () {
    $("#searchbox").on("keyup", function () {
        const value = $(this).val().toLowerCase();
        $("#champion_table tbody tr").filter(function () {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });
});