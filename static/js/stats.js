/**
 * Script d'interactivitat per al Centre d'Estadístiques
 * Encarregat exclusivament d'inicialitzar i actualitzar Chart.js i gestionar els filtres temporals.
 */

document.addEventListener('DOMContentLoaded', function () {
    const canvas = document.getElementById('chartUserEvolution');
    if (!canvas) return;

    let chartInstance = null;

    // Inicialitzar dades de la gràfica amb la configuració inicial de Flask
    function initChart(labels, xpData, coinsData) {
        const ctx = canvas.getContext('2d');
        if (chartInstance) {
            chartInstance.destroy();
        }

        chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'XP Guanyats',
                        data: xpData,
                        borderColor: '#eab308',
                        backgroundColor: 'rgba(234, 179, 8, 0.15)',
                        fill: true,
                        tension: 0.3,
                        pointRadius: 4
                    },
                    {
                        label: 'Monedes Acumulades',
                        data: coinsData,
                        borderColor: '#d97706',
                        backgroundColor: 'rgba(217, 119, 6, 0.05)',
                        fill: false,
                        tension: 0.3,
                        pointRadius: 3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            font: { family: 'Inter, sans-serif' }
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    x: {
                        grid: { display: false }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: '#f3f4f6' }
                    }
                }
            }
        });
    }

    // Carregar dades inicials via API
    function fetchEvolutionData(period) {
        fetch(`/api/stats/evolution?period=${period}`)
            .then(response => response.json())
            .then(data => {
                if (data.labels && data.datasets) {
                    initChart(data.labels, data.datasets.xp, data.datasets.coins);
                }
            })
            .catch(err => console.error('Error carregant gràfica d\'evolució:', err));
    }

    // Connectar esdeveniments dels botons de filtre temporal
    const periodButtons = document.querySelectorAll('#evolution-period-buttons button');
    periodButtons.forEach(button => {
        button.addEventListener('click', function () {
            periodButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            const period = this.getAttribute('data-period');
            fetchEvolutionData(period);
        });
    });

    // Càrrega inicial per defecte (Setmana)
    fetchEvolutionData('week');
});
