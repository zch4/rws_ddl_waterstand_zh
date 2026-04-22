function cssKleur(naam) {
  return getComputedStyle(document.documentElement).getPropertyValue(naam).trim();
}

function maakLegenda(elementId, datasets) {
  const element = document.getElementById(elementId);
  if (!element) return;

  element.innerHTML = datasets.map(dataset => `
    <span class="legenda-item">
      <span class="legenda-kleur" style="background:${dataset.kleur}"></span>
      ${dataset.label}
    </span>
  `).join('');
}

function basisOpties(yLabel) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: cssKleur('--kaart'),
        borderColor: cssKleur('--rand'),
        borderWidth: 1,
        titleColor: cssKleur('--tekst'),
        bodyColor: cssKleur('--tekst-zacht'),
      },
    },
    scales: {
      x: {
        grid: { color: cssKleur('--rand') },
        ticks: { color: cssKleur('--tekst-zacht'), maxTicksLimit: 12, maxRotation: 45 },
      },
      y: {
        title: { display: true, text: yLabel, color: cssKleur('--tekst-zacht') },
        grid: { color: cssKleur('--rand') },
        ticks: { color: cssKleur('--tekst-zacht') },
      },
    },
  };
}

async function tekenLijngrafiek(endpoint, canvasId, legendaId, yLabel) {
  const response = await fetch(endpoint);
  const data = await response.json();
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  const datasets = data.datasets.map(dataset => ({
    label: dataset.label,
    data: dataset.waarden,
    borderColor: dataset.kleur,
    backgroundColor: `${dataset.kleur}22`,
    borderWidth: data.labels.length > 100 ? 1.4 : 2,
    pointRadius: 0,
    tension: 0.25,
    spanGaps: true,
  }));

  new Chart(canvas, {
    type: 'line',
    data: { labels: data.labels, datasets },
    options: basisOpties(yLabel),
  });

  if (legendaId) maakLegenda(legendaId, data.datasets);
}

async function tekenStaafgrafiek(endpoint, canvasId, legendaId, yLabel) {
  const response = await fetch(endpoint);
  const data = await response.json();
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  const datasets = data.datasets.map(dataset => ({
    label: dataset.label,
    data: dataset.waarden,
    backgroundColor: `${dataset.kleur}88`,
    borderColor: dataset.kleur,
    borderWidth: 1,
  }));

  new Chart(canvas, {
    type: 'bar',
    data: { labels: data.labels, datasets },
    options: basisOpties(yLabel),
  });

  maakLegenda(legendaId, data.datasets);
}

async function tekenUurprofiel() {
  const response = await fetch('/api/uurprofiel/');
  const data = await response.json();
  const canvas = document.getElementById('grafiek-uurprofiel');
  if (!canvas) return;

  new Chart(canvas, {
    type: 'line',
    data: {
      labels: data.labels,
      datasets: [{
        label: 'Hoek van Holland',
        data: data.waarden,
        borderColor: '#20808D',
        backgroundColor: '#20808D22',
        borderWidth: 2,
        pointRadius: 3,
        tension: 0.25,
      }],
    },
    options: basisOpties('Waterstand (cm t.o.v. NAP)'),
  });
}

async function tekenStationkaart() {
  const response = await fetch('/api/stationkaart/');
  const data = await response.json();
  const container = document.getElementById('stationkaart');
  if (!container || !data.stations.length) return;

  const stations = data.stations;
  const lons = stations.map(station => station.lon);
  const lats = stations.map(station => station.lat);
  const minLon = Math.min(...lons) - 0.08;
  const maxLon = Math.max(...lons) + 0.08;
  const minLat = Math.min(...lats) - 0.04;
  const maxLat = Math.max(...lats) + 0.04;

  const breedte = 900;
  const hoogte = 420;
  const marge = 44;
  const x = lon => marge + ((lon - minLon) / (maxLon - minLon)) * (breedte - marge * 2);
  const y = lat => hoogte - marge - ((lat - minLat) / (maxLat - minLat)) * (hoogte - marge * 2);

  const punten = stations.map(station => {
    const px = x(station.lon);
    const py = y(station.lat);
    return `
      <g>
        <circle cx="${px}" cy="${py}" r="8" fill="${station.kleur}">
          <title>${station.naam}: ${station.gemiddelde_cm} cm</title>
        </circle>
        <text x="${px + 12}" y="${py - 8}">
          <tspan>${station.naam}</tspan>
          <tspan x="${px + 12}" dy="15">${station.gemiddelde_cm} cm</tspan>
        </text>
      </g>`;
  }).join('');

  container.innerHTML = `
    <svg viewBox="0 0 ${breedte} ${hoogte}" role="img" aria-label="Meetstations Zuid-Holland">
      <rect x="1" y="1" width="${breedte - 2}" height="${hoogte - 2}" rx="8" class="kaart-bg" />
      <path d="M ${marge} ${hoogte - marge} C ${breedte * 0.34} ${hoogte * 0.56}, ${breedte * 0.48} ${hoogte * 0.54}, ${breedte - marge} ${marge}" class="waterlijn" />
      ${punten}
    </svg>`;
}

document.addEventListener('DOMContentLoaded', () => {
  tekenLijngrafiek('/api/daggemiddelden/', 'grafiek-daggemiddelden', 'daggemiddelden-legenda', 'Waterstand (cm t.o.v. NAP)');
  tekenLijngrafiek('/api/astronomisch/', 'grafiek-astronomisch', 'astronomisch-legenda', 'Waterhoogte (cm t.o.v. NAP)');
  tekenLijngrafiek('/api/seizoen/', 'grafiek-seizoen', 'seizoen-legenda', 'Waterstand (cm t.o.v. NAP)');
  tekenStaafgrafiek('/api/extremen/', 'grafiek-extremen', 'extremen-legenda', 'Aantal metingen boven P95');
  tekenUurprofiel();
  tekenStationkaart();
});
