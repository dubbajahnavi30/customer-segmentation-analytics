/**
 * Nexus RFM Analytics Platform - Main Interactive Application Logic
 * Academic Dual-Method Analysis: Rule-Based RFM + K-Means Clustering
 */

document.addEventListener('DOMContentLoaded', () => {
  const data = window.ANALYTICS_DATA;
  if (!data) {
    console.error('ANALYTICS_DATA is not loaded.');
    return;
  }

  // Segment Color Map
  const SEGMENT_COLORS = {
    'Champions': { border: '#10b981', bg: 'rgba(16, 185, 129, 0.15)', text: '#34d399' },
    'Loyal Customers': { border: '#3b82f6', bg: 'rgba(59, 130, 246, 0.15)', text: '#60a5fa' },
    'Big Spenders': { border: '#a855f7', bg: 'rgba(168, 85, 247, 0.15)', text: '#c084fc' },
    'Potential Loyalists': { border: '#f59e0b', bg: 'rgba(245, 158, 11, 0.15)', text: '#fbbf24' },
    'New Customers': { border: '#06b6d4', bg: 'rgba(6, 182, 212, 0.15)', text: '#22d3ee' },
    'At Risk': { border: '#f43f5e', bg: 'rgba(244, 63, 94, 0.15)', text: '#fb7185' },
    'Lost Customers': { border: '#64748b', bg: 'rgba(100, 116, 139, 0.18)', text: '#94a3b8' }
  };

  const CLUSTER_COLORS = {
    'Cluster 0': { border: '#818cf8', bg: 'rgba(129, 140, 248, 0.2)', text: '#a5b4fc' },
    'Cluster 1': { border: '#64748b', bg: 'rgba(100, 116, 139, 0.2)', text: '#94a3b8' },
    'Cluster 2': { border: '#10b981', bg: 'rgba(16, 185, 129, 0.2)', text: '#34d399' },
    'Cluster 3': { border: '#06b6d4', bg: 'rgba(6, 182, 212, 0.2)', text: '#22d3ee' }
  };

  const ACTION_PLAYBOOKS = {
    'Champions': 'Reward with exclusive VIP loyalty perks, early access to new releases, and personalized account advocacy.',
    'Loyal Customers': 'Maintain steady engagement with tailored cross-selling, upsell incentives, and anniversary bonuses.',
    'Big Spenders': 'Target with high-ticket luxury product bundles, premium tier invitations, and concierge support.',
    'Potential Loyalists': 'Nurture with membership enrollment discounts, curated recommendations, and post-purchase follow-ups.',
    'New Customers': 'Provide seamless onboarding tutorials, welcome promotional vouchers, and customer satisfaction surveys.',
    'At Risk': 'Deploy aggressive win-back email sequences, reactivation discounts, and personalized check-ins before permanent churn.',
    'Lost Customers': 'Low direct-spend priority; limit to automated seasonal broad reactivations or exclude from costly outreach.'
  };

  // State
  let currentSortCol = 'customer_id';
  let currentSortAsc = true;
  let currentPage = 1;
  let pageSize = 15;
  let filteredCustomers = [...data.customers];

  // ========================================================================
  // 1. NAVIGATION TAB SWITCHING
  // ========================================================================
  const tabButtons = document.querySelectorAll('.nav-tab-btn');
  const tabPanels = document.querySelectorAll('.tab-panel');

  function switchTab(targetId) {
    tabButtons.forEach(btn => {
      const isTarget = btn.getAttribute('data-target') === targetId;
      btn.classList.toggle('active', isTarget);
      btn.setAttribute('aria-selected', isTarget ? 'true' : 'false');
    });

    tabPanels.forEach(panel => {
      panel.classList.toggle('active', panel.id === targetId);
    });

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      switchTab(targetId);
    });
  });

  document.getElementById('btn-quick-sim')?.addEventListener('click', () => {
    switchTab('panel-simulator');
  });

  // ========================================================================
  // 2. RENDER KPI METRICS
  // ========================================================================
  function initKPIs() {
    document.getElementById('kpi-total-revenue').textContent = `$${data.total_revenue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    document.getElementById('kpi-total-customers').textContent = data.total_customers.toString();
    document.getElementById('kpi-avg-spend').textContent = `$${data.avg_monetary.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    
    // Champions share
    const champ = data.segment_profiles.find(s => s.segment === 'Champions');
    if (champ) {
      const share = ((champ.total_spending / data.total_revenue) * 100).toFixed(1);
      document.getElementById('kpi-champions-share').textContent = `${share}%`;
    }

    // Churn share (At Risk + Lost)
    const atRisk = data.segment_profiles.find(s => s.segment === 'At Risk')?.count || 0;
    const lost = data.segment_profiles.find(s => s.segment === 'Lost Customers')?.count || 0;
    const churnPct = (((atRisk + lost) / data.total_customers) * 100).toFixed(1);
    document.getElementById('kpi-churn-exposure').textContent = `${churnPct}%`;

    document.getElementById('kpi-kmeans-k').textContent = `K = ${data.evaluation.recommended_k}`;
  }

  // ========================================================================
  // 3. RENDER SEGMENT CARDS (TAB 1)
  // ========================================================================
  function renderSegmentCards() {
    const container = document.getElementById('segment-cards-container');
    if (!container) return;

    container.innerHTML = data.segment_profiles.map(seg => {
      const color = SEGMENT_COLORS[seg.segment] || { border: '#6366f1', bg: 'rgba(99,102,241,0.1)', text: '#fff' };
      const playbook = ACTION_PLAYBOOKS[seg.segment] || 'Standard customer engagement strategy.';
      
      return `
        <div class="segment-item-card" data-segment="${seg.segment}" style="border-top: 3px solid ${color.border};">
          <div>
            <div class="segment-header">
              <span class="segment-pill" style="background: ${color.bg}; color: ${color.text}; border: 1px solid ${color.border};">
                ${seg.segment}
              </span>
              <span class="segment-count-badge">${seg.count} customers (${seg.pct}%)</span>
            </div>

            <div class="segment-stats-row">
              <div>
                <div class="seg-stat-val">${seg.avg_recency} d</div>
                <div class="seg-stat-lbl">Avg Recency</div>
              </div>
              <div>
                <div class="seg-stat-val">${seg.avg_frequency}</div>
                <div class="seg-stat-lbl">Avg Orders</div>
              </div>
              <div>
                <div class="seg-stat-val">$${Math.round(seg.avg_monetary).toLocaleString()}</div>
                <div class="seg-stat-lbl">Avg Spend</div>
              </div>
            </div>

            <div class="segment-desc">
              <strong>Behavior:</strong> ${seg.characteristics}
            </div>
          </div>

          <div class="segment-action-box" style="border-left-color: ${color.border};">
            <span class="action-label" style="color: ${color.text};">Action Playbook</span>
            ${playbook}
          </div>
        </div>
      `;
    }).join('');

    // Clicking a segment card jumps to Directory filtered by that segment
    container.querySelectorAll('.segment-item-card').forEach(card => {
      card.addEventListener('click', () => {
        const segName = card.getAttribute('data-segment');
        const segSelect = document.getElementById('filter-segment');
        if (segSelect) {
          segSelect.value = segName;
          applyCustomerFilters();
          switchTab('panel-directory');
        }
      });
    });
  }

  // ========================================================================
  // 4. CHART.JS VISUALIZATIONS
  // ========================================================================
  let chartDist, chartSpend, chartElbow, chartScatter;

  function initCharts() {
    if (typeof Chart === 'undefined') {
      console.warn('Chart.js not available.');
      return;
    }

    // Chart.js Dark Mode Defaults
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.06)';

    // 1. Segment Distribution Donut
    const ctxDist = document.getElementById('chart-segment-distribution')?.getContext('2d');
    if (ctxDist) {
      const labels = data.segment_profiles.map(s => s.segment);
      const counts = data.segment_profiles.map(s => s.count);
      const bgColors = labels.map(l => (SEGMENT_COLORS[l] ? SEGMENT_COLORS[l].border : '#6366f1'));

      chartDist = new Chart(ctxDist, {
        type: 'doughnut',
        data: {
          labels,
          datasets: [{
            data: counts,
            backgroundColor: bgColors,
            borderColor: '#0f172a',
            borderWidth: 2,
            hoverOffset: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'right',
              labels: { boxWidth: 12, padding: 12, color: '#e2e8f0', font: { size: 11 } }
            },
            tooltip: {
              callbacks: {
                label: (ctx) => ` ${ctx.label}: ${ctx.raw} customers (${((ctx.raw / data.total_customers) * 100).toFixed(1)}%)`
              }
            }
          },
          cutout: '68%'
        }
      });
    }

    // 2. Total & Average Spend Bar Chart
    const ctxSpend = document.getElementById('chart-segment-spend')?.getContext('2d');
    if (ctxSpend) {
      const labels = data.segment_profiles.map(s => s.segment);
      const totalSpends = data.segment_profiles.map(s => s.total_spending);
      const avgSpends = data.segment_profiles.map(s => s.avg_monetary);

      chartSpend = new Chart(ctxSpend, {
        type: 'bar',
        data: {
          labels,
          datasets: [
            {
              label: 'Total Spend ($)',
              data: totalSpends,
              backgroundColor: 'rgba(99, 102, 241, 0.75)',
              borderColor: '#6366f1',
              borderWidth: 1,
              borderRadius: 4,
              yAxisID: 'y'
            },
            {
              label: 'Avg Spend / Customer ($)',
              data: avgSpends,
              backgroundColor: 'rgba(6, 182, 212, 0.75)',
              borderColor: '#06b6d4',
              borderWidth: 1,
              borderRadius: 4,
              yAxisID: 'y1'
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              grid: { display: false },
              ticks: { maxRotation: 25, minRotation: 0, font: { size: 10 } }
            },
            y: {
              type: 'linear',
              position: 'left',
              title: { display: true, text: 'Total Spending ($)', color: '#94a3b8' },
              grid: { color: 'rgba(255, 255, 255, 0.05)' }
            },
            y1: {
              type: 'linear',
              position: 'right',
              title: { display: true, text: 'Avg Spend ($)', color: '#94a3b8' },
              grid: { drawOnChartArea: false }
            }
          },
          plugins: {
            legend: { position: 'top', labels: { boxWidth: 12, color: '#e2e8f0' } }
          }
        }
      });
    }

    // 3. K-Means Elbow & Silhouette Dual-Axis Line
    const ctxElbow = document.getElementById('chart-kmeans-elbow')?.getContext('2d');
    if (ctxElbow) {
      const kVals = data.evaluation.k_values;
      const inertias = data.evaluation.inertias;
      const silScores = data.evaluation.silhouette_scores;

      chartElbow = new Chart(ctxElbow, {
        type: 'line',
        data: {
          labels: kVals.map(k => `K = ${k}`),
          datasets: [
            {
              label: 'Inertia (SSE)',
              data: inertias,
              borderColor: '#f59e0b',
              backgroundColor: 'rgba(245, 158, 11, 0.1)',
              borderWidth: 2,
              tension: 0.3,
              pointBackgroundColor: '#f59e0b',
              pointRadius: 4,
              yAxisID: 'y'
            },
            {
              label: 'Silhouette Score',
              data: silScores,
              borderColor: '#10b981',
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
              borderWidth: 2,
              tension: 0.3,
              pointBackgroundColor: (ctx) => (ctx.dataIndex === 2 ? '#fff' : '#10b981'),
              pointBorderColor: '#10b981',
              pointRadius: (ctx) => (ctx.dataIndex === 2 ? 8 : 4),
              yAxisID: 'y1'
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { grid: { display: false } },
            y: {
              type: 'linear',
              position: 'left',
              title: { display: true, text: 'Inertia (Error Sum)', color: '#94a3b8' },
              grid: { color: 'rgba(255, 255, 255, 0.05)' }
            },
            y1: {
              type: 'linear',
              position: 'right',
              title: { display: true, text: 'Silhouette Score', color: '#94a3b8' },
              min: 0.35,
              max: 0.55,
              grid: { drawOnChartArea: false }
            }
          },
          plugins: {
            legend: { position: 'top', labels: { boxWidth: 12, color: '#e2e8f0' } },
            tooltip: {
              callbacks: {
                afterBody: (ctx) => (ctx[0].dataIndex === 2 ? '★ Optimal Model Selection: K=4' : '')
              }
            }
          }
        }
      });
    }

    // 4. K-Means Scatter Plot (Recency vs Monetary)
    const ctxScatter = document.getElementById('chart-kmeans-scatter')?.getContext('2d');
    if (ctxScatter) {
      // Group points by cluster
      const clusterDatasets = ['Cluster 0', 'Cluster 1', 'Cluster 2', 'Cluster 3'].map(clName => {
        const color = CLUSTER_COLORS[clName] || { border: '#fff' };
        const points = data.customers
          .filter(c => c.kmeans_cluster === clName)
          .map(c => ({
            x: c.recency,
            y: c.monetary,
            code: c.customer_code,
            segment: c.segment_label,
            cluster: clName
          }));

        return {
          label: clName,
          data: points,
          backgroundColor: color.border,
          borderColor: '#0f172a',
          borderWidth: 1,
          pointRadius: 5,
          pointHoverRadius: 8
        };
      });

      chartScatter = new Chart(ctxScatter, {
        type: 'scatter',
        data: { datasets: clusterDatasets },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              title: { display: true, text: 'Recency (Days)', color: '#94a3b8' },
              grid: { color: 'rgba(255, 255, 255, 0.05)' }
            },
            y: {
              title: { display: true, text: 'Monetary Spend ($)', color: '#94a3b8' },
              grid: { color: 'rgba(255, 255, 255, 0.05)' }
            }
          },
          plugins: {
            legend: { position: 'top', labels: { boxWidth: 10, color: '#e2e8f0' } },
            tooltip: {
              callbacks: {
                label: (ctx) => {
                  const p = ctx.raw;
                  return ` ${p.code} (${p.cluster}): $${p.y.toLocaleString()} spend | ${p.x} days recency [${p.segment}]`;
                }
              }
            }
          }
        }
      });
    }
  }

  // ========================================================================
  // 5. RENDER K-MEANS CLUSTER CARDS (TAB 2)
  // ========================================================================
  function renderClusterCards() {
    const container = document.getElementById('cluster-cards-container');
    if (!container) return;

    container.innerHTML = data.kmeans_profiles.map(cl => {
      const color = CLUSTER_COLORS[cl.cluster] || { border: '#6366f1', bg: 'rgba(99,102,241,0.1)', text: '#fff' };
      return `
        <div class="segment-item-card" style="border-top: 3px solid ${color.border};">
          <div>
            <div class="segment-header">
              <span class="segment-pill" style="background: ${color.bg}; color: ${color.text}; border: 1px solid ${color.border};">
                ${cl.cluster}
              </span>
              <span class="segment-count-badge">${cl.count} customers (${cl.pct}%)</span>
            </div>

            <div class="segment-stats-row">
              <div>
                <div class="seg-stat-val">${cl.avg_recency} d</div>
                <div class="seg-stat-lbl">Centroid Recency</div>
              </div>
              <div>
                <div class="seg-stat-val">${cl.avg_frequency}</div>
                <div class="seg-stat-lbl">Centroid Freq</div>
              </div>
              <div>
                <div class="seg-stat-val">$${Math.round(cl.avg_monetary).toLocaleString()}</div>
                <div class="seg-stat-lbl">Centroid Monetary</div>
              </div>
            </div>

            <div class="segment-desc">
              <strong>Characterization:</strong> ${cl.characterization}
            </div>
          </div>

          <div class="segment-action-box" style="border-left-color: ${color.border};">
            <span class="action-label" style="color: ${color.text};">Aggregate Economic Value</span>
            Total Cluster Spend: <strong>$${cl.total_spending.toLocaleString()}</strong> (${((cl.total_spending / data.total_revenue) * 100).toFixed(1)}% of total revenue)
          </div>
        </div>
      `;
    }).join('');
  }

  // ========================================================================
  // 6. RENDER CROSS-TABULATION HEATMAP (TAB 3)
  // ========================================================================
  function renderHeatmap() {
    const container = document.getElementById('heatmap-container');
    if (!container) return;

    const clusters = ['Cluster 0', 'Cluster 1', 'Cluster 2', 'Cluster 3'];
    const rows = data.crosstab.filter(r => r.segment_label !== 'Total');

    let html = `
      <table class="heatmap-table">
        <thead>
          <tr>
            <th>Rule-Based Segment</th>
            <th>Cluster 0 (Dormant High-Value)</th>
            <th>Cluster 1 (Dormant Churned)</th>
            <th>Cluster 2 (Active Core High-Value)</th>
            <th>Cluster 3 (Active New / Low-Spend)</th>
            <th>Total Accounts</th>
          </tr>
        </thead>
        <tbody>
    `;

    rows.forEach(r => {
      html += `<tr>`;
      html += `<td style="font-weight:700; color:#fff;">${r.segment_label}</td>`;

      clusters.forEach(cl => {
        const val = parseInt(r[cl] || 0, 10);
        let cellClass = 'cell-zero';
        if (val > 20) cellClass = 'cell-high';
        else if (val > 5) cellClass = 'cell-med';
        else if (val > 0) cellClass = 'cell-low';

        html += `
          <td class="heatmap-cell ${cellClass}" title="${r.segment_label} &harr; ${cl}: ${val} customers" data-seg="${r.segment_label}" data-cl="${cl}">
            ${val}
          </td>
        `;
      });

      html += `<td class="heatmap-cell" style="background:rgba(255,255,255,0.05); color:#fff; font-weight:800;">${r.Total}</td>`;
      html += `</tr>`;
    });

    html += `</tbody></table>`;
    container.innerHTML = html;

    // Click heatmap cell to filter Customer Directory
    container.querySelectorAll('.heatmap-cell[data-seg]').forEach(cell => {
      cell.addEventListener('click', () => {
        const seg = cell.getAttribute('data-seg');
        const cl = cell.getAttribute('data-cl');
        const count = parseInt(cell.textContent.trim(), 10);
        if (count === 0) return;

        document.getElementById('filter-segment').value = seg;
        document.getElementById('filter-cluster').value = cl;
        applyCustomerFilters();
        switchTab('panel-directory');
      });
    });
  }

  // ========================================================================
  // 7. WHAT-IF RFM SIMULATOR (TAB 4)
  // ========================================================================
  const sliderR = document.getElementById('slider-recency');
  const sliderF = document.getElementById('slider-frequency');
  const sliderM = document.getElementById('slider-monetary');

  const displayR = document.getElementById('sim-val-recency');
  const displayF = document.getElementById('sim-val-frequency');
  const displayM = document.getElementById('sim-val-monetary');

  const simSegText = document.getElementById('sim-predicted-segment');
  const simRScore = document.getElementById('sim-r-score');
  const simFScore = document.getElementById('sim-f-score');
  const simMScore = document.getElementById('sim-m-score');
  const simCompScore = document.getElementById('sim-composite-score');
  const simClusterText = document.getElementById('sim-predicted-cluster');
  const simPlaybookText = document.getElementById('sim-playbook-text');

  // Exact quantiles computed from dataset
  function computeRScore(r) {
    if (r <= 16) return 5;
    if (r <= 36) return 4;
    if (r <= 67) return 3;
    if (r <= 236) return 2;
    return 1;
  }

  function computeFScore(f) {
    if (f <= 2) return 1;
    if (f <= 3) return 2;
    if (f <= 4) return 3;
    if (f <= 6) return 4;
    return 5;
  }

  function computeMScore(m) {
    if (m <= 206) return 1;
    if (m <= 777) return 2;
    if (m <= 1440) return 3;
    if (m <= 2874) return 4;
    return 5;
  }

  function classifySegment(rScore, fScore, mScore) {
    if (rScore >= 4 && fScore >= 4 && mScore >= 4) return 'Champions';
    if (rScore >= 3 && fScore >= 3 && mScore >= 3) return 'Loyal Customers';
    if (mScore >= 4 && fScore < 3) return 'Big Spenders';
    if (rScore >= 4 && fScore <= 2) return 'New Customers';
    if (rScore <= 2 && (fScore >= 3 || mScore >= 3)) return 'At Risk';
    if (rScore <= 2 && fScore <= 2 && mScore <= 2) return 'Lost Customers';
    return 'Potential Loyalists';
  }

  function estimateCluster(r, f, m) {
    // Centroids:
    // C0: R=100.9, F=5.0, M=1687.8
    // C1: R=365.2, F=1.5, M=164.6
    // C2: R=10.0, F=9.1, M=6600.9
    // C3: R=22.5, F=1.5, M=374.4
    const centroids = [
      { id: 'Cluster 0 (Dormant High-Value)', r: 100.9, f: 5.0, m: 1687.8 },
      { id: 'Cluster 1 (Dormant Churned)', r: 365.2, f: 1.5, m: 164.6 },
      { id: 'Cluster 2 (Active Core High-Value)', r: 10.0, f: 9.1, m: 6600.9 },
      { id: 'Cluster 3 (Active New / Low-Spend)', r: 22.5, f: 1.5, m: 374.4 }
    ];

    // Normalized Euclidean distance in log space
    const logR = Math.log(r + 1);
    const logF = Math.log(f + 1);
    const logM = Math.log(m + 1);

    let bestDist = Infinity;
    let bestCluster = centroids[0].id;

    centroids.forEach(c => {
      const cLogR = Math.log(c.r + 1);
      const cLogF = Math.log(c.f + 1);
      const cLogM = Math.log(c.m + 1);

      const dist = Math.sqrt(
        Math.pow(logR - cLogR, 2) +
        Math.pow(logF - cLogF, 2) +
        Math.pow(logM - cLogM, 2)
      );

      if (dist < bestDist) {
        bestDist = dist;
        bestCluster = c.id;
      }
    });

    return bestCluster;
  }

  function updateSimulator() {
    if (!sliderR || !sliderF || !sliderM) return;

    const r = parseInt(sliderR.value, 10);
    const f = parseInt(sliderF.value, 10);
    const m = parseInt(sliderM.value, 10);

    displayR.textContent = `${r} day${r === 1 ? '' : 's'}`;
    displayF.textContent = `${f} order${f === 1 ? '' : 's'}`;
    displayM.textContent = `$${m.toLocaleString()}`;

    const rScore = computeRScore(r);
    const fScore = computeFScore(f);
    const mScore = computeMScore(m);
    const compScore = `${rScore}${fScore}${mScore}`;

    simRScore.textContent = rScore;
    simFScore.textContent = fScore;
    simMScore.textContent = mScore;
    simCompScore.textContent = compScore;

    const segment = classifySegment(rScore, fScore, mScore);
    simSegText.textContent = segment;
    const color = SEGMENT_COLORS[segment] || { text: '#fff' };
    simSegText.style.color = color.text;

    const clusterMatch = estimateCluster(r, f, m);
    simClusterText.textContent = clusterMatch;

    simPlaybookText.textContent = ACTION_PLAYBOOKS[segment] || 'Standard marketing follow-up.';
  }

  sliderR?.addEventListener('input', updateSimulator);
  sliderF?.addEventListener('input', updateSimulator);
  sliderM?.addEventListener('input', updateSimulator);

  document.querySelectorAll('.sim-preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      sliderR.value = btn.getAttribute('data-r');
      sliderF.value = btn.getAttribute('data-f');
      sliderM.value = btn.getAttribute('data-m');
      updateSimulator();
    });
  });

  // ========================================================================
  // 8. LIVE CUSTOMER DIRECTORY (TAB 5)
  // ========================================================================
  const searchInput = document.getElementById('search-customers');
  const filterSegment = document.getElementById('filter-segment');
  const filterCluster = document.getElementById('filter-cluster');
  const tableBody = document.getElementById('customers-table-body');
  const showingText = document.getElementById('showing-records-text');
  const pageIndicator = document.getElementById('page-indicator');
  const prevBtn = document.getElementById('btn-page-prev');
  const nextBtn = document.getElementById('btn-page-next');
  const pageSizeSelect = document.getElementById('page-size-select');

  function applyCustomerFilters() {
    const query = searchInput ? searchInput.value.trim().toLowerCase() : '';
    const segVal = filterSegment ? filterSegment.value : 'ALL';
    const clVal = filterCluster ? filterCluster.value : 'ALL';

    filteredCustomers = data.customers.filter(c => {
      const matchQuery = !query || 
        c.customer_code.toLowerCase().includes(query) || 
        c.customer_id.toString().includes(query) ||
        c.segment_label.toLowerCase().includes(query);
      const matchSeg = segVal === 'ALL' || c.segment_label === segVal;
      const matchCl = clVal === 'ALL' || c.kmeans_cluster === clVal;
      return matchQuery && matchSeg && matchCl;
    });

    // Sort
    filteredCustomers.sort((a, b) => {
      let valA = a[currentSortCol];
      let valB = b[currentSortCol];

      if (typeof valA === 'string') {
        return currentSortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
      }
      return currentSortAsc ? valA - valB : valB - valA;
    });

    currentPage = 1;
    renderCustomerTable();
  }

  function renderCustomerTable() {
    if (!tableBody) return;

    const total = filteredCustomers.length;
    const startIdx = (currentPage - 1) * pageSize;
    const endIdx = Math.min(startIdx + pageSize, total);
    const pageRecords = filteredCustomers.slice(startIdx, endIdx);
    const totalPages = Math.ceil(total / pageSize) || 1;

    if (pageRecords.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="11" style="text-align:center; padding: 24px; color:var(--text-muted);">No matching customer records found.</td></tr>`;
    } else {
      tableBody.innerHTML = pageRecords.map(c => {
        const segColor = SEGMENT_COLORS[c.segment_label] || { border: '#6366f1', bg: 'rgba(99,102,241,0.1)', text: '#fff' };
        const clColor = CLUSTER_COLORS[c.kmeans_cluster] || { border: '#6366f1', text: '#fff' };

        return `
          <tr data-id="${c.customer_id}">
            <td class="mono-cell">${c.customer_id}</td>
            <td class="mono-cell" style="font-weight:700; color:#fff;">${c.customer_code}</td>
            <td class="mono-cell">${c.recency} d</td>
            <td class="mono-cell">${c.frequency}</td>
            <td class="mono-cell" style="color:#34d399; font-weight:600;">$${c.monetary.toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
            <td class="mono-cell">${c.R_Score}</td>
            <td class="mono-cell">${c.F_Score}</td>
            <td class="mono-cell">${c.M_Score}</td>
            <td><span class="score-badge">${c.RFM_Score}</span></td>
            <td>
              <span class="segment-pill" style="background:${segColor.bg}; color:${segColor.text}; border:1px solid ${segColor.border}; font-size:0.72rem;">
                ${c.segment_label}
              </span>
            </td>
            <td>
              <span style="color:${clColor.text}; font-size:0.75rem; font-weight:600;">
                ${c.kmeans_cluster}
              </span>
            </td>
          </tr>
        `;
      }).join('');
    }

    // Update pagination controls
    if (showingText) showingText.textContent = total > 0 ? `Showing ${startIdx + 1}-${endIdx} of ${total}` : 'Showing 0 records';
    if (pageIndicator) pageIndicator.textContent = `Page ${currentPage} of ${totalPages}`;
    if (prevBtn) prevBtn.disabled = currentPage <= 1;
    if (nextBtn) nextBtn.disabled = currentPage >= totalPages;

    // Attach row click listener for Customer Detail Modal
    tableBody.querySelectorAll('tr[data-id]').forEach(row => {
      row.addEventListener('click', () => {
        const id = parseInt(row.getAttribute('data-id'), 10);
        const cust = data.customers.find(c => c.customer_id === id);
        if (cust) openCustomerModal(cust);
      });
    });
  }

  searchInput?.addEventListener('input', applyCustomerFilters);
  filterSegment?.addEventListener('change', applyCustomerFilters);
  filterCluster?.addEventListener('change', applyCustomerFilters);

  pageSizeSelect?.addEventListener('change', (e) => {
    pageSize = parseInt(e.target.value, 10);
    currentPage = 1;
    renderCustomerTable();
  });

  prevBtn?.addEventListener('click', () => {
    if (currentPage > 1) {
      currentPage--;
      renderCustomerTable();
    }
  });

  nextBtn?.addEventListener('click', () => {
    const totalPages = Math.ceil(filteredCustomers.length / pageSize) || 1;
    if (currentPage < totalPages) {
      currentPage++;
      renderCustomerTable();
    }
  });

  // Table Column Header Sorting
  document.querySelectorAll('#customers-table th[data-sort]').forEach(th => {
    th.addEventListener('click', () => {
      const col = th.getAttribute('data-sort');
      if (currentSortCol === col) {
        currentSortAsc = !currentSortAsc;
      } else {
        currentSortCol = col;
        currentSortAsc = true;
      }
      applyCustomerFilters();
    });
  });

  // ========================================================================
  // 9. CUSTOMER DETAIL MODAL
  // ========================================================================
  const modalCust = document.getElementById('customer-modal');
  const btnCloseModal = document.getElementById('btn-close-modal');

  function openCustomerModal(cust) {
    if (!modalCust) return;
    document.getElementById('modal-cust-code').textContent = `${cust.customer_code} (Account #${cust.customer_id})`;
    
    const segColor = SEGMENT_COLORS[cust.segment_label] || { bg: 'rgba(99,102,241,0.1)', text: '#fff', border: '#6366f1' };
    const segBadge = document.getElementById('modal-segment-badge');
    segBadge.textContent = cust.segment_label;
    segBadge.style.background = segColor.bg;
    segBadge.style.color = segColor.text;
    segBadge.style.border = `1px solid ${segColor.border}`;

    const clColor = CLUSTER_COLORS[cust.kmeans_cluster] || { text: '#a5b4fc', bg: 'rgba(99,102,241,0.15)' };
    const clBadge = document.getElementById('modal-cluster-badge');
    clBadge.textContent = cust.kmeans_cluster;
    clBadge.style.color = clColor.text;
    clBadge.style.background = clColor.bg;

    document.getElementById('modal-recency').textContent = `${cust.recency} d`;
    document.getElementById('modal-frequency').textContent = cust.frequency.toString();
    document.getElementById('modal-monetary').textContent = `$${cust.monetary.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;

    document.getElementById('modal-r-score').textContent = cust.R_Score;
    document.getElementById('modal-f-score').textContent = cust.F_Score;
    document.getElementById('modal-m-score').textContent = cust.M_Score;
    document.getElementById('modal-composite-score').textContent = cust.RFM_Score;

    document.getElementById('modal-action-text').textContent = ACTION_PLAYBOOKS[cust.segment_label] || 'Standard customer engagement strategy.';

    modalCust.classList.add('active');
  }

  btnCloseModal?.addEventListener('click', () => {
    modalCust.classList.remove('active');
  });

  modalCust?.addEventListener('click', (e) => {
    if (e.target === modalCust) modalCust.classList.remove('active');
  });

  // ========================================================================
  // 10. ACADEMIC FIGURE GALLERY (300 DPI MATPLOTLIB CHARTS)
  // ========================================================================
  const GALLERY_IMAGES = [
    {
      file: '01_customer_count_by_segment.png',
      title: 'Figure 1: Customer Headcount by Segment',
      desc: 'Bar distribution showing absolute customer headcount across all 7 behavioral segments.'
    },
    {
      file: '02_segment_distribution.png',
      title: 'Figure 2: Segment Percentage Share (Donut)',
      desc: 'Publication pie/donut chart detailing customer percentage share across the entire active portfolio.'
    },
    {
      file: '03_total_spending_by_segment.png',
      title: 'Figure 3: Aggregate Spending Contribution',
      desc: 'Cumulative revenue contribution ($) per segment highlighting Pareto concentration in Champions.'
    },
    {
      file: '04_avg_monetary_by_segment.png',
      title: 'Figure 4: Average Monetary Value per Customer',
      desc: 'Per-customer average net revenue comparison demonstrating high-ticket vs low-spend cohorts.'
    },
    {
      file: '05_avg_frequency_by_segment.png',
      title: 'Figure 5: Average Purchase Frequency',
      desc: 'Average completed orders per customer across segments, differentiating Champions and Loyalists.'
    },
    {
      file: '06_avg_recency_by_segment.png',
      title: 'Figure 6: Average Recency Inactivity Days',
      desc: 'Days elapsed since latest purchase, highlighting dormant churn risk in At-Risk and Lost accounts.'
    },
    {
      file: '07_kmeans_elbow_and_silhouette.png',
      title: 'Figure 7: K-Means Diagnostic (Elbow & Silhouette)',
      desc: 'Dual-panel evaluation comparing Within-Cluster Sum of Squares (Inertia) and Silhouette Scores for K=2..8.'
    },
    {
      file: '08_kmeans_clusters_scatter.png',
      title: 'Figure 8: 3D/2D Feature Space Cluster Scatter',
      desc: 'Visual projection of scaled RFM space demonstrating non-overlapping geometric cluster separation.'
    },
    {
      file: '09_rfm_vs_kmeans_heatmap.png',
      title: 'Figure 9: Cross-Tabulation Overlap Heatmap',
      desc: 'Contingency heatmap quantifying customer alignment between Rule-Based labels and K-Means clusters.'
    }
  ];

  const lightboxModal = document.getElementById('lightbox-modal');
  const lightboxImg = document.getElementById('lightbox-img');
  const lightboxTitle = document.getElementById('lightbox-title');
  const lightboxCaption = document.getElementById('lightbox-caption');
  const lightboxDownload = document.getElementById('lightbox-download-link');
  const btnCloseLightbox = document.getElementById('btn-close-lightbox');

  function renderGallery() {
    const container = document.getElementById('gallery-container');
    if (!container) return;

    container.innerHTML = GALLERY_IMAGES.map((item, index) => {
      const src = `output/charts/${item.file}`;
      return `
        <div class="gallery-card">
          <div class="gallery-img-wrap" data-index="${index}">
            <img class="gallery-img" src="${src}" alt="${item.title}" loading="lazy" onerror="this.onerror=null; this.src='https://placehold.co/600x400/1e293b/94a3b8?text=Generating+Figure...';">
            <div class="gallery-overlay">
              <button type="button" class="zoom-btn" title="Zoom in">&#128269;</button>
            </div>
          </div>
          <div class="gallery-content">
            <div class="gallery-title">${item.title}</div>
            <div class="gallery-desc">${item.desc}</div>
            <div class="gallery-meta">
              <span>300 DPI Matplotlib</span>
              <a href="${src}" download="${item.file}" style="font-weight:600;">Download PNG &darr;</a>
            </div>
          </div>
        </div>
      `;
    }).join('');

    container.querySelectorAll('.gallery-img-wrap').forEach(wrap => {
      wrap.addEventListener('click', () => {
        const idx = parseInt(wrap.getAttribute('data-index'), 10);
        const item = GALLERY_IMAGES[idx];
        const src = `output/charts/${item.file}`;

        lightboxImg.src = src;
        lightboxTitle.textContent = item.title;
        lightboxCaption.textContent = item.desc;
        lightboxDownload.href = src;
        lightboxDownload.setAttribute('download', item.file);

        lightboxModal.classList.add('active');
      });
    });
  }

  btnCloseLightbox?.addEventListener('click', () => {
    lightboxModal.classList.remove('active');
  });

  lightboxModal?.addEventListener('click', (e) => {
    if (e.target === lightboxModal) lightboxModal.classList.remove('active');
  });

  // ========================================================================
  // 11. EXPORTS & SQL COPY
  // ========================================================================
  function exportCSV(records, filename = 'customer_rfm_analytics.csv') {
    if (!records || records.length === 0) return;

    const headers = [
      'customer_id', 'customer_code', 'recency', 'frequency', 'monetary',
      'R_Score', 'F_Score', 'M_Score', 'RFM_Score', 'RFM_Mean',
      'segment_label', 'kmeans_cluster_id', 'kmeans_cluster'
    ];

    const csvRows = [headers.join(',')];

    records.forEach(r => {
      const row = headers.map(h => {
        let val = r[h] !== undefined ? r[h] : '';
        if (typeof val === 'string' && val.includes(',')) {
          val = `"${val}"`;
        }
        return val;
      });
      csvRows.push(row.join(','));
    });

    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  document.getElementById('btn-export-csv')?.addEventListener('click', () => {
    exportCSV(data.customers, 'nexus_rfm_all_customers.csv');
  });

  document.getElementById('btn-export-filtered')?.addEventListener('click', () => {
    exportCSV(filteredCustomers, 'nexus_rfm_filtered_customers.csv');
  });

  document.getElementById('btn-copy-sql')?.addEventListener('click', () => {
    const code = document.getElementById('sql-code-view')?.textContent;
    if (code) {
      navigator.clipboard.writeText(code).then(() => {
        const btn = document.getElementById('btn-copy-sql');
        btn.textContent = 'Copied!';
        setTimeout(() => { btn.textContent = 'Copy SQL'; }, 2000);
      });
    }
  });

  // ESC key closes modals
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      modalCust?.classList.remove('active');
      lightboxModal?.classList.remove('active');
    }
  });

  // ========================================================================
  // INITIALIZE EVERYTHING
  // ========================================================================
  initKPIs();
  renderSegmentCards();
  renderClusterCards();
  renderHeatmap();
  initCharts();
  updateSimulator();
  applyCustomerFilters();
  renderGallery();
});
