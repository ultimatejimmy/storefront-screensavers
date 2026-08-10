document.addEventListener('DOMContentLoaded', () => {
  let catalogData = [];

  // Nav tab switching
  const navLinks = document.querySelectorAll('.nav-link');
  const sections = document.querySelectorAll('.section');

  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = link.getAttribute('data-target');

      navLinks.forEach(l => l.classList.remove('active'));
      sections.forEach(s => s.classList.remove('active'));

      link.classList.add('active');
      document.getElementById(targetId).classList.add('active');
    });
  });

  // Fetch catalog
  fetch('screensavers.json')
    .then(res => res.json())
    .then(data => {
      catalogData = data;
      renderGallery(catalogData);
    })
    .catch(err => console.error("Failed loading catalog", err));

  async function forceDownload(url, filename) {
    try {
      const res = await fetch(url);
      const blob = await res.blob();
      const blobUrl = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(blobUrl);
    } catch (err) {
      window.open(url, '_blank');
    }
  }

  function renderGallery(items) {
    const grid = document.getElementById('wallpaper-grid');
    grid.innerHTML = '';

    if (items.length === 0) {
      grid.innerHTML = '<p style="color: var(--text-muted); grid-column: 1/-1; text-align: center;">No screensavers found.</p>';
      return;
    }

    items.forEach(item => {
      const card = document.createElement('div');
      card.className = 'card';
      card.innerHTML = `
        <div class="card-image-wrap">
          <img class="card-img" src="${item.thumbnailUrl}" alt="${item.title}" loading="lazy">
          <div class="card-overlay">
            <span style="font-size: 0.8rem; background: rgba(0,0,0,0.6); padding: 0.25rem 0.5rem; border-radius: 4px;">by ${item.author}</span>
          </div>
        </div>
        <div class="card-body">
          <h3 class="card-title">${item.title}</h3>
          <div class="card-meta">
            <span>🏷️ ${item.category}</span>
            <span>❤️ ${item.likes}</span>
          </div>
          <div class="card-footer">
            <button class="btn-primary download-btn">Download</button>
          </div>
        </div>
      `;

      card.querySelector('.download-btn').addEventListener('click', (e) => {
        e.preventDefault();
        forceDownload(item.fullUrl, `${item.id}.jpg`);
      });

      grid.appendChild(card);
    });
  }

  // Filter Buttons
  const tagBtns = document.querySelectorAll('.tag-btn');
  tagBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tagBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const cat = btn.getAttribute('data-category');
      if (cat === 'all') {
        renderGallery(catalogData);
      } else {
        const filtered = catalogData.filter(i => i.category.toLowerCase() === cat.toLowerCase());
        renderGallery(filtered);
      }
    });
  });

  // Search filter
  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase();
      const filtered = catalogData.filter(i => 
        i.title.toLowerCase().includes(q) || 
        i.author.toLowerCase().includes(q) ||
        i.category.toLowerCase().includes(q)
      );
      renderGallery(filtered);
    });
  }

  // File upload preview
  const fileInput = document.getElementById('sub-file');
  const previewContainer = document.getElementById('sub-preview-container');
  const previewImg = document.getElementById('sub-preview-img');

  if (fileInput) {
    fileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (evt) => {
          previewImg.src = evt.target.result;
          previewContainer.style.display = 'block';
        };
        reader.readAsDataURL(file);
      } else {
        previewContainer.style.display = 'none';
      }
    });
  }

  // Submission Form -> GitHub Issue generator
  const submitForm = document.getElementById('submit-form');
  if (submitForm) {
    submitForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const title = document.getElementById('sub-title').value;
      const author = document.getElementById('sub-author').value;
      const checkedCats = Array.from(document.querySelectorAll('input[name="sub-cat"]:checked')).map(el => el.value);
      const category = checkedCats.length > 0 ? checkedCats.join(', ') : 'General';
      const file = fileInput ? fileInput.files[0] : null;
      const fileName = file ? file.name : 'wallpaper.png';

      const issueTitle = encodeURIComponent(`Screensaver Submission: ${title}`);
      const issueBody = encodeURIComponent(
`### Screensaver Submission

**Title:** ${title}
**Author:** ${author}
**Category:** ${category}
**File Name:** ${fileName}

---
📎 **Action Required:** Please drag and drop your image file (\`${fileName}\`) into this box to attach it before clicking Submit!

---
*Submitted via Storefront Screensaver Catalog Site*`
      );

      const githubIssueUrl = `https://github.com/ultimatejimmy/storefront-screensavers/issues/new?title=${issueTitle}&body=${issueBody}`;
      window.open(githubIssueUrl, '_blank');
    });
  }
});
