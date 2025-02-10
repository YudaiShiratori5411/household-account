document.addEventListener('DOMContentLoaded', function() {
    // 月別支出グラフ
    const monthlyCtx = document.getElementById('monthlyChart').getContext('2d');
    new Chart(monthlyCtx, {
        type: 'line',
        data: {
            labels: monthlyLabels,  // テンプレートから渡されるデータ
            datasets: [{
                label: '月別支出',
                data: monthlyData,  // テンプレートから渡されるデータ
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString() + '円';
                        }
                    }
                }
            }
        }
    });

    // カテゴリ別支出グラフ
    const categoryCtx = document.getElementById('categoryChart').getContext('2d');
    new Chart(categoryCtx, {
        type: 'doughnut',
        data: {
            labels: categoryLabels,  // テンプレートから渡されるデータ
            datasets: [{
                data: categoryData,  // テンプレートから渡されるデータ
                backgroundColor: [
                    'rgb(255, 99, 132)',
                    'rgb(54, 162, 235)',
                    'rgb(255, 206, 86)',
                    'rgb(75, 192, 192)',
                    'rgb(153, 102, 255)',
                    'rgb(255, 159, 64)'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
});