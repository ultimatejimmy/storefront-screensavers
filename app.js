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
            <a href="${item.fullUrl}" target="_blank" download class="btn-primary">Download</a>
          </div>
        </div>
      `;
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

  // Form Category Pills Handler
  const catPills = document.querySelectorAll('#form-category-pills .cat-pill');
  const subCategoryInput = document.getElementById('sub-category');
  if (catPills && subCategoryInput) {
    catPills.forEach(pill => {
      pill.addEventListener('click', (e) => {
        e.preventDefault();
        catPills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        subCategoryInput.value = pill.getAttribute('data-value');
      });
    });
  }

  // Submission Form & File Upload Dropzone
  const btnModeFile = document.getElementById('btn-mode-file');
  const btnModeUrl = document.getElementById('btn-mode-url');
  const dropzoneBox = document.getElementById('dropzone-box');
  const urlBox = document.getElementById('url-box');
  const subFile = document.getElementById('sub-file');
  const subUrl = document.getElementById('sub-url');
  const dropzonePrompt = document.getElementById('dropzone-prompt');
  const dropzonePreview = document.getElementById('dropzone-preview');
  const previewImg = document.getElementById('preview-img');
  const previewFilename = document.getElementById('preview-filename');
  const previewSpecs = document.getElementById('preview-specs');
  const btnRemoveFile = document.getElementById('btn-remove-file');
  const submitForm = document.getElementById('submit-form');
  const btnSubmitIssue = document.getElementById('btn-submit-issue');

  let selectedFile = null;
  let selectedFileMeta = null;
  let currentMode = 'file'; // 'file' or 'url'

  if (btnModeFile && btnModeUrl) {
    btnModeFile.addEventListener('click', () => {
      currentMode = 'file';
      btnModeFile.classList.add('active');
      btnModeUrl.classList.remove('active');
      dropzoneBox.style.display = 'block';
      urlBox.style.display = 'none';
      if (subUrl) subUrl.required = false;
    });

    btnModeUrl.addEventListener('click', () => {
      currentMode = 'url';
      btnModeUrl.classList.add('active');
      btnModeFile.classList.remove('active');
      dropzoneBox.style.display = 'none';
      urlBox.style.display = 'block';
      if (subUrl) subUrl.required = true;
    });
  }

  // Handle dropzone click & file selection
  if (dropzoneBox && subFile) {
    dropzoneBox.addEventListener('click', (e) => {
      if (e.target !== btnRemoveFile && !btnRemoveFile.contains(e.target)) {
        subFile.click();
      }
    });

    ['dragenter', 'dragover'].forEach(evt => {
      dropzoneBox.addEventListener(evt, (e) => {
        e.preventDefault();
        dropzoneBox.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(evt => {
      dropzoneBox.addEventListener(evt, (e) => {
        e.preventDefault();
        dropzoneBox.classList.remove('dragover');
      });
    });

    dropzoneBox.addEventListener('drop', (e) => {
      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        handleFileSelect(files[0]);
      }
    });

    subFile.addEventListener('change', () => {
      if (subFile.files && subFile.files.length > 0) {
        handleFileSelect(subFile.files[0]);
      }
    });

    if (btnRemoveFile) {
      btnRemoveFile.addEventListener('click', (e) => {
        e.stopPropagation();
        selectedFile = null;
        selectedFileMeta = null;
        subFile.value = '';
        dropzonePrompt.style.display = 'block';
        dropzonePreview.style.display = 'none';
      });
    }
  }

  function handleFileSelect(file) {
    if (!file || !file.type.startsWith('image/')) {
      alert('Please select a valid image file (PNG, JPG, or WebP).');
      return;
    }

    selectedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      const img = new Image();
      img.onload = () => {
        const kb = (file.size / 1024).toFixed(0);
        selectedFileMeta = `${img.width} × ${img.height} px · ${kb} KB`;
        previewFilename.textContent = file.name;
        previewSpecs.textContent = selectedFileMeta;
        dropzonePrompt.style.display = 'none';
        dropzonePreview.style.display = 'flex';
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }

  // Upload file anonymously to free image host API
  async function uploadImageFile(file) {
    try {
      const formData = new FormData();
      formData.append('image', file);
      const res = await fetch('https://freeimage.host/api/1/upload?key=6d207e02198a847aa98d0a2a901485a5&format=json', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data && data.image && data.image.url) {
        return data.image.url;
      }
    } catch (err) {
      console.warn('Anonymous API upload failed, falling back to clipboard copy:', err);
    }
    return null;
  }

  // Submission Form Submit Handler
  if (submitForm) {
    submitForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const title = document.getElementById('sub-title').value;
      const author = document.getElementById('sub-author').value;
      const category = document.getElementById('sub-category').value;

      let imageUrl = '';
      let fileNotice = '';

      if (currentMode === 'file') {
        if (!selectedFile) {
          alert('Please select an image file to upload.');
          return;
        }

        if (btnSubmitIssue) {
          btnSubmitIssue.textContent = 'Uploading image... ⏳';
          btnSubmitIssue.disabled = true;
        }

        // Try anonymous image host upload
        const uploadedUrl = await uploadImageFile(selectedFile);

        // Copy file to clipboard so user can press Ctrl+V directly in GitHub Issue
        try {
          if (navigator.clipboard && window.ClipboardItem) {
            await navigator.clipboard.write([
              new ClipboardItem({ [selectedFile.type]: selectedFile })
            ]);
            fileNotice = 'Image copied to clipboard! Press Ctrl+V / Cmd+V in the GitHub issue comment box to attach directly.';
          }
        } catch (clipErr) {
          console.log('Clipboard write not allowed:', clipErr);
        }

        if (uploadedUrl) {
          imageUrl = uploadedUrl;
        } else {
          imageUrl = `[Uploaded File: ${selectedFile.name} (${selectedFileMeta})]`;
        }

        if (btnSubmitIssue) {
          btnSubmitIssue.textContent = 'Continue to GitHub Submission →';
          btnSubmitIssue.disabled = false;
        }
      } else {
        imageUrl = document.getElementById('sub-url').value;
      }

      const issueTitle = encodeURIComponent(`Screensaver Submission: ${title}`);
      const bodyLines = [
        `### Screensaver Submission`,
        ``,
        `**Title:** ${title}`,
        `**Author:** ${author}`,
        `**Category:** ${category}`,
        `**Image:** ${imageUrl}`,
      ];

      if (selectedFileMeta) {
        bodyLines.push(`**Specs:** ${selectedFileMeta}`);
      }
      if (fileNotice) {
        bodyLines.push(``, `> 💡 ${fileNotice}`);
      }

      bodyLines.push(``, `---`, `*Submitted via Storefront Screensaver Catalog Site*`);

      const issueBody = encodeURIComponent(bodyLines.join('\n'));
      const repoUrl = 'https://github.com/ultimatejimmy/storefront-screensavers';
      const githubIssueUrl = `${repoUrl}/issues/new?title=${issueTitle}&body=${issueBody}`;

      window.open(githubIssueUrl, '_blank');
    });
  }
});
