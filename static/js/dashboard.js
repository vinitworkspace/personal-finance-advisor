/**
 * Dashboard & Analytics Visualization Controller
 * Powered by Chart.js with responsive dark-mode styling and custom tooltips.
 */

document.addEventListener('DOMContentLoaded', () => {
    initDashboardCharts();
});

async function initDashboardCharts() {
    const trendCanvas = document.getElementById('cashflowTrendChart');
    const donutCanvas = document.getElementById('categoryDonutChart');

    if (!trendCanvas && !donutCanvas) return;

    try {
        const response = await fetch('/api/analytics/charts');
        if (!response.ok) throw new Error('Failed to fetch chart payload');
        const data = await response.json();

        // 1. Render Cashflow Trend Chart (Bar & Line Combo)
        if (trendCanvas && data.trend_chart) {
            renderCashflowTrendChart(trendCanvas, data.trend_chart);
        }

        // 2. Render Expense Category Doughnut Chart
        if (donutCanvas && data.category_chart) {
            renderCategoryDonutChart(donutCanvas, data.category_chart);
        }
    } catch (err) {
        console.warn('Chart initialization error:', err);
    }
}

function renderCashflowTrendChart(canvas, trendData) {
    const ctx = canvas.getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: trendData.labels,
            datasets: [
                {
                    label: 'Income',
                    data: trendData.income,
                    backgroundColor: 'rgba(16, 185, 129, 0.75)',
                    borderColor: '#10b981',
                    borderWidth: 1.5,
                    borderRadius: 6,
                    maxBarThickness: 32
                },
                {
                    label: 'Expenses',
                    data: trendData.expenses,
                    backgroundColor: 'rgba(244, 63, 94, 0.75)',
                    borderColor: '#f43f5e',
                    borderWidth: 1.5,
                    borderRadius: 6,
                    maxBarThickness: 32
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#94a3b8',
                        font: { family: 'Inter', size: 12, weight: 500 },
                        usePointStyle: true,
                        boxWidth: 8
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#ffffff',
                    bodyColor: '#cbd5e1',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            return ` ${context.dataset.label}: ₹${context.parsed.y.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.04)' },
                    ticks: { color: '#64748b', font: { family: 'Inter', size: 11 } }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: {
                        color: '#64748b',
                        font: { family: 'Inter', size: 11 },
                        callback: function(value) {
                            return '₹' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

function renderCategoryDonutChart(canvas, categoryData) {
    const ctx = canvas.getContext('2d');

    if (!categoryData.data || categoryData.data.length === 0) {
        // If no expenses, display friendly empty placeholder
        ctx.font = '14px Inter';
        ctx.fillStyle = '#64748b';
        ctx.textAlign = 'center';
        ctx.fillText('No expense data logged yet', canvas.width / 2, canvas.height / 2);
        return;
    }

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: categoryData.labels,
            datasets: [{
                data: categoryData.data,
                backgroundColor: categoryData.colors,
                borderColor: '#0f172a',
                borderWidth: 2,
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#94a3b8',
                        font: { family: 'Inter', size: 11, weight: 500 },
                        usePointStyle: true,
                        boxWidth: 8,
                        padding: 12
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.95)',
                    titleColor: '#ffffff',
                    bodyColor: '#cbd5e1',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            const val = context.parsed;
                            const total = categoryData.total_expenses || 1;
                            const pct = ((val / total) * 100).toFixed(1);
                            return ` ${context.label}: ₹${val.toLocaleString()} (${pct}%)`;
                        }
                    }
                }
            }
        }
    });
}
