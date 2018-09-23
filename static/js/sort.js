$(function () {
    let headers = $('.sort > thead > tr > th');
    let body_rows = $('.sort > tbody > tr').get();
    headers.click(function () {
        let header = $(this);
        header.toggleClass('sorted-ascending');
        let index = headers.index(header);
        body_rows.sort(function (item1, item2) {
            let value1 = item1.children[index].innerText;
            let value2 = item2.children[index].innerText;
            if (isNaN(value1)){
                return value1 < value2
            }
            value1 = parseInt(value1);
            value2 = parseInt(value2);
            return value1 < value2
        });
        if (!header.hasClass('sorted-ascending')){
            body_rows.reverse();
        }
        for (let item in body_rows){
            $('.sort tbody').append(body_rows[item]);
        }
    })
});