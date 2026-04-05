/**
 * Navigation, Modal and Dynamic Content Logic for Political Science (Class 11)
 */

const chapters = [
  // Book 1: भारत का संविधान: सिद्धांत और व्यवहार (Indian Constitution at Work)
  { id: 1, title: "संविधान: क्यों और कैसे?" },
  { id: 2, title: "भारतीय संविधान में अधिकार" },
  { id: 3, title: "चुनाव और प्रतिनिधित्व" },
  { id: 4, title: "कार्यपालिका" },
  { id: 5, title: "विधायिका" },
  { id: 6, title: "न्यायपालिका" },
  { id: 7, title: "संघवाद" },
  { id: 8, title: "स्थानीय शासन" },
  { id: 9, title: "संविधान: एक जीवंत दस्तावेज़" },
  { id: 10, title: "संविधान का राजनीतिक दर्शन" },
  // Book 2: राजनीतिक सिद्धांत (Political Theory)
  { id: 11, title: "राजनीतिक सिद्धांत: एक परिचय" },
  { id: 12, title: "स्वतंत्रता" },
  { id: 13, title: "समानता" },
  { id: 14, title: "सामाजिक न्याय" },
  { id: 15, title: "अधिकार" },
  { id: 16, title: "नागरिकता" },
  { id: 17, title: "राष्ट्रवाद" },
  { id: 18, title: "धर्मनिरपेक्षता" }
];

document.addEventListener('DOMContentLoaded', () => {
  renderChapters(chapters);

  const searchBar = document.getElementById('searchBar');
  if(searchBar) {
    searchBar.addEventListener('input', (e) => {
      const term = e.target.value.toLowerCase();
      const filtered = chapters.filter(c => c.title.toLowerCase().includes(term));
      renderChapters(filtered);
    });
  }
});

function renderChapters(data) {
  const grid = document.getElementById('chapter-grid');
  if(!grid) return;

  grid.innerHTML = '';

  data.forEach(chapter => {
    const card = document.createElement('div');
    card.className = 'chapter-card';
    card.innerHTML = `
      <div class="chapter-num">${String(chapter.id).padStart(2, '0')}</div>
      <h3 class="chapter-title">${chapter.title}</h3>
      <div class="chapter-actions" style="display:flex; gap:10px; flex-direction: column; margin-top:20px; position:relative; z-index:10;">
        <button class="btn-primary" onclick="window.open('notes_html_view.html?id=${chapter.id}', '_blank')">🌍 संपूर्ण नोट्स देखें (Premium HTML)</button>
      </div>
    `;
    grid.appendChild(card);
  });
}
