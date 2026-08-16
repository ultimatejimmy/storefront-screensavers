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

  const RATINGS_API_URL = 'https://storefront-vote.ultimatejimmy.workers.dev';
  let liveRatings = {};

  // Fetch catalog & sync live ratings from Cloudflare worker
  fetch(`screensavers.json?t=${Date.now()}`, { cache: 'no-cache' })
    .then(res => res.json())
    .then(data => {
      catalogData = data.map((item, idx) => ({ ...item, _originalIndex: idx }));
      applyFilters();
      fetchLiveRatings();
    })
    .catch(err => console.error("Failed loading catalog", err));

  async function fetchLiveRatings() {
    try {
      const res = await fetch(`${RATINGS_API_URL}/ratings`, { cache: 'no-cache' });
      if (res.ok) {
        liveRatings = await res.json();
        if (Array.isArray(catalogData)) {
          catalogData.forEach(item => {
            const r = liveRatings[item.id] || (item.id && liveRatings[item.id.toLowerCase()]);
            if (r) {
              item.likes = Math.max(0, (r.up || 0) - (r.down || 0));
              item.wilson = r.wilson || 0;
            } else {
              item.likes = 0;
              item.wilson = 0;
            }
          });
          applyFilters();
        }
      }
    } catch (e) {
      console.warn('Could not fetch live ratings from worker:', e);
    }
  }

  let currentOverlayMode = localStorage.getItem('overlayMode') || 'checkerboard';
  let userDownloads = JSON.parse(localStorage.getItem('storefront_user_downloads') || '{}');

  function getItemLikes(item) {
    const r = liveRatings[item.id] || (item.id && liveRatings[item.id.toLowerCase()]);
    if (r) {
      return Math.max(0, (r.up || 0) - (r.down || 0));
    }
    return item.likes || 0;
  }

  function getItemDownloads(item) {
    const baseDownloads = item.downloads || 0;
    const addedDownloads = userDownloads[item.id] || 0;
    return baseDownloads + addedDownloads;
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

      const authorDisplay = item.authorUrl
        ? `<a href="${item.authorUrl}" target="_blank" style="color: inherit; text-decoration: underline;">${item.author}</a>`
        : item.author;

      let attributionHtml = '';
      if (item.license || item.sourceUrl) {
        const licText = item.license || 'Open Access';
        const licLink = item.sourceUrl || item.licenseUrl || '#';
        attributionHtml = `
          <div class="card-attribution">
            <a href="${licLink}" target="_blank" class="license-tag">${licText}</a>
            ${item.attribution ? `<span style="font-size: 0.7rem; color: var(--text-muted);">${item.attribution}</span>` : ''}
          </div>
        `;
      }

      // Tags HTML
      let tagsHtml = '';
      if (Array.isArray(item.tags) && item.tags.length > 0) {
        const topTags = item.tags.slice(0, 3);
        const moreCount = item.tags.length - 3;
        tagsHtml = `
          <div class="card-tags">
            ${topTags.map(tag => `<button type="button" class="card-tag-chip" data-tag="${tag}" title="Search #${tag}">#${tag}</button>`).join('')}
            ${moreCount > 0 ? `<span class="card-tags-more" title="${item.tags.slice(3).join(', ')}">+${moreCount}</span>` : ''}
          </div>
        `;
      }

      // Check if item is an explicit Transparent (e.g. ReaderBackdrop or Transparent category)
      const isTransparent = (
        (typeof item.category === 'string' && item.category.toLowerCase().includes('transparent')) ||
        (Array.isArray(item.category) && item.category.some(c => String(c).toLowerCase().includes('transparent'))) ||
        (item.id && typeof item.id === 'string' && item.id.startsWith('rb-'))
      );

      const wrapClass = 'card-image-wrap' + (isTransparent ? ' transparent-bg' : '') + (isTransparent && currentOverlayMode === 'booktext' ? ' book-text-mode' : '');

      const likesCount = getItemLikes(item);
      const downloadsCount = getItemDownloads(item);

      card.innerHTML = `
        <div class="${wrapClass}">
          <img class="card-img" src="${item.thumbnailUrl}" alt="${item.title}" loading="lazy">
          <div class="card-overlay">
            <span style="font-size: 0.8rem; background: rgba(0,0,0,0.6); padding: 0.25rem 0.5rem; border-radius: 4px;">by ${authorDisplay}</span>
          </div>
        </div>
        <div class="card-body">
          <h3 class="card-title">${item.title}</h3>
          <div class="card-meta">
            <span class="card-category-badge">🏷️ ${Array.isArray(item.category) ? item.category.join(', ') : item.category}</span>
            <div class="card-stats">
              <span class="stat-item rating-stat" title="${likesCount} thumbs up in KOReader">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path></svg>
                <span class="like-count">${likesCount}</span>
              </span>
              <span class="stat-item download-stat" title="${downloadsCount} downloads">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                <span class="download-count">${downloadsCount}</span>
              </span>
            </div>
          </div>
          ${tagsHtml}
          ${attributionHtml}
          <div class="card-footer">
            <a href="${item.fullUrl}" target="_blank" download class="btn-primary card-download-btn" data-id="${item.id}">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
              <span>Download</span>
            </a>
            <button type="button" class="btn-suggest-change" title="Suggest Change / Report Issue" data-id="${item.id}">✏️</button>
          </div>
        </div>
      `;

      // Tag chip click to filter
      const chipBtns = card.querySelectorAll('.card-tag-chip');
      chipBtns.forEach(chip => {
        chip.addEventListener('click', (e) => {
          e.stopPropagation();
          const tag = chip.getAttribute('data-tag');
          if (searchInput) {
            searchInput.value = tag;
            applyFilters();
            searchInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        });
      });

      // Download button click tracking
      const downloadBtn = card.querySelector('.card-download-btn');
      if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
          userDownloads[item.id] = (userDownloads[item.id] || 0) + 1;
          localStorage.setItem('storefront_user_downloads', JSON.stringify(userDownloads));
          const dlSpan = card.querySelector('.download-count');
          if (dlSpan) {
            dlSpan.textContent = getItemDownloads(item);
          }
        });
      }

      const btnSuggest = card.querySelector('.btn-suggest-change');
      if (btnSuggest) {
        btnSuggest.addEventListener('click', () => openSuggestDrawer(item));
      }

      grid.appendChild(card);
    });
  }

  // Transparent Preview Mode Toggle Listener
  const overlayToggleBtns = document.querySelectorAll('#overlay-mode-toggle .mode-btn');
  if (overlayToggleBtns.length > 0) {
    // Set initial active state based on localStorage
    overlayToggleBtns.forEach(btn => {
      if (btn.getAttribute('data-mode') === currentOverlayMode) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    overlayToggleBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const mode = btn.getAttribute('data-mode');
        if (mode === currentOverlayMode) return;

        currentOverlayMode = mode;
        localStorage.setItem('overlayMode', mode);

        overlayToggleBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Apply class to all current transparent wraps
        const transparentWraps = document.querySelectorAll('.card-image-wrap.transparent-bg');
        transparentWraps.forEach(wrap => {
          if (currentOverlayMode === 'booktext') {
            wrap.classList.add('book-text-mode');
          } else {
            wrap.classList.remove('book-text-mode');
          }
        });
      });
    });
  }

  // Helper to check if item matches selected categories
  function itemMatchesCategories(item, activeCats) {
    if (!activeCats || activeCats.length === 0 || activeCats.includes('all')) return true;
    let itemCats = [];
    if (Array.isArray(item.category)) {
      itemCats = item.category.map(c => String(c).toLowerCase());
    } else if (typeof item.category === 'string') {
      itemCats = item.category.split(',').map(c => c.trim().toLowerCase());
    }

    return activeCats.some(ac => {
      const acNorm = ac.toLowerCase();
      if (acNorm.includes('transparent')) {
        return itemCats.some(ic => ic.includes('transparent'));
      }
      return itemCats.includes(acNorm);
    });
  }

  function getActiveFilterCategories() {
    const activeBtns = document.querySelectorAll('.category-tags .tag-btn.active');
    const cats = Array.from(activeBtns).map(b => b.getAttribute('data-category').toLowerCase());
    return cats;
  }

  function applyFilters() {
    const activeCats = getActiveFilterCategories();
    const q = (searchInput ? searchInput.value : '').trim().toLowerCase();
    const sortSelect = document.getElementById('sort-select');
    const sortBy = sortSelect ? sortSelect.value : 'likes';

    let filtered = catalogData.filter(item => {
      const matchCat = itemMatchesCategories(item, activeCats);
      const matchSearch = !q || (
        (item.title && item.title.toLowerCase().includes(q)) ||
        (item.author && item.author.toLowerCase().includes(q)) ||
        (item.category && String(item.category).toLowerCase().includes(q)) ||
        (Array.isArray(item.tags) && item.tags.some(t => String(t).toLowerCase().includes(q)))
      );
      return matchCat && matchSearch;
    });

    if (sortBy === 'downloads') {
      filtered.sort((a, b) => (getItemDownloads(b) - getItemDownloads(a)) || ((b._originalIndex || 0) - (a._originalIndex || 0)));
    } else if (sortBy === 'newest') {
      filtered.sort((a, b) => {
        if (a.dateAdded && b.dateAdded) return new Date(b.dateAdded) - new Date(a.dateAdded);
        return (b._originalIndex || 0) - (a._originalIndex || 0);
      });
    } else if (sortBy === 'oldest') {
      filtered.sort((a, b) => {
        if (a.dateAdded && b.dateAdded) return new Date(a.dateAdded) - new Date(b.dateAdded);
        return (a._originalIndex || 0) - (b._originalIndex || 0);
      });
    } else if (sortBy === 'title-asc') {
      filtered.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
    } else if (sortBy === 'title-desc') {
      filtered.sort((a, b) => (b.title || '').localeCompare(a.title || ''));
    } else if (sortBy === 'author-asc') {
      filtered.sort((a, b) => (a.author || '').localeCompare(b.author || ''));
    } else {
      // Default: Most Popular (Thumbs Up) with newest additions as tiebreaker
      filtered.sort((a, b) => (getItemLikes(b) - getItemLikes(a)) || ((b._originalIndex || 0) - (a._originalIndex || 0)));
    }

    renderGallery(filtered);
  }

  // Gallery Multi-Select Filter Buttons
  const tagBtns = document.querySelectorAll('.category-tags .tag-btn');
  const allTagBtn = document.querySelector('.category-tags .tag-btn[data-category="all"]');

  tagBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const cat = btn.getAttribute('data-category');

      if (cat === 'all') {
        tagBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      } else {
        if (allTagBtn) allTagBtn.classList.remove('active');
        btn.classList.toggle('active');

        // If no categories active, revert back to All
        const anyActive = document.querySelectorAll('.category-tags .tag-btn.active[data-category]:not([data-category="all"])');
        if (anyActive.length === 0 && allTagBtn) {
          allTagBtn.classList.add('active');
        }
      }

      applyFilters();
    });
  });

  // Search filter
  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      applyFilters();
    });
  }

  // Sort dropdown listener
  const sortSelect = document.getElementById('sort-select');
  if (sortSelect) {
    sortSelect.addEventListener('change', () => {
      applyFilters();
    });
  }

  // Form Multi-Select Category Pills Handler
  const catPills = document.querySelectorAll('#form-category-pills .cat-pill');
  const subCategoryInput = document.getElementById('sub-category');
  if (catPills && subCategoryInput) {
    catPills.forEach(pill => {
      pill.addEventListener('click', (e) => {
        e.preventDefault();
        pill.classList.toggle('active');

        const activePills = document.querySelectorAll('#form-category-pills .cat-pill.active');
        if (activePills.length === 0) {
          pill.classList.add('active'); // ensure at least one category stays selected
        }

        const selectedVals = Array.from(document.querySelectorAll('#form-category-pills .cat-pill.active'))
          .map(p => p.getAttribute('data-value'));
        subCategoryInput.value = selectedVals.join(', ');
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
      if (btnRemoveFile && (e.target === btnRemoveFile || btnRemoveFile.contains(e.target))) {
        return;
      }
      if (cropperContainer && (e.target === cropperContainer || cropperContainer.contains(e.target))) {
        return;
      }
      subFile.click();
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
        cropImageObj = null;
        subFile.value = '';
        dropzonePrompt.style.display = 'block';
        dropzonePreview.style.display = 'none';
        if (cropperContainer) cropperContainer.style.display = 'none';
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
        initCropper(img);
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }

  // Upload file anonymously to free image host API (CORS enabled)
  async function uploadImageFile(file) {
    // 1. Try ImgBB API
    try {
      const formData = new FormData();
      formData.append('key', '6d207e02198a847aa98d0a2a901485a5');
      formData.append('image', file);
      const res = await fetch('https://api.imgbb.com/1/upload', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data && data.data && (data.data.url || data.data.display_url)) {
        return data.data.url || data.data.display_url;
      }
    } catch (err1) {
      console.warn('ImgBB upload attempt failed:', err1);
    }

    // 2. Try Litterbox / Catbox API
    try {
      const formData = new FormData();
      formData.append('reqtype', 'fileupload');
      formData.append('time', '72h');
      formData.append('fileToUpload', file);
      const res = await fetch('https://litterbox.catbox.moe/resources/internals/api.php', {
        method: 'POST',
        body: formData
      });
      const text = await res.text();
      if (text && text.trim().startsWith('http')) {
        return text.trim();
      }
    } catch (err2) {
      console.warn('Catbox upload attempt failed:', err2);
    }

    return null;
  }

  // Interactive 3:4 Cropper Module
  const cropperContainer = document.getElementById('cropper-container');
  const cropperCanvas = document.getElementById('cropper-canvas');
  const cropZoomSlider = document.getElementById('crop-zoom-slider');
  const zoomValLabel = document.getElementById('zoom-val');
  const btnAutoFocal = document.getElementById('btn-auto-focal');

  let cropImageObj = null;
  let cropState = {
    zoom: 1,
    offsetX: 0,
    offsetY: 0,
    isDragging: false,
    startX: 0,
    startY: 0
  };

  const FRAME_W = 270;
  const FRAME_H = 360; // 3:4 ratio

  function initCropper(imgObj) {
    cropImageObj = imgObj;
    cropState.zoom = 1;
    if (cropZoomSlider) cropZoomSlider.value = 1;
    if (zoomValLabel) zoomValLabel.textContent = '1.0x';

    if (cropperCanvas) {
      cropperCanvas.width = FRAME_W;
      cropperCanvas.height = FRAME_H;
    }

    autoDetectFocalPoint();
    if (cropperContainer) cropperContainer.style.display = 'block';
  }

  function autoDetectFocalPoint() {
    if (!cropImageObj || !cropperCanvas) return;

    const imgW = cropImageObj.naturalWidth || cropImageObj.width;
    const imgH = cropImageObj.naturalHeight || cropImageObj.height;

    const baseScale = Math.max(FRAME_W / imgW, FRAME_H / imgH);
    const scaledW = imgW * baseScale * cropState.zoom;
    const scaledH = imgH * baseScale * cropState.zoom;

    try {
      const sampleCanvas = document.createElement('canvas');
      const ctx = sampleCanvas.getContext('2d');
      const sW = 64, sH = 64;
      sampleCanvas.width = sW;
      sampleCanvas.height = sH;
      ctx.drawImage(cropImageObj, 0, 0, sW, sH);
      const imgData = ctx.getImageData(0, 0, sW, sH).data;

      let maxVar = -1;
      let bestX = sW / 2, bestY = sH / 2;

      const step = 8;
      for (let y = 0; y < sH; y += step) {
        for (let x = 0; x < sW; x += step) {
          let sum = 0, count = 0;
          for (let cy = y; cy < y + step && cy < sH; cy++) {
            for (let cx = x; cx < x + step && cx < sW; cx++) {
              const idx = (cy * sW + cx) * 4;
              const lum = 0.299 * imgData[idx] + 0.587 * imgData[idx + 1] + 0.114 * imgData[idx + 2];
              sum += lum;
              count++;
            }
          }
          const mean = sum / count;
          let variance = 0;
          for (let cy = y; cy < y + step && cy < sH; cy++) {
            for (let cx = x; cx < x + step && cx < sW; cx++) {
              const idx = (cy * sW + cx) * 4;
              const lum = 0.299 * imgData[idx] + 0.587 * imgData[idx + 1] + 0.114 * imgData[idx + 2];
              variance += Math.pow(lum - mean, 2);
            }
          }
          if (variance > maxVar) {
            maxVar = variance;
            bestX = x + step / 2;
            bestY = y + step / 2;
          }
        }
      }

      const focalPctX = bestX / sW;
      const focalPctY = bestY / sH;

      cropState.offsetX = (FRAME_W / 2) - (scaledW * focalPctX);
      cropState.offsetY = (FRAME_H / 2) - (scaledH * focalPctY);
      clampCropOffsets(scaledW, scaledH);
    } catch (err) {
      cropState.offsetX = (FRAME_W - scaledW) / 2;
      cropState.offsetY = (FRAME_H - scaledH) / 2;
    }

    drawCropper();
  }

  function clampCropOffsets(scaledW, scaledH) {
    const padX = Math.max(0, (FRAME_W - scaledW) / 2);
    const padY = Math.max(0, (FRAME_H - scaledH) / 2);

    const minX = Math.min(0, FRAME_W - scaledW) - padX;
    const maxX = Math.max(0, FRAME_W - scaledW) + padX;
    const minY = Math.min(0, FRAME_H - scaledH) - padY;
    const maxY = Math.max(0, FRAME_H - scaledH) + padY;

    cropState.offsetX = Math.max(minX, Math.min(maxX, cropState.offsetX));
    cropState.offsetY = Math.max(minY, Math.min(maxY, cropState.offsetY));
  }

  function drawCropper() {
    if (!cropImageObj || !cropperCanvas) return;
    const ctx = cropperCanvas.getContext('2d');
    const imgW = cropImageObj.naturalWidth || cropImageObj.width;
    const imgH = cropImageObj.naturalHeight || cropImageObj.height;

    const baseScale = Math.max(FRAME_W / imgW, FRAME_H / imgH);
    const scaledW = imgW * baseScale * cropState.zoom;
    const scaledH = imgH * baseScale * cropState.zoom;

    clampCropOffsets(scaledW, scaledH);

    // Fill background with solid black for letterbox padding
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, FRAME_W, FRAME_H);

    ctx.drawImage(cropImageObj, cropState.offsetX, cropState.offsetY, scaledW, scaledH);

    // Rule of thirds grid overlay
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.25)';
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);

    ctx.beginPath();
    ctx.moveTo(FRAME_W / 3, 0); ctx.lineTo(FRAME_W / 3, FRAME_H);
    ctx.moveTo((FRAME_W / 3) * 2, 0); ctx.lineTo((FRAME_W / 3) * 2, FRAME_H);
    ctx.moveTo(0, FRAME_H / 3); ctx.lineTo(FRAME_W, FRAME_H / 3);
    ctx.moveTo(0, (FRAME_H / 3) * 2); ctx.lineTo(FRAME_W, (FRAME_H / 3) * 2);
    ctx.stroke();
    ctx.setLineDash([]);

    // Draw 3:4 E-Ink Screen Outline Border
    ctx.strokeStyle = 'rgba(139, 92, 246, 0.8)'; // accent purple
    ctx.lineWidth = 2;
    ctx.strokeRect(1, 1, FRAME_W - 2, FRAME_H - 2);

    // Draw Cyan Corner Brackets
    const cLen = 16;
    ctx.strokeStyle = '#06b6d4'; // bright cyan
    ctx.lineWidth = 3;
    ctx.beginPath();
    // Top-Left
    ctx.moveTo(0, cLen); ctx.lineTo(0, 0); ctx.lineTo(cLen, 0);
    // Top-Right
    ctx.moveTo(FRAME_W - cLen, 0); ctx.lineTo(FRAME_W, 0); ctx.lineTo(FRAME_W, cLen);
    // Bottom-Left
    ctx.moveTo(0, FRAME_H - cLen); ctx.lineTo(0, FRAME_H); ctx.lineTo(cLen, FRAME_H);
    // Bottom-Right
    ctx.moveTo(FRAME_W - cLen, FRAME_H); ctx.lineTo(FRAME_W, FRAME_H); ctx.lineTo(FRAME_W, FRAME_H - cLen);
    ctx.stroke();
  }

  if (cropperCanvas) {
    cropperCanvas.addEventListener('mousedown', (e) => {
      cropState.isDragging = true;
      cropState.startX = e.clientX - cropState.offsetX;
      cropState.startY = e.clientY - cropState.offsetY;
    });

    window.addEventListener('mousemove', (e) => {
      if (!cropState.isDragging) return;
      cropState.offsetX = e.clientX - cropState.startX;
      cropState.offsetY = e.clientY - cropState.startY;
      drawCropper();
    });

    window.addEventListener('mouseup', () => {
      cropState.isDragging = false;
    });

    cropperCanvas.addEventListener('touchstart', (e) => {
      if (e.touches.length === 1) {
        cropState.isDragging = true;
        cropState.startX = e.touches[0].clientX - cropState.offsetX;
        cropState.startY = e.touches[0].clientY - cropState.offsetY;
      }
    });

    window.addEventListener('touchmove', (e) => {
      if (!cropState.isDragging || e.touches.length !== 1) return;
      cropState.offsetX = e.touches[0].clientX - cropState.startX;
      cropState.offsetY = e.touches[0].clientY - cropState.startY;
      drawCropper();
    });

    window.addEventListener('touchend', () => {
      cropState.isDragging = false;
    });
  }

  if (cropZoomSlider) {
    cropZoomSlider.addEventListener('input', (e) => {
      cropState.zoom = parseFloat(e.target.value);
      if (zoomValLabel) zoomValLabel.textContent = cropState.zoom.toFixed(1) + 'x';
      drawCropper();
    });
  }

  if (btnAutoFocal) {
    btnAutoFocal.addEventListener('click', (e) => {
      e.preventDefault();
      autoDetectFocalPoint();
    });
  }

  function getCroppedBlob() {
    return new Promise((resolve) => {
      if (!cropImageObj) {
        resolve(selectedFile);
        return;
      }
      const outCanvas = document.createElement('canvas');
      const TARGET_W = 1860;
      const TARGET_H = 2480;
      outCanvas.width = TARGET_W;
      outCanvas.height = TARGET_H;
      const ctx = outCanvas.getContext('2d');

      const imgW = cropImageObj.naturalWidth || cropImageObj.width;
      const imgH = cropImageObj.naturalHeight || cropImageObj.height;

      const baseScale = Math.max(FRAME_W / imgW, FRAME_H / imgH);
      const scaledW = imgW * baseScale * cropState.zoom;
      const scaledH = imgH * baseScale * cropState.zoom;

      const scaleFactor = TARGET_W / FRAME_W;
      const drawX = cropState.offsetX * scaleFactor;
      const drawY = cropState.offsetY * scaleFactor;
      const drawW = scaledW * scaleFactor;
      const drawH = scaledH * scaleFactor;

      ctx.fillStyle = '#000000';
      ctx.fillRect(0, 0, TARGET_W, TARGET_H);
      ctx.drawImage(cropImageObj, drawX, drawY, drawW, drawH);

      outCanvas.toBlob((blob) => {
        resolve(blob || selectedFile);
      }, 'image/jpeg', 0.92);
    });
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
          btnSubmitIssue.textContent = 'Processing & uploading crop... ⏳';
          btnSubmitIssue.disabled = true;
        }

        // Get 3:4 cropped image blob
        const fileToUpload = await getCroppedBlob();

        // Try automatic image host upload
        const uploadedUrl = await uploadImageFile(fileToUpload);

        if (uploadedUrl) {
          imageUrl = uploadedUrl;
          fileNotice = 'Image automatically uploaded to CDN! A Pull Request will be generated for review.';
        } else {
          imageUrl = `[Uploaded File: ${selectedFile.name} (${selectedFileMeta})]`;
          // Copy file to clipboard fallback if upload fails
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
        }

        if (btnSubmitIssue) {
          btnSubmitIssue.textContent = 'Continue to GitHub Submission →';
          btnSubmitIssue.disabled = false;
        }
      } else {
        imageUrl = document.getElementById('sub-url').value;
      }

      const subTags = document.getElementById('sub-tags') ? document.getElementById('sub-tags').value.trim() : '';

      const issueTitle = encodeURIComponent(`Screensaver Submission: ${title}`);
      const bodyLines = [
        `### Screensaver Submission`,
        ``,
        `**Title:** ${title}`,
        `**Author:** ${author}`,
        `**Category:** ${category}`,
      ];

      if (subTags) {
        bodyLines.push(`**Tags:** ${subTags}`);
      }

      bodyLines.push(`**Image:** ${imageUrl}`);

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

  // --- Submission Mode Switcher: Single vs Bulk ---
  const btnSubmitSingle = document.getElementById('btn-submit-single');
  const btnSubmitBulk = document.getElementById('btn-submit-bulk');
  const submitFormEl = document.getElementById('submit-form');
  const bulkSubmitContainer = document.getElementById('bulk-submit-container');

  if (btnSubmitSingle && btnSubmitBulk) {
    btnSubmitSingle.addEventListener('click', () => {
      btnSubmitSingle.classList.add('active');
      btnSubmitBulk.classList.remove('active');
      if (submitFormEl) submitFormEl.style.display = 'block';
      if (bulkSubmitContainer) bulkSubmitContainer.style.display = 'none';
    });

    btnSubmitBulk.addEventListener('click', () => {
      btnSubmitBulk.classList.add('active');
      btnSubmitSingle.classList.remove('active');
      if (submitFormEl) submitFormEl.style.display = 'none';
      if (bulkSubmitContainer) bulkSubmitContainer.style.display = 'block';
    });
  }

  // --- Bulk Queue Logic ---
  const bulkDropzoneBox = document.getElementById('bulk-dropzone-box');
  const subBulkFiles = document.getElementById('sub-bulk-files');
  const bulkQueueList = document.getElementById('bulk-queue-list');
  const btnSubmitBulkAll = document.getElementById('btn-submit-bulk-all');

  let bulkQueue = []; // items: { id, file, title, author, category, previewUrl }

  if (bulkDropzoneBox && subBulkFiles) {
    bulkDropzoneBox.addEventListener('click', () => subBulkFiles.click());

    ['dragenter', 'dragover'].forEach(evt => {
      bulkDropzoneBox.addEventListener(evt, (e) => {
        e.preventDefault();
        bulkDropzoneBox.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(evt => {
      bulkDropzoneBox.addEventListener(evt, (e) => {
        e.preventDefault();
        bulkDropzoneBox.classList.remove('dragover');
      });
    });

    bulkDropzoneBox.addEventListener('drop', (e) => {
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleBulkFiles(e.dataTransfer.files);
      }
    });

    subBulkFiles.addEventListener('change', () => {
      if (subBulkFiles.files && subBulkFiles.files.length > 0) {
        handleBulkFiles(subBulkFiles.files);
      }
    });
  }

  function handleBulkFiles(files) {
    const fileArray = Array.from(files).filter(f => f.type.startsWith('image/')).slice(0, 10);
    fileArray.forEach(file => {
      const qId = 'item-' + Date.now() + '-' + Math.random().toString(36).substr(2, 4);
      const cleanTitle = file.name.replace(/\.[^/.]+$/, "").replace(/[-_]/g, " ");
      const formattedTitle = cleanTitle.charAt(0).toUpperCase() + cleanTitle.slice(1);

      const queueItem = {
        id: qId,
        file: file,
        title: formattedTitle,
        author: 'Community',
        category: 'Minimalist',
        previewUrl: URL.createObjectURL(file)
      };
      bulkQueue.push(queueItem);
    });
    renderBulkQueue();
  }

  function renderBulkQueue() {
    if (!bulkQueueList) return;
    bulkQueueList.innerHTML = '';

    if (bulkQueue.length === 0) {
      if (btnSubmitBulkAll) btnSubmitBulkAll.style.display = 'none';
      return;
    }

    if (btnSubmitBulkAll) {
      btnSubmitBulkAll.style.display = 'block';
      btnSubmitBulkAll.textContent = `Submit All (${bulkQueue.length}) Wallpapers →`;
    }

    bulkQueue.forEach((item, idx) => {
      const card = document.createElement('div');
      card.className = 'bulk-item-card';
      card.innerHTML = `
        <img class="bulk-item-thumb" src="${item.previewUrl}" alt="Queue Thumbnail">
        <div class="bulk-item-fields">
          <input type="text" class="form-control bulk-input-title" data-idx="${idx}" value="${item.title}" placeholder="Title" required>
          <div style="display: flex; gap: 0.5rem;">
            <input type="text" class="form-control bulk-input-author" data-idx="${idx}" value="${item.author}" placeholder="Author / Artist" required style="flex: 1;">
            <select class="form-control bulk-input-category" data-idx="${idx}" style="flex: 1;">
              <option value="Minimalist" ${item.category === 'Minimalist' ? 'selected' : ''}>Minimalist</option>
              <option value="Nature" ${item.category === 'Nature' ? 'selected' : ''}>Nature</option>
              <option value="Architecture" ${item.category === 'Architecture' ? 'selected' : ''}>Architecture</option>
              <option value="Fantasy" ${item.category === 'Fantasy' ? 'selected' : ''}>Fantasy</option>
              <option value="Sci-Fi" ${item.category === 'Sci-Fi' ? 'selected' : ''}>Sci-Fi</option>
              <option value="Anime" ${item.category === 'Anime' ? 'selected' : ''}>Anime</option>
              <option value="Abstract" ${item.category === 'Abstract' ? 'selected' : ''}>Abstract</option>
              <option value="Art" ${item.category === 'Art' ? 'selected' : ''}>Art</option>
              <option value="Pop Culture" ${item.category === 'Pop Culture' ? 'selected' : ''}>Pop Culture</option>
              <option value="Quotes" ${item.category === 'Quotes' ? 'selected' : ''}>Quotes</option>
            </select>
          </div>
        </div>
        <button type="button" class="btn-remove bulk-btn-remove" data-idx="${idx}">✕</button>
      `;

      card.querySelector('.bulk-input-title').addEventListener('input', (e) => {
        bulkQueue[idx].title = e.target.value;
      });
      card.querySelector('.bulk-input-author').addEventListener('input', (e) => {
        bulkQueue[idx].author = e.target.value;
      });
      card.querySelector('.bulk-input-category').addEventListener('change', (e) => {
        bulkQueue[idx].category = e.target.value;
      });
      card.querySelector('.bulk-btn-remove').addEventListener('click', () => {
        bulkQueue.splice(idx, 1);
        renderBulkQueue();
      });

      bulkQueueList.appendChild(card);
    });
  }

  if (btnSubmitBulkAll) {
    btnSubmitBulkAll.addEventListener('click', async () => {
      if (bulkQueue.length === 0) return;

      btnSubmitBulkAll.disabled = true;
      btnSubmitBulkAll.textContent = `Uploading batch (1 of ${bulkQueue.length})... ⏳`;

      for (let i = 0; i < bulkQueue.length; i++) {
        const item = bulkQueue[i];
        btnSubmitBulkAll.textContent = `Processing image ${i + 1} of ${bulkQueue.length}... ⏳`;

        let imageUrl = await uploadImageFile(item.file);
        if (!imageUrl) {
          imageUrl = `[Uploaded File: ${item.file.name}]`;
        }

        const issueTitle = encodeURIComponent(`Screensaver Submission: ${item.title}`);
        const bodyLines = [
          `### Screensaver Submission`,
          ``,
          `**Title:** ${item.title}`,
          `**Author:** ${item.author}`,
          `**Category:** ${item.category}`,
          `**Image:** ${imageUrl}`,
          `**Specs:** Batch upload (${(item.file.size / 1024).toFixed(0)} KB)`,
          ``,
          `---`,
          `*Submitted via Storefront Screensaver Catalog Site (Batch Upload ${i + 1}/${bulkQueue.length})*`
        ];

        const issueBody = encodeURIComponent(bodyLines.join('\n'));
        const repoUrl = 'https://github.com/ultimatejimmy/storefront-screensavers';
        const githubIssueUrl = `${repoUrl}/issues/new?title=${issueTitle}&body=${issueBody}`;

        window.open(githubIssueUrl, '_blank');
      }

      btnSubmitBulkAll.disabled = false;
      btnSubmitBulkAll.textContent = `Submit All (${bulkQueue.length}) Wallpapers →`;
      alert(`Opened ${bulkQueue.length} GitHub submission tab(s)! Click submit on each tab to finish.`);
    });
  }

  // --- Suggest Change Drawer Logic ---
  const drawerBackdrop = document.getElementById('suggest-drawer-backdrop');
  const suggestDrawer = document.getElementById('suggest-drawer');
  const btnCloseSuggest = document.getElementById('btn-close-suggest');
  const suggestForm = document.getElementById('suggest-form');
  const suggestTypeSelect = document.getElementById('suggest-type');
  const groupSuggestUrl = document.getElementById('group-suggest-url');

  function openSuggestDrawer(item) {
    if (!suggestDrawer || !drawerBackdrop) return;

    document.getElementById('suggest-item-id').value = item.id || '';
    document.getElementById('suggest-target-img').src = item.thumbnailUrl || '';
    document.getElementById('suggest-target-title').textContent = item.title || 'Wallpaper';
    document.getElementById('suggest-target-author').textContent = `by ${item.author || 'Unknown'}`;

    document.getElementById('suggest-title').value = item.title || '';
    document.getElementById('suggest-author').value = item.author || '';
    document.getElementById('suggest-category').value = item.category || '';
    const suggestTagsEl = document.getElementById('suggest-tags');
    if (suggestTagsEl) {
      suggestTagsEl.value = Array.isArray(item.tags) ? item.tags.join(', ') : (item.tags || '');
    }
    document.getElementById('suggest-reason').value = '';

    suggestDrawer.classList.add('open');
    drawerBackdrop.classList.add('open');
  }

  function closeSuggestDrawer() {
    if (!suggestDrawer || !drawerBackdrop) return;
    suggestDrawer.classList.remove('open');
    drawerBackdrop.classList.remove('open');
  }

  if (btnCloseSuggest) btnCloseSuggest.addEventListener('click', closeSuggestDrawer);
  if (drawerBackdrop) drawerBackdrop.addEventListener('click', closeSuggestDrawer);

  if (suggestTypeSelect && groupSuggestUrl) {
    suggestTypeSelect.addEventListener('change', () => {
      groupSuggestUrl.style.display = (suggestTypeSelect.value === 'replacement') ? 'block' : 'none';
    });
  }

  if (suggestForm) {
    suggestForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const itemId = document.getElementById('suggest-item-id').value;
      const targetTitle = document.getElementById('suggest-target-title').textContent;
      const type = suggestTypeSelect.value;
      const newTitle = document.getElementById('suggest-title').value;
      const newAuthor = document.getElementById('suggest-author').value;
      const newCategory = document.getElementById('suggest-category').value;
      const newTags = document.getElementById('suggest-tags') ? document.getElementById('suggest-tags').value.trim() : '';
      const newUrl = document.getElementById('suggest-url').value;
      const reason = document.getElementById('suggest-reason').value;

      const typeLabels = {
        metadata: 'Metadata Correction',
        replacement: 'Replacement Image',
        issue: 'Low Quality / Issue Report'
      };

      const issueTitle = encodeURIComponent(`Change Suggestion: [${itemId}] ${targetTitle}`);
      const bodyLines = [
        `### Catalog Change Suggestion`,
        ``,
        `**Target Item ID:** \`${itemId}\``,
        `**Change Type:** ${typeLabels[type] || type}`,
        ``,
        `**Proposed Title:** ${newTitle}`,
        `**Proposed Author:** ${newAuthor}`,
        `**Proposed Category:** ${newCategory}`,
      ];

      if (newTags) {
        bodyLines.push(`**Proposed Tags:** ${newTags}`);
      }

      if (type === 'replacement' && newUrl) {
        bodyLines.push(`**Replacement Image URL:** ${newUrl}`);
      }

      bodyLines.push(``, `**Reason / Details:**`, reason, ``, `---`, `*Submitted via Storefront Screensaver Catalog Site*`);

      const issueBody = encodeURIComponent(bodyLines.join('\n'));
      const repoUrl = 'https://github.com/ultimatejimmy/storefront-screensavers';
      const githubIssueUrl = `${repoUrl}/issues/new?title=${issueTitle}&labels=suggest-change&body=${issueBody}`;

      window.open(githubIssueUrl, '_blank');
      closeSuggestDrawer();
    });
  }
});

