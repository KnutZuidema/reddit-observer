$(function () {
    let headers = $('.sort > thead > tr > th');
    let body_rows = $('.sort > tbody > tr').get();
    headers.click(function () {
        let header = $(this);
        header.toggleClass('sorted-ascending');
        let index = headers.index(header);
        body_rows.sort(function (item1, item2) {
            item1 = item1.children[index].innerText;
            item2 = item2.children[index].innerText;
            if (!isNaN(item1)){
                item1 = parseInt(item1);
                item2 = parseInt(item2);
            }
            return item1 < item2
        });
        if (!header.hasClass('sorted-ascending')){
            body_rows.reverse();
        }
        for (let item in body_rows){
            $('.sort tbody').append(body_rows[item]);
        }
    })
});