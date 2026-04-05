/**
 * Navigation, Modal and Dynamic Content Logic for Political Science
 */

const chapters = [
  // Book 1: समकालीन विश्व राजनीति
  { id: 1, title: "दो ध्रुवीयता का अंत" },
  { id: 2, title: "सत्ता के समकालीन केंद्र" },
  { id: 3, title: "समकालीन दक्षिण एशिया" },
  { id: 4, title: "अंतर्राष्ट्रीय संगठन" },
  { id: 5, title: "समकालीन विश्व में सुरक्षा" },
  { id: 6, title: "पर्यावरण और प्राकृतिक संसाधन" },
  { id: 7, title: "वैश्वीकरण" },
  // Book 2: स्वतंत्र भारत में राजनीति
  { id: 8, title: "राष्ट्र-निर्माण की चुनौतियाँ" },
  { id: 9, title: "एक दल के प्रभुत्व का दौर" },
  { id: 10, title: "नियोजित विकास की राजनीति" },
  { id: 11, title: "भारत के विदेश संबंध" },
  { id: 12, title: "कांग्रेस प्रणाली: चुनौतियाँ और पुनर्स्थापना" },
  { id: 13, title: "लोकतांत्रिक व्यवस्था का संकट" },
  { id: 14, title: "क्षेत्रीय आकांक्षाएँ" },
  { id: 15, title: "भारतीय राजनीति: नए बदलाव" }
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
  if(!grid) return; // If on notes_view.html, grid might not exist, that's fine.
  
  grid.innerHTML = '';

  data.forEach(chapter => {
    const card = document.createElement('div');
    card.className = 'chapter-card';
    card.innerHTML = `
      <div class="chapter-num">${String(chapter.id).padStart(2, '0')}</div>
      <h3 class="chapter-title">${chapter.title}</h3>
      <div class="chapter-actions" style="display:flex; gap:10px; flex-direction: column; margin-top:20px; position:relative; z-index:10;">
        <button class="btn-primary" onclick="window.open('notes_html_view.html?id=${chapter.id}', '_blank')">🌍 संपूर्ण नोट्स देखें (Premium HTML)</button>
        <button class="btn-secondary" onclick="window.open('qa_view.html?id=${chapter.id}', '_blank')" style="background: #8b5cf6; border-color: #7c3aed;">❓ प्रश्न-उत्तर (Master Q&A)</button>

        <!-- <button class="btn-secondary" onclick="window.open('notes_view.html?id=${chapter.id}', '_blank')">📝 Google Docs (Editable)</button> -->
      </div>
    `;
    grid.appendChild(card);
  });
}


// Google Docs Mapping Output
// Placeholder for Political Science IDs. You can map real IDs later.
const googleDocsDb = {
  1: "1hYhC1msvAKvKHVSnvwGY9OgVvFOBTAsLQUqL5c31RNE",
  2: "19xSt-WJ93KIim1DCuWYiUny-6wv5AXXr0FSdV5HslQU",
  3: "1H3hdN0UertSnUctAEVUw9WHHYuKHGcWX-avxSlo6hyk",
  4: "18HNdLmo2qy534M6riMmFIbLH0cL95W0aCkDX94twzLE",
  5: "1iAxEwHhC9SvDT-KRUvp9UFNI376c_1_XFgr7jP_QrfI",
  6: "162kl67LIAi6W8H2gdVhT0oKp4a6I5ulvL4YioHWFb_A",
  7: "1EekWASRVb1Tr0ZRMUdQPgM3qMu4IU3heh4TDPE20MYw",
  8: "1pLZ6-8bDeRHvFctm4HAsDO17puDweWqTWbF38uAyA9w",
  9: "1QqiRghZsix4e8jGgKaU5_m4m3AI0GulR_rDJeeR4NPs",
  10: "1xupgSfF_kZY7Qgx12NhVyNgpsNpYdrE3VeQcJ_A63BU",
  11: "1HfJtvlT6V0MreB9UJ5XoYlrfhsWnCgAducSW0YnXwPA",
  12: "1x3f7wele1kkvvSGbEhwug213Syg7ifIVytBLfTrUe5w",
  13: "1NS5F78ot0NueuAqhgMFu0ECa6Gb1YLtBDhKUQfHYS_c",
  14: "1sWyuhddMf_eeqvFh_6lJnXMJahA5jIRj62V96SaghQU",
  15: "1VMG8Af6dn4RtZ7hOcF8NaaN3cmhi1IKm__QNQJQn4gE"
};
