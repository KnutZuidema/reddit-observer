$(function () {
    Chart.defaults.global.defaultFontColor = 'white';
    new Chart('mentions', {
        type: 'line',
        data: {
            labels: [
                '-6 days',
                '-5 days',
                '-4 days',
                '-3 days',
                '-2 days',
                '-1 day',
                'Today',
            ],
            datasets: [{
                label: "Mentions last week",
                backgroundColor: 'darkslategrey',
                data: data
            }]
        },
        options: {}
    })
});