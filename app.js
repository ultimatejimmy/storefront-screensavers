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
              item.downloads = r.downloads || 0;
            } else {
              item.likes = 0;
              item.wilson = 0;
              item.downloads = 0;
            }
          });
          applyFilters();
        }
      }
    } catch (e) {
      console.warn('Could not fetch live ratings from worker:', e);
    }
  }

  async function trackWebDownload(itemId) {
    try {
      await fetch(`${RATINGS_API_URL}/download`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify({ repo_id: itemId, item_kind: 'screensaver' })
      });
    } catch (e) {
      console.warn('Could not track download:', e);
    }
  }

  let currentOverlayMode = localStorage.getItem('overlayMode') || 'checkerboard';

  function getItemLikes(item) {
    const r = liveRatings[item.id] || (item.id && liveRatings[item.id.toLowerCase()]);
    if (r) {
      return Math.max(0, (r.up || 0) - (r.down || 0));
    }
    return item.likes || 0;
  }

  function getItemDownloads(item) {
    const r = liveRatings[item.id] || (item.id && liveRatings[item.id.toLowerCase()]);
    if (r && r.downloads !== undefined) {
      return r.downloads;
    }
    return item.downloads || 0;
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
      card.id = `item-${item.id}`;

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
            <span class="card-overlay-badge">by ${authorDisplay}</span>
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
            <button type="button" class="btn-copy-link" title="Copy direct link to wallpaper" data-id="${item.id}">🔗</button>
            <button type="button" class="btn-suggest-change" title="Suggest Change/Report DMCA Takedown" data-id="${item.id}">✏️</button>
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

      // Copy direct link button
      const copyBtn = card.querySelector('.btn-copy-link');
      if (copyBtn) {
        copyBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          const permalink = `${window.location.origin}${window.location.pathname}#item-${item.id}`;
          navigator.clipboard.writeText(permalink).then(() => {
            copyBtn.classList.add('copied');
            copyBtn.textContent = '✓';
            showToast(`Copied direct link for "${item.title}"!`);
            window.history.replaceState(null, '', `#item-${item.id}`);
            setTimeout(() => {
              copyBtn.classList.remove('copied');
              copyBtn.textContent = '🔗';
            }, 2000);
          }).catch(() => {
            prompt('Copy direct link:', permalink);
          });
        });
      }

      // Download button click tracking
      const downloadBtn = card.querySelector('.card-download-btn');
      if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
          const key = item.id;
          if (!liveRatings[key]) liveRatings[key] = { up: 0, down: 0, wilson: 0, downloads: 0 };
          liveRatings[key].downloads = (liveRatings[key].downloads || 0) + 1;
          const dlSpan = card.querySelector('.download-count');
          if (dlSpan) {
            dlSpan.textContent = getItemDownloads(item);
          }
          trackWebDownload(item.id);
        });
      }

      const btnSuggest = card.querySelector('.btn-suggest-change');
      if (btnSuggest) {
        btnSuggest.addEventListener('click', () => openSuggestDrawer(item));
      }

      grid.appendChild(card);
    });

    scrollToCardFromHash();
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
    const sortBy = sortSelect ? sortSelect.value : 'downloads';

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

    if (sortBy === 'newest') {
      filtered.sort((a, b) => {
        if (a.dateAdded && b.dateAdded) return new Date(b.dateAdded) - new Date(a.dateAdded);
        return (b._originalIndex || 0) - (a._originalIndex || 0);
      });
    } else if (sortBy === 'likes') {
      filtered.sort((a, b) => (getItemLikes(b) - getItemLikes(a)) || ((b._originalIndex || 0) - (a._originalIndex || 0)));
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
      // Default: Most Downloaded with newest additions as tiebreaker
      filtered.sort((a, b) => (getItemDownloads(b) - getItemDownloads(a)) || ((b._originalIndex || 0) - (a._originalIndex || 0)));
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

  const ALLOWED_IMAGE_MIMES = ['image/jpeg', 'image/png', 'image/webp'];
  const ALLOWED_IMAGE_EXTS = ['.jpg', '.jpeg', '.png', '.webp'];
  const MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024; // 25 MB limit

  function isValidImageFile(file) {
    if (!file) return { valid: false, error: 'No file selected.' };
    const ext = '.' + (file.name.split('.').pop() || '').toLowerCase();
    if (!ALLOWED_IMAGE_MIMES.includes(file.type) || !ALLOWED_IMAGE_EXTS.includes(ext)) {
      return {
        valid: false,
        error: 'Invalid file format. Only standard raster images (JPG, PNG, WebP) are compatible with KOReader screensavers. Vector/SVG, executable files, and scripts are strictly disallowed.'
      };
    }
    if (file.size > MAX_FILE_SIZE_BYTES) {
      return {
        valid: false,
        error: `File size exceeds 25 MB limit (${(file.size / (1024 * 1024)).toFixed(1)} MB).`
      };
    }
    return { valid: true };
  }

  function handleFileSelect(file) {
    const check = isValidImageFile(file);
    if (!check.valid) {
      alert(check.error);
      return;
    }

    selectedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      const img = new Image();
      img.onload = () => {
        if (img.width < 200 || img.height < 200) {
          alert(`Image dimensions (${img.width}×${img.height} px) are too small for an e-reader screensaver. Minimum resolution is 200×200 px.`);
          selectedFile = null;
          return;
        }
        const kb = (file.size / 1024).toFixed(0);
        selectedFileMeta = `${img.width} × ${img.height} px · ${kb} KB`;
        previewFilename.textContent = file.name;
        previewSpecs.textContent = selectedFileMeta;
        dropzonePrompt.style.display = 'none';
        dropzonePreview.style.display = 'flex';
        initCropper(img);
      };
      img.onerror = () => {
        alert('Failed to decode image data. The file appears to be corrupted or invalid.');
        selectedFile = null;
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }

  // Helper for fetch with timeout
  function fetchWithTimeout(url, options, timeoutMs = 35000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    return fetch(url, { ...options, signal: controller.signal })
      .finally(() => clearTimeout(timeoutId));
  }

  // Upload file anonymously using a 4-tier resilient cascade with dynamic timeouts
  async function uploadImageFile(file, fileName = 'screensaver.jpg', statusCallback = null) {
    const cleanFileName = (fileName || 'screensaver.jpg').replace(/[^a-zA-Z0-9._-]/g, '_');
    const fileSize = (file && file.size) ? file.size : 1024 * 1024;
    // Dynamic timeout: generous 35s base, up to 60s for 10-25MB files
    const timeoutMs = Math.max(35000, Math.min(60000, Math.round(fileSize / 200)));

    // Tier 1: Litterbox (Catbox temporary 72h, CORS enabled)
    try {
      if (statusCallback) statusCallback('Uploading to Catbox (Tier 1)...');
      const formData = new FormData();
      formData.append('reqtype', 'fileupload');
      formData.append('time', '72h');
      formData.append('fileToUpload', file, cleanFileName);
      const res = await fetchWithTimeout('https://litterbox.catbox.moe/resources/internals/api.php', {
        method: 'POST',
        body: formData
      }, timeoutMs);
      if (res.ok) {
        const text = await res.text();
        if (text && text.trim().startsWith('http')) {
          console.log('Tier 1 (Litterbox) upload successful:', text.trim());
          return text.trim();
        }
      }
    } catch (err1) {
      console.warn('Tier 1 (Litterbox) upload attempt failed:', err1);
    }

    // Tier 2: Catbox Permanent (CORS enabled)
    try {
      if (statusCallback) statusCallback('Uploading to Catbox (Tier 2)...');
      const formData = new FormData();
      formData.append('reqtype', 'fileupload');
      formData.append('fileToUpload', file, cleanFileName);
      const res = await fetchWithTimeout('https://catbox.moe/user/api.php', {
        method: 'POST',
        body: formData
      }, timeoutMs);
      if (res.ok) {
        const text = await res.text();
        if (text && text.trim().startsWith('http')) {
          console.log('Tier 2 (Catbox) upload successful:', text.trim());
          return text.trim();
        }
      }
    } catch (err2) {
      console.warn('Tier 2 (Catbox) upload attempt failed:', err2);
    }

    // Tier 3: TmpFiles API (CORS enabled)
    try {
      if (statusCallback) statusCallback('Uploading to TmpFiles (Tier 3)...');
      const formData = new FormData();
      formData.append('file', file, cleanFileName);
      const res = await fetchWithTimeout('https://tmpfiles.org/api/v1/upload', {
        method: 'POST',
        body: formData
      }, timeoutMs);
      if (res.ok) {
        const data = await res.json();
        if (data && data.data && data.data.url) {
          console.log('Tier 3 (TmpFiles) upload successful:', data.data.url);
          return data.data.url;
        }
      }
    } catch (err3) {
      console.warn('Tier 3 (TmpFiles) upload attempt failed:', err3);
    }

    // Tier 4: FreeImage.host API (CORS enabled)
    try {
      if (statusCallback) statusCallback('Uploading to FreeImage (Tier 4)...');
      const formData = new FormData();
      formData.append('key', '6d207e02198a847aa98d0a2a901485a5');
      formData.append('action', 'upload');
      formData.append('format', 'json');
      formData.append('source', file, cleanFileName);
      const res = await fetchWithTimeout('https://freeimage.host/api/1/upload', {
        method: 'POST',
        body: formData
      }, timeoutMs);
      if (res.ok) {
        const data = await res.json();
        if (data && data.image && data.image.url) {
          console.log('Tier 4 (FreeImage) upload successful:', data.image.url);
          return data.image.url;
        }
      }
    } catch (err4) {
      console.warn('Tier 4 (FreeImage) upload attempt failed:', err4);
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

  // --- Shared Cropper Math & Rendering Utilities ---
  function computeFocalPointOffsets(imgObj, zoom = 1) {
    if (!imgObj) return { offsetX: 0, offsetY: 0 };
    const imgW = imgObj.naturalWidth || imgObj.width || 1200;
    const imgH = imgObj.naturalHeight || imgObj.height || 1600;

    const baseScale = Math.max(FRAME_W / imgW, FRAME_H / imgH);
    const scaledW = imgW * baseScale * zoom;
    const scaledH = imgH * baseScale * zoom;

    try {
      const sampleCanvas = document.createElement('canvas');
      const ctx = sampleCanvas.getContext('2d');
      const sW = 64, sH = 64;
      sampleCanvas.width = sW;
      sampleCanvas.height = sH;
      ctx.drawImage(imgObj, 0, 0, sW, sH);
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

      let offX = (FRAME_W / 2) - (scaledW * focalPctX);
      let offY = (FRAME_H / 2) - (scaledH * focalPctY);
      return clampOffsetValues(scaledW, scaledH, offX, offY);
    } catch (err) {
      let offX = (FRAME_W - scaledW) / 2;
      let offY = (FRAME_H - scaledH) / 2;
      return clampOffsetValues(scaledW, scaledH, offX, offY);
    }
  }

  function clampOffsetValues(scaledW, scaledH, offX, offY) {
    const padX = Math.max(0, (FRAME_W - scaledW) / 2);
    const padY = Math.max(0, (FRAME_H - scaledH) / 2);

    const minX = Math.min(0, FRAME_W - scaledW) - padX;
    const maxX = Math.max(0, FRAME_W - scaledW) + padX;
    const minY = Math.min(0, FRAME_H - scaledH) - padY;
    const maxY = Math.max(0, FRAME_H - scaledH) + padY;

    return {
      offsetX: Math.max(minX, Math.min(maxX, offX)),
      offsetY: Math.max(minY, Math.min(maxY, offY))
    };
  }

  function renderCropCanvas(canvas, imgObj, cState, showGuides = true, isTransparent = false) {
    if (!canvas || !imgObj) return;
    const ctx = canvas.getContext('2d');
    const imgW = imgObj.naturalWidth || imgObj.width || 1200;
    const imgH = imgObj.naturalHeight || imgObj.height || 1600;

    const baseScale = Math.max(FRAME_W / imgW, FRAME_H / imgH);
    const scaledW = imgW * baseScale * (cState.zoom || 1);
    const scaledH = imgH * baseScale * (cState.zoom || 1);

    const clamped = clampOffsetValues(scaledW, scaledH, cState.offsetX, cState.offsetY);
    cState.offsetX = clamped.offsetX;
    cState.offsetY = clamped.offsetY;

    if (isTransparent) {
      ctx.clearRect(0, 0, FRAME_W, FRAME_H);
    } else {
      ctx.fillStyle = '#000000';
      ctx.fillRect(0, 0, FRAME_W, FRAME_H);
    }

    ctx.drawImage(imgObj, cState.offsetX, cState.offsetY, scaledW, scaledH);

    if (showGuides) {
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
      ctx.strokeStyle = 'rgba(139, 92, 246, 0.8)';
      ctx.lineWidth = 2;
      ctx.strokeRect(1, 1, FRAME_W - 2, FRAME_H - 2);

      // Draw Cyan Corner Brackets
      const cLen = 16;
      ctx.strokeStyle = '#06b6d4';
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
  }

  function renderExportBlob(imgObj, cState, fileType = 'image/jpeg', fileName = '', isTransparent = false) {
    return new Promise((resolve) => {
      if (!imgObj) {
        resolve(null);
        return;
      }
      const outCanvas = document.createElement('canvas');
      const TARGET_W = 1860;
      const TARGET_H = 2480;
      outCanvas.width = TARGET_W;
      outCanvas.height = TARGET_H;
      const ctx = outCanvas.getContext('2d');

      const imgW = imgObj.naturalWidth || imgObj.width || 1200;
      const imgH = imgObj.naturalHeight || imgObj.height || 1600;

      const baseScale = Math.max(FRAME_W / imgW, FRAME_H / imgH);
      const scaledW = imgW * baseScale * (cState.zoom || 1);
      const scaledH = imgH * baseScale * (cState.zoom || 1);

      const scaleFactor = TARGET_W / FRAME_W;
      const drawX = cState.offsetX * scaleFactor;
      const drawY = cState.offsetY * scaleFactor;
      const drawW = scaledW * scaleFactor;
      const drawH = scaledH * scaleFactor;

      const isPng = (fileType === 'image/png' || (fileName && fileName.toLowerCase().endsWith('.png')));

      if (!isPng && !isTransparent) {
        ctx.fillStyle = '#000000';
        ctx.fillRect(0, 0, TARGET_W, TARGET_H);
      } else {
        ctx.clearRect(0, 0, TARGET_W, TARGET_H);
      }
      ctx.drawImage(imgObj, drawX, drawY, drawW, drawH);

      const exportMime = (isPng || isTransparent) ? 'image/png' : 'image/jpeg';
      const exportQuality = (isPng || isTransparent) ? undefined : 0.92;

      outCanvas.toBlob((blob) => {
        resolve(blob);
      }, exportMime, exportQuality);
    });
  }

  function renderThumbnailDataUrl(imgObj, cState, thumbW = 76, thumbH = 101, isTransparent = false) {
    if (!imgObj) return '';
    const tCanvas = document.createElement('canvas');
    tCanvas.width = thumbW;
    tCanvas.height = thumbH;
    const ctx = tCanvas.getContext('2d');

    const imgW = imgObj.naturalWidth || imgObj.width || 1200;
    const imgH = imgObj.naturalHeight || imgObj.height || 1600;

    const baseScale = Math.max(FRAME_W / imgW, FRAME_H / imgH);
    const scaledW = imgW * baseScale * (cState.zoom || 1);
    const scaledH = imgH * baseScale * (cState.zoom || 1);

    const scaleFactor = thumbW / FRAME_W;
    const drawX = cState.offsetX * scaleFactor;
    const drawY = cState.offsetY * scaleFactor;
    const drawW = scaledW * scaleFactor;
    const drawH = scaledH * scaleFactor;

    if (!isTransparent) {
      ctx.fillStyle = '#000000';
      ctx.fillRect(0, 0, thumbW, thumbH);
    } else {
      ctx.clearRect(0, 0, thumbW, thumbH);
    }
    ctx.drawImage(imgObj, drawX, drawY, drawW, drawH);
    return tCanvas.toDataURL('image/jpeg', 0.85);
  }

  function autoDetectFocalPoint() {
    if (!cropImageObj || !cropperCanvas) return;
    const offsets = computeFocalPointOffsets(cropImageObj, cropState.zoom);
    cropState.offsetX = offsets.offsetX;
    cropState.offsetY = offsets.offsetY;
    drawCropper();
  }

  function drawCropper() {
    if (!cropImageObj || !cropperCanvas) return;
    const isTransCat = document.getElementById('sub-category') && document.getElementById('sub-category').value.toLowerCase().includes('transparent');
    renderCropCanvas(cropperCanvas, cropImageObj, cropState, true, isTransCat);
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
    if (!cropImageObj) return Promise.resolve(selectedFile);
    const isTransCat = document.getElementById('sub-category') && document.getElementById('sub-category').value.toLowerCase().includes('transparent');
    return renderExportBlob(cropImageObj, cropState, selectedFile ? selectedFile.type : 'image/jpeg', selectedFile ? selectedFile.name : '', isTransCat)
      .then(blob => blob || selectedFile);
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

        const fileName = selectedFile.name || 'screensaver.jpg';
        const fileMeta = selectedFileMeta || `${(selectedFile.size / 1024).toFixed(0)} KB`;

        if (btnSubmitIssue) {
          btnSubmitIssue.textContent = 'Processing 3:4 crop... ⏳';
          btnSubmitIssue.disabled = true;
        }

        // Get 3:4 cropped image blob
        const fileToUpload = await getCroppedBlob();

        // Copy cropped file to clipboard immediately as a universal convenience/backup
        try {
          if (navigator.clipboard && window.ClipboardItem && fileToUpload) {
            await navigator.clipboard.write([
              new ClipboardItem({ [fileToUpload.type || selectedFile.type || 'image/jpeg']: fileToUpload })
            ]);
          }
        } catch (clipErr) {
          console.log('Clipboard auto-copy:', clipErr);
        }

        // Try automatic image host upload with status updates
        const uploadedUrl = await uploadImageFile(fileToUpload, fileName, (msg) => {
          if (btnSubmitIssue) btnSubmitIssue.textContent = `${msg} ⏳`;
        });

        if (uploadedUrl) {
          imageUrl = uploadedUrl;
          fileNotice = 'Image automatically uploaded! A Pull Request will be created for review.';
        } else {
          imageUrl = `[Uploaded File: ${fileName} (${fileMeta})]`;
          fileNotice = 'Image copied to your clipboard! Press Ctrl+V / Cmd+V in the GitHub issue to attach directly.';
          alert('Image host upload was blocked or timed out. Your cropped image has been copied to your clipboard—simply press Ctrl+V / Cmd+V in the GitHub issue description to attach it!');
        }

        if (btnSubmitIssue) {
          btnSubmitIssue.textContent = 'Continue to GitHub Submission →';
          btnSubmitIssue.disabled = false;
        }
      } else {
        imageUrl = document.getElementById('sub-url').value;
      }

      const subTags = document.getElementById('sub-tags') ? document.getElementById('sub-tags').value.trim() : '';
      const fileName = (currentMode === 'file' && selectedFile) ? selectedFile.name : (imageUrl.split('/').pop().split('?')[0] || 'screensaver.jpg');

      const issueTitle = encodeURIComponent(`Screensaver Submission: ${title}`);
      const bodyLines = [
        `### Screensaver Submission`,
        ``,
        `**Title:** ${title}`,
        `**Author:** ${author}`,
        `**Category:** ${category}`,
        `**Filename:** ${fileName}`,
      ];

      if (subTags) {
        bodyLines.push(`**Tags:** ${subTags}`);
      }

      bodyLines.push(`**Image:** ${imageUrl}`);

      if (imageUrl && imageUrl.startsWith('http')) {
        bodyLines.push(``, `### Image Preview`, `![${title}](${imageUrl})`);
      }

      if (selectedFileMeta) {
        bodyLines.push(``, `**Specs:** ${selectedFileMeta}`);
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

  // --- Bulk Queue & Batch Logic ---
  const ALL_SUBMIT_CATEGORIES = [
    'Minimalist',
    'Nature',
    'Architecture',
    'Fantasy',
    'Sci-Fi',
    'Anime',
    'Abstract',
    'Art',
    'Pop Culture',
    'Quotes',
    'Religion',
    'Transparent'
  ];

  const bulkDropzoneBox = document.getElementById('bulk-dropzone-box');
  const subBulkFiles = document.getElementById('sub-bulk-files');
  const bulkQueueList = document.getElementById('bulk-queue-list');
  const bulkBatchToolbar = document.getElementById('bulk-batch-toolbar');
  const btnSubmitBulkAll = document.getElementById('btn-submit-bulk-all');
  const subBulkAgree = document.getElementById('sub-bulk-agree');

  // Batch toolbar elements
  const bulkBatchAuthorInput = document.getElementById('bulk-batch-author-input');
  const btnBatchApplyAuthor = document.getElementById('btn-batch-apply-author');
  const btnBatchApplyCategory = document.getElementById('btn-batch-apply-category');
  const bulkBatchTagsInput = document.getElementById('bulk-batch-tags-input');
  const btnBatchApplyTags = document.getElementById('btn-batch-apply-tags');
  const btnBatchAutofocalAll = document.getElementById('btn-batch-autofocal-all');
  const btnBulkClearAll = document.getElementById('btn-bulk-clear-all');

  // Batch Category Pills Toggle Handler
  const batchCategoryPills = document.querySelectorAll('#batch-category-pills .cat-pill');
  if (batchCategoryPills) {
    batchCategoryPills.forEach(pill => {
      pill.addEventListener('click', (e) => {
        e.preventDefault();
        pill.classList.toggle('active');
      });
    });
  }

  // Modal Editor elements
  const imageEditorModalBackdrop = document.getElementById('image-editor-modal-backdrop');
  const editorModalHeading = document.getElementById('editor-modal-heading');
  const btnCloseEditorModal = document.getElementById('btn-close-editor-modal');
  const btnCancelEditorModal = document.getElementById('btn-cancel-editor-modal');
  const btnSaveEditorModal = document.getElementById('btn-save-editor-modal');
  const modalCropperCanvas = document.getElementById('modal-cropper-canvas');
  const modalCropZoomSlider = document.getElementById('modal-crop-zoom-slider');
  const modalZoomVal = document.getElementById('modal-zoom-val');
  const btnModalAutoFocal = document.getElementById('btn-modal-auto-focal');
  const btnModalCenterFit = document.getElementById('btn-modal-center-fit');
  const modalOrigSpecs = document.getElementById('modal-orig-specs');

  let bulkQueue = []; // items: { id, file, title, author, category, tags, cropState, previewUrl, imgObj }
  let activeModalItem = null;
  let modalCropState = { zoom: 1, offsetX: 0, offsetY: 0, isDragging: false, startX: 0, startY: 0 };

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
    const rawFiles = Array.from(files);
    let rejectedCount = 0;
    const validFiles = rawFiles.filter(f => {
      const check = isValidImageFile(f);
      if (!check.valid) {
        rejectedCount++;
        return false;
      }
      return true;
    }).slice(0, 10);

    if (rejectedCount > 0) {
      alert(`${rejectedCount} file(s) were skipped because they are not valid JPG, PNG, or WebP images or exceed 25 MB.`);
    }

    if (validFiles.length === 0) return;

    // Check if batch category pills have selections to apply as default
    const batchActiveCats = Array.from(document.querySelectorAll('#batch-category-pills .cat-pill.active'))
      .map(p => p.getAttribute('data-value'));
    const defaultCat = batchActiveCats.length > 0 ? batchActiveCats.join(', ') : 'Minimalist';
    const batchAuthor = (bulkBatchAuthorInput && bulkBatchAuthorInput.value.trim()) ? bulkBatchAuthorInput.value.trim() : '';

    validFiles.forEach(file => {
      const qId = 'bulk-' + Date.now() + '-' + Math.random().toString(36).substring(2, 7);
      const cleanTitle = file.name.replace(/\.[^/.]+$/, "").replace(/[-_]/g, " ");
      const formattedTitle = cleanTitle.charAt(0).toUpperCase() + cleanTitle.slice(1);

      const queueItem = {
        id: qId,
        file: file,
        title: formattedTitle,
        author: batchAuthor,
        category: defaultCat,
        tags: '',
        cropState: { zoom: 1, offsetX: 0, offsetY: 0, isCustom: false },
        previewUrl: URL.createObjectURL(file),
        imgObj: null
      };

      bulkQueue.push(queueItem);

      // Preload image for focal analysis and 3:4 crop previews
      const img = new Image();
      img.onload = () => {
        queueItem.imgObj = img;
        const offsets = computeFocalPointOffsets(img, 1);
        queueItem.cropState.offsetX = offsets.offsetX;
        queueItem.cropState.offsetY = offsets.offsetY;
        const thumbUrl = renderThumbnailDataUrl(img, queueItem.cropState, 76, 101, queueItem.category.toLowerCase().includes('transparent'));
        if (thumbUrl) {
          queueItem.previewUrl = thumbUrl;
        }
        renderBulkQueue();
      };
      img.src = queueItem.previewUrl;
    });

    renderBulkQueue();
  }

  function renderBulkQueue() {
    if (!bulkQueueList) return;
    bulkQueueList.innerHTML = '';

    if (bulkQueue.length === 0) {
      if (btnSubmitBulkAll) btnSubmitBulkAll.style.display = 'none';
      if (bulkBatchToolbar) bulkBatchToolbar.style.display = 'none';
      return;
    }

    if (bulkBatchToolbar) {
      bulkBatchToolbar.style.display = 'block';
    }

    if (btnSubmitBulkAll) {
      btnSubmitBulkAll.style.display = 'block';
      btnSubmitBulkAll.textContent = `Submit All (${bulkQueue.length}) Wallpapers →`;
    }

    bulkQueue.forEach((item, idx) => {
      const card = document.createElement('div');
      card.className = 'bulk-item-card';

      const currentCats = (item.category || 'Minimalist').split(',').map(c => c.trim()).filter(Boolean);

      const pillsHtml = ALL_SUBMIT_CATEGORIES.map(cat => {
        const isActive = currentCats.includes(cat);
        return `<button type="button" class="tag-btn cat-pill ${isActive ? 'active' : ''}" data-cat="${cat}">${cat}</button>`;
      }).join('');

      const cropStatusText = item.cropState && item.cropState.isCustom
        ? `✓ Custom (${item.cropState.zoom.toFixed(1)}x)`
        : `⚡ Auto-crop (3:4)`;
      const cropBadgeClass = item.cropState && item.cropState.isCustom ? 'bulk-crop-status-badge customized' : 'bulk-crop-status-badge';

      card.innerHTML = `
        <div class="bulk-item-thumb-wrap" title="Click to edit 3:4 crop">
          <img class="bulk-item-thumb" src="${item.previewUrl}" alt="Queue Thumbnail">
          <div class="bulk-thumb-edit-overlay">
            <span>✂️</span>
            <span>Edit</span>
          </div>
        </div>
        <div class="bulk-item-fields">
          <input type="text" class="form-control bulk-input-title" data-idx="${idx}" value="${item.title}" placeholder="Title" required>
          <div style="display: flex; gap: 0.5rem;">
            <input type="text" class="form-control bulk-input-author" data-idx="${idx}" value="${item.author}" placeholder="Creator/Artist" style="flex: 1;">
          </div>
          <div class="bulk-item-categories">
            <span class="bulk-item-cat-label">Categories (select all that apply):</span>
            <div class="category-pills bulk-item-category-pills" data-idx="${idx}">
              ${pillsHtml}
            </div>
          </div>
          <input type="text" class="form-control bulk-input-tags" data-idx="${idx}" value="${item.tags || ''}" placeholder="Tags/keywords (e.g. anime, landscape, dark, minimal)...">
          <div class="bulk-card-actions">
            <button type="button" class="btn-bulk-crop-edit" data-idx="${idx}" title="Open 3:4 E-Ink screen cropper">
              <span>✂️</span>
              <span>Edit & Crop (3:4)</span>
            </button>
            <span class="${cropBadgeClass}">${cropStatusText}</span>
          </div>
        </div>
        <button type="button" class="btn-remove bulk-btn-remove" data-idx="${idx}" title="Remove from queue">✕</button>
      `;

      card.querySelector('.bulk-input-title').addEventListener('input', (e) => {
        bulkQueue[idx].title = e.target.value;
      });

      card.querySelector('.bulk-input-author').addEventListener('input', (e) => {
        bulkQueue[idx].author = e.target.value;
      });

      card.querySelectorAll('.bulk-item-category-pills .cat-pill').forEach(pill => {
        pill.addEventListener('click', (e) => {
          e.preventDefault();
          pill.classList.toggle('active');
          const activePills = card.querySelectorAll('.bulk-item-category-pills .cat-pill.active');
          if (activePills.length === 0) {
            pill.classList.add('active'); // keep at least 1 selected
          }
          const selected = Array.from(card.querySelectorAll('.bulk-item-category-pills .cat-pill.active'))
            .map(p => p.getAttribute('data-cat'));
          bulkQueue[idx].category = selected.join(', ');

          if (bulkQueue[idx].imgObj) {
            const isTrans = bulkQueue[idx].category.toLowerCase().includes('transparent');
            bulkQueue[idx].previewUrl = renderThumbnailDataUrl(bulkQueue[idx].imgObj, bulkQueue[idx].cropState, 76, 101, isTrans);
            const thumbEl = card.querySelector('.bulk-item-thumb');
            if (thumbEl) thumbEl.src = bulkQueue[idx].previewUrl;
          }
        });
      });

      card.querySelector('.bulk-input-tags').addEventListener('input', (e) => {
        bulkQueue[idx].tags = e.target.value;
      });

      card.querySelector('.bulk-item-thumb-wrap').addEventListener('click', () => {
        openImageEditorModal(bulkQueue[idx]);
      });

      card.querySelector('.btn-bulk-crop-edit').addEventListener('click', () => {
        openImageEditorModal(bulkQueue[idx]);
      });

      card.querySelector('.bulk-btn-remove').addEventListener('click', () => {
        bulkQueue.splice(idx, 1);
        renderBulkQueue();
      });

      bulkQueueList.appendChild(card);
    });
  }

  // --- Batch Toolbar Action Listeners ---
  if (btnBatchApplyAuthor && bulkBatchAuthorInput) {
    btnBatchApplyAuthor.addEventListener('click', () => {
      const val = bulkBatchAuthorInput.value.trim();
      if (!val) {
        alert('Please enter a Creator/Artist name to apply to all items.');
        return;
      }
      bulkQueue.forEach(item => { item.author = val; });
      renderBulkQueue();
      showToast(`Applied author "${val}" to all ${bulkQueue.length} wallpapers!`);
    });
  }

  if (btnBatchApplyCategory) {
    btnBatchApplyCategory.addEventListener('click', () => {
      const activePills = document.querySelectorAll('#batch-category-pills .cat-pill.active');
      const selectedCats = Array.from(activePills).map(p => p.getAttribute('data-value'));
      if (selectedCats.length === 0) {
        alert('Please select at least one Category from the pills above to apply to all items.');
        return;
      }
      const val = selectedCats.join(', ');
      bulkQueue.forEach(item => {
        item.category = val;
        if (item.imgObj) {
          item.previewUrl = renderThumbnailDataUrl(item.imgObj, item.cropState, 76, 101, val.toLowerCase().includes('transparent'));
        }
      });
      renderBulkQueue();
      showToast(`Applied categories "${val}" to all ${bulkQueue.length} wallpapers!`);
    });
  }

  if (btnBatchApplyTags && bulkBatchTagsInput) {
    btnBatchApplyTags.addEventListener('click', () => {
      const val = bulkBatchTagsInput.value.trim();
      if (!val) {
        alert('Please enter tags to add to all items.');
        return;
      }
      bulkQueue.forEach(item => {
        if (!item.tags) {
          item.tags = val;
        } else {
          const currentTags = item.tags.split(',').map(t => t.trim());
          const newTags = val.split(',').map(t => t.trim());
          const merged = Array.from(new Set([...currentTags, ...newTags])).join(', ');
          item.tags = merged;
        }
      });
      renderBulkQueue();
      showToast(`Added tags to all ${bulkQueue.length} wallpapers!`);
    });
  }

  if (btnBatchAutofocalAll) {
    btnBatchAutofocalAll.addEventListener('click', () => {
      if (bulkQueue.length === 0) return;
      bulkQueue.forEach(item => {
        if (item.imgObj) {
          const offsets = computeFocalPointOffsets(item.imgObj, item.cropState.zoom || 1);
          item.cropState.offsetX = offsets.offsetX;
          item.cropState.offsetY = offsets.offsetY;
          item.previewUrl = renderThumbnailDataUrl(item.imgObj, item.cropState, 76, 101, item.category.toLowerCase().includes('transparent'));
        }
      });
      renderBulkQueue();
      showToast(`Auto-detected subject crops for all ${bulkQueue.length} wallpapers!`);
    });
  }

  if (btnBulkClearAll) {
    btnBulkClearAll.addEventListener('click', () => {
      if (bulkQueue.length === 0) return;
      if (confirm('Clear all wallpapers from the bulk queue?')) {
        bulkQueue = [];
        renderBulkQueue();
      }
    });
  }

  // --- Image Editor & Cropper Modal Logic ---
  function openImageEditorModal(item) {
    activeModalItem = item;
    if (!activeModalItem) return;

    if (editorModalHeading) {
      editorModalHeading.textContent = `Crop "${item.title}"`;
    }

    if (modalCropperCanvas) {
      modalCropperCanvas.width = FRAME_W;
      modalCropperCanvas.height = FRAME_H;
    }

    modalCropState = {
      zoom: item.cropState.zoom || 1,
      offsetX: item.cropState.offsetX || 0,
      offsetY: item.cropState.offsetY || 0,
      isDragging: false,
      startX: 0,
      startY: 0
    };

    if (modalCropZoomSlider) {
      modalCropZoomSlider.value = modalCropState.zoom;
    }
    if (modalZoomVal) {
      modalZoomVal.textContent = modalCropState.zoom.toFixed(1) + 'x';
    }

    if (modalOrigSpecs && item.imgObj) {
      modalOrigSpecs.textContent = `${item.imgObj.naturalWidth || item.imgObj.width} × ${item.imgObj.naturalHeight || item.imgObj.height} px · ${(item.file.size / 1024).toFixed(0)} KB`;
    }

    if (!item.imgObj) {
      const tempImg = new Image();
      tempImg.onload = () => {
        item.imgObj = tempImg;
        if (modalOrigSpecs) {
          modalOrigSpecs.textContent = `${tempImg.naturalWidth} × ${tempImg.naturalHeight} px · ${(item.file.size / 1024).toFixed(0)} KB`;
        }
        drawModalCropper();
      };
      tempImg.src = URL.createObjectURL(item.file);
    } else {
      drawModalCropper();
    }

    if (imageEditorModalBackdrop) {
      imageEditorModalBackdrop.style.display = 'flex';
      setTimeout(() => imageEditorModalBackdrop.classList.add('open'), 10);
    }
  }

  function closeImageEditorModal() {
    if (!imageEditorModalBackdrop) return;
    imageEditorModalBackdrop.classList.remove('open');
    setTimeout(() => {
      imageEditorModalBackdrop.style.display = 'none';
      activeModalItem = null;
    }, 250);
  }

  function drawModalCropper() {
    if (!activeModalItem || !activeModalItem.imgObj || !modalCropperCanvas) return;
    const isTrans = activeModalItem.category && activeModalItem.category.toLowerCase().includes('transparent');
    renderCropCanvas(modalCropperCanvas, activeModalItem.imgObj, modalCropState, true, isTrans);
  }

  if (modalCropperCanvas) {
    modalCropperCanvas.addEventListener('mousedown', (e) => {
      modalCropState.isDragging = true;
      modalCropState.startX = e.clientX - modalCropState.offsetX;
      modalCropState.startY = e.clientY - modalCropState.offsetY;
    });

    window.addEventListener('mousemove', (e) => {
      if (!modalCropState.isDragging || !activeModalItem) return;
      modalCropState.offsetX = e.clientX - modalCropState.startX;
      modalCropState.offsetY = e.clientY - modalCropState.startY;
      drawModalCropper();
    });

    window.addEventListener('mouseup', () => {
      modalCropState.isDragging = false;
    });

    modalCropperCanvas.addEventListener('touchstart', (e) => {
      if (e.touches.length === 1) {
        modalCropState.isDragging = true;
        modalCropState.startX = e.touches[0].clientX - modalCropState.offsetX;
        modalCropState.startY = e.touches[0].clientY - modalCropState.offsetY;
      }
    });

    window.addEventListener('touchmove', (e) => {
      if (!modalCropState.isDragging || !activeModalItem || e.touches.length !== 1) return;
      modalCropState.offsetX = e.touches[0].clientX - modalCropState.startX;
      modalCropState.offsetY = e.touches[0].clientY - modalCropState.startY;
      drawModalCropper();
    });

    window.addEventListener('touchend', () => {
      modalCropState.isDragging = false;
    });
  }

  if (modalCropZoomSlider) {
    modalCropZoomSlider.addEventListener('input', (e) => {
      modalCropState.zoom = parseFloat(e.target.value);
      if (modalZoomVal) modalZoomVal.textContent = modalCropState.zoom.toFixed(1) + 'x';
      drawModalCropper();
    });
  }

  if (btnModalAutoFocal) {
    btnModalAutoFocal.addEventListener('click', (e) => {
      e.preventDefault();
      if (!activeModalItem || !activeModalItem.imgObj) return;
      const offsets = computeFocalPointOffsets(activeModalItem.imgObj, modalCropState.zoom);
      modalCropState.offsetX = offsets.offsetX;
      modalCropState.offsetY = offsets.offsetY;
      drawModalCropper();
    });
  }

  if (btnModalCenterFit) {
    btnModalCenterFit.addEventListener('click', (e) => {
      e.preventDefault();
      if (!activeModalItem || !activeModalItem.imgObj) return;
      modalCropState.zoom = 1;
      if (modalCropZoomSlider) modalCropZoomSlider.value = 1;
      if (modalZoomVal) modalZoomVal.textContent = '1.0x';

      const imgW = activeModalItem.imgObj.naturalWidth || activeModalItem.imgObj.width || 1200;
      const imgH = activeModalItem.imgObj.naturalHeight || activeModalItem.imgObj.height || 1600;
      const baseScale = Math.max(FRAME_W / imgW, FRAME_H / imgH);
      const scaledW = imgW * baseScale;
      const scaledH = imgH * baseScale;

      modalCropState.offsetX = (FRAME_W - scaledW) / 2;
      modalCropState.offsetY = (FRAME_H - scaledH) / 2;
      drawModalCropper();
    });
  }

  if (btnSaveEditorModal) {
    btnSaveEditorModal.addEventListener('click', () => {
      if (!activeModalItem || !activeModalItem.imgObj) return;
      activeModalItem.cropState = {
        zoom: modalCropState.zoom,
        offsetX: modalCropState.offsetX,
        offsetY: modalCropState.offsetY,
        isCustom: true
      };

      const isTrans = activeModalItem.category && activeModalItem.category.toLowerCase().includes('transparent');
      activeModalItem.previewUrl = renderThumbnailDataUrl(activeModalItem.imgObj, activeModalItem.cropState, 76, 101, isTrans);

      renderBulkQueue();
      showToast(`Updated 3:4 crop for "${activeModalItem.title}"!`);
      closeImageEditorModal();
    });
  }

  if (btnCloseEditorModal) btnCloseEditorModal.addEventListener('click', closeImageEditorModal);
  if (btnCancelEditorModal) btnCancelEditorModal.addEventListener('click', closeImageEditorModal);
  if (imageEditorModalBackdrop) {
    imageEditorModalBackdrop.addEventListener('click', (e) => {
      if (e.target === imageEditorModalBackdrop) closeImageEditorModal();
    });
  }

  // --- Bulk Submit All Handler ---
  if (btnSubmitBulkAll) {
    btnSubmitBulkAll.addEventListener('click', async () => {
      if (bulkQueue.length === 0) return;

      if (subBulkAgree && !subBulkAgree.checked) {
        alert('Please check the Community Agreement box to proceed with batch submission.');
        subBulkAgree.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return;
      }

      btnSubmitBulkAll.disabled = true;
      btnSubmitBulkAll.textContent = `Uploading batch (0 of ${bulkQueue.length})... ⏳`;

      const processedItems = [];
      const failedItems = [];

      for (let i = 0; i < bulkQueue.length; i++) {
        const item = bulkQueue[i];
        const fileName = item.file.name || `screensaver_${i + 1}.jpg`;
        const isTrans = item.category && item.category.toLowerCase().includes('transparent');

        // Render high-res 1860x2480 3:4 cropped blob
        let fileToUpload = item.file;
        if (item.imgObj) {
          const croppedBlob = await renderExportBlob(item.imgObj, item.cropState, item.file.type, fileName, isTrans);
          if (croppedBlob) {
            fileToUpload = croppedBlob;
          }
        }

        let imageUrl = await uploadImageFile(fileToUpload, fileName, (msg) => {
          if (btnSubmitBulkAll) {
            btnSubmitBulkAll.textContent = `[${i + 1}/${bulkQueue.length}] ${msg} ⏳`;
          }
        });

        if (!imageUrl) {
          imageUrl = `[Uploaded File: ${fileName}]`;
          failedItems.push(item);
        }

        processedItems.push({
          title: item.title,
          author: item.author && item.author.trim() ? item.author.trim() : 'Community',
          category: item.category || 'General',
          tags: item.tags && item.tags.trim() ? item.tags.trim() : '',
          fileName: fileName,
          imageUrl: imageUrl,
          fileSizeKb: (item.file.size / 1024).toFixed(0)
        });
      }

      if (failedItems.length > 0) {
        // Try copying the first failed image to clipboard so the user can easily paste it
        try {
          if (navigator.clipboard && window.ClipboardItem && failedItems[0].file) {
            await navigator.clipboard.write([
              new ClipboardItem({ [failedItems[0].file.type || 'image/jpeg']: failedItems[0].file })
            ]);
          }
        } catch (clipErr) {
          console.log('Clipboard copy note:', clipErr);
        }
        alert(`Note: ${failedItems.length} wallpaper(s) could not be uploaded to the CDN automatically. The first one has been copied to your clipboard—you can attach/paste it directly in the GitHub issue comment box!`);
      }

      btnSubmitBulkAll.textContent = `Preparing GitHub submission... ⏳`;

      // Build single unified issue body
      let issueTitle = '';
      const bodyLines = [];

      if (processedItems.length === 1) {
        const item = processedItems[0];
        issueTitle = encodeURIComponent(`Screensaver Submission: ${item.title}`);
        bodyLines.push(
          `### Screensaver Submission`,
          ``,
          `**Title:** ${item.title}`,
          `**Author:** ${item.author}`,
          `**Category:** ${item.category}`,
          `**Filename:** ${item.fileName}`
        );
        if (item.tags) bodyLines.push(`**Tags:** ${item.tags}`);
        bodyLines.push(`**Image:** ${item.imageUrl}`);
        if (item.imageUrl && item.imageUrl.startsWith('http')) {
          bodyLines.push(``, `### Image Preview`, `![${item.title}](${item.imageUrl})`);
        }
        bodyLines.push(
          ``,
          `**Specs:** 3:4 E-Ink optimized (${item.fileSizeKb} KB)`,
          ``,
          `---`,
          `*Submitted via Storefront Screensaver Catalog Site*`
        );
      } else {
        const titlesSample = processedItems.map(p => p.title).slice(0, 3).join(', ');
        const extraCount = processedItems.length > 3 ? ` +${processedItems.length - 3} more` : '';
        issueTitle = encodeURIComponent(`Batch Screensaver Submission: ${processedItems.length} Wallpapers (${titlesSample}${extraCount})`);

        bodyLines.push(
          `### Batch Screensaver Submission (${processedItems.length} Wallpapers)`,
          ``,
          `The following ${processedItems.length} screensaver wallpapers are submitted as a batch. Automated PRs will be created for each image:`,
          ``
        );

        processedItems.forEach((item, idx) => {
          bodyLines.push(
            `---`,
            ``,
            `#### Wallpaper ${idx + 1}: ${item.title}`,
            `- **Title:** ${item.title}`,
            `- **Author:** ${item.author}`,
            `- **Category:** ${item.category}`,
            `- **Filename:** ${item.fileName}`
          );
          if (item.tags) bodyLines.push(`- **Tags:** ${item.tags}`);
          bodyLines.push(`- **Image:** ${item.imageUrl}`);
          if (item.imageUrl && item.imageUrl.startsWith('http')) {
            bodyLines.push(``, `![${item.title}](${item.imageUrl})`);
          }
          bodyLines.push(``);
        });

        bodyLines.push(
          `---`,
          `*Submitted via Storefront Screensaver Catalog Site (Batch Upload of ${processedItems.length} Wallpapers)*`
        );
      }

      const issueBody = encodeURIComponent(bodyLines.join('\n'));
      const repoUrl = 'https://github.com/ultimatejimmy/storefront-screensavers';
      const githubIssueUrl = `${repoUrl}/issues/new?title=${issueTitle}&body=${issueBody}`;

      window.open(githubIssueUrl, '_blank');

      btnSubmitBulkAll.disabled = false;
      btnSubmitBulkAll.textContent = `Submit All (${bulkQueue.length}) Wallpapers →`;
      showToast(`Opened 1 GitHub issue tab with all ${bulkQueue.length} wallpapers! Click "Submit new issue" to finish.`);
    });
  }

  // --- Toast Notification Helper ---
  function showToast(message) {
    let toast = document.getElementById('catalog-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'catalog-toast';
      toast.className = 'toast-notice';
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 2800);
  }

  // --- Scroll to Card from URL Hash ---
  function scrollToCardFromHash() {
    if (!window.location.hash) return;
    const rawHash = window.location.hash.replace(/^#/, '');
    const targetId = rawHash.startsWith('item-') ? rawHash : `item-${rawHash}`;
    const targetEl = document.getElementById(targetId);
    if (targetEl) {
      setTimeout(() => {
        targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        targetEl.classList.add('card-highlight');
        setTimeout(() => targetEl.classList.remove('card-highlight'), 3000);
      }, 300);
    }
  }
  window.addEventListener('hashchange', scrollToCardFromHash);

  const drawerBackdrop = document.getElementById('suggest-drawer-backdrop');
  const suggestDrawer = document.getElementById('suggest-drawer');
  const drawerHeadingTitle = document.getElementById('drawer-heading-title');
  const btnCloseSuggest = document.getElementById('btn-close-suggest');
  const suggestForm = document.getElementById('suggest-form');
  const suggestTypeSelect = document.getElementById('suggest-type');
  const drawerTabBtns = document.querySelectorAll('#drawer-action-tabs .drawer-tab-btn');
  const groupSuggestUrl = document.getElementById('group-suggest-url');
  const groupDmcaFields = document.getElementById('group-dmca-fields');
  const groupMetadataFields = document.getElementById('group-metadata-fields');
  const labelSuggestReason = document.getElementById('label-suggest-reason');
  const btnSubmitSuggest = document.getElementById('btn-submit-suggest');

  function setDrawerTab(type) {
    if (suggestTypeSelect) {
      suggestTypeSelect.value = type;
    }
    drawerTabBtns.forEach(btn => {
      if (btn.getAttribute('data-type') === type) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    if (drawerHeadingTitle) {
      if (type === 'dmca') {
        drawerHeadingTitle.textContent = '🛡️ File DMCA Takedown Notice';
      } else if (type === 'replacement') {
        drawerHeadingTitle.textContent = '🖼️ Suggest Replacement Image';
      } else if (type === 'issue') {
        drawerHeadingTitle.textContent = '⚠️ Report Issue/Quality';
      } else {
        drawerHeadingTitle.textContent = '✏️ Suggest a Change';
      }
    }

    updateDrawerFormState();
  }

  drawerTabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const type = btn.getAttribute('data-type');
      setDrawerTab(type);
    });
  });

  function updateDrawerFormState() {
    if (!suggestTypeSelect) return;
    const type = suggestTypeSelect.value;
    const isDmca = (type === 'dmca');
    const isReplacement = (type === 'replacement');

    if (groupDmcaFields) {
      groupDmcaFields.style.display = isDmca ? 'block' : 'none';
    }
    if (groupMetadataFields) {
      groupMetadataFields.style.display = isDmca ? 'none' : 'block';
    }
    if (groupSuggestUrl) {
      groupSuggestUrl.style.display = isReplacement ? 'block' : 'none';
    }
    if (labelSuggestReason) {
      labelSuggestReason.textContent = isDmca 
        ? 'Infringement Description & Ownership Details' 
        : 'Reason/Additional Notes';
    }
    if (btnSubmitSuggest) {
      btnSubmitSuggest.textContent = isDmca 
        ? 'Submit DMCA Notice on GitHub →' 
        : 'Submit Suggestion on GitHub →';
    }
  }

  function openSuggestDrawer(item, defaultType = 'metadata') {
    if (!suggestDrawer || !drawerBackdrop) return;

    document.getElementById('suggest-item-id').value = item.id || '';
    document.getElementById('suggest-target-img').src = item.thumbnailUrl || '';
    document.getElementById('suggest-target-title').textContent = item.title || 'Wallpaper';
    document.getElementById('suggest-target-author').textContent = `by ${item.author || 'Unknown'}`;

    setDrawerTab(defaultType);

    document.getElementById('suggest-title').value = item.title || '';
    document.getElementById('suggest-author').value = item.author || '';
    document.getElementById('suggest-category').value = item.category || '';
    const suggestTagsEl = document.getElementById('suggest-tags');
    if (suggestTagsEl) {
      suggestTagsEl.value = Array.isArray(item.tags) ? item.tags.join(', ') : (item.tags || '');
    }
    document.getElementById('suggest-reason').value = '';

    const dmcaOwnerEl = document.getElementById('dmca-owner');
    if (dmcaOwnerEl) dmcaOwnerEl.value = '';
    const dmcaProofEl = document.getElementById('dmca-proof');
    if (dmcaProofEl) dmcaProofEl.value = '';

    // Reset replacement file upload state
    resetReplaceFileState();

    suggestDrawer.classList.add('open');
    drawerBackdrop.classList.add('open');
  }

  function closeSuggestDrawer() {
    if (!suggestDrawer || !drawerBackdrop) return;
    suggestDrawer.classList.remove('open');
    drawerBackdrop.classList.remove('open');
    resetReplaceFileState();
  }

  // Replacement File Upload Handler
  const replaceDropzone = document.getElementById('replace-dropzone');
  const replaceFileInput = document.getElementById('replace-file-input');
  const replacePrompt = document.getElementById('replace-dropzone-prompt');
  const replacePreview = document.getElementById('replace-dropzone-preview');
  const replacePreviewImg = document.getElementById('replace-preview-img');
  const replacePreviewName = document.getElementById('replace-preview-name');
  const replacePreviewMeta = document.getElementById('replace-preview-meta');
  const btnRemoveReplaceFile = document.getElementById('btn-remove-replace-file');

  let replaceSelectedFile = null;
  let replaceSelectedMeta = '';

  function resetReplaceFileState() {
    replaceSelectedFile = null;
    replaceSelectedMeta = '';
    if (replaceFileInput) replaceFileInput.value = '';
    if (replacePreviewImg) replacePreviewImg.src = '';
    if (replacePrompt) replacePrompt.style.display = 'flex';
    if (replacePreview) replacePreview.style.display = 'none';
    const suggestUrlInput = document.getElementById('suggest-url');
    if (suggestUrlInput) suggestUrlInput.value = '';
  }

  if (replaceDropzone && replaceFileInput) {
    replaceDropzone.addEventListener('click', (e) => {
      if (e.target !== btnRemoveReplaceFile && !e.target.closest('#btn-remove-replace-file')) {
        replaceFileInput.click();
      }
    });

    replaceFileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) handleReplaceFile(file);
    });

    replaceDropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      replaceDropzone.classList.add('dragover');
    });

    replaceDropzone.addEventListener('dragleave', () => {
      replaceDropzone.classList.remove('dragover');
    });

    replaceDropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      replaceDropzone.classList.remove('dragover');
      const file = e.dataTransfer.files[0];
      if (file) handleReplaceFile(file);
    });
  }

  if (btnRemoveReplaceFile) {
    btnRemoveReplaceFile.addEventListener('click', (e) => {
      e.stopPropagation();
      resetReplaceFileState();
    });
  }

  function handleReplaceFile(file) {
    const check = isValidImageFile(file);
    if (!check.valid) {
      alert(check.error);
      return;
    }

    replaceSelectedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      if (replacePreviewImg) replacePreviewImg.src = e.target.result;
      const img = new Image();
      img.onload = () => {
        if (img.width < 200 || img.height < 200) {
          alert(`Image dimensions (${img.width}×${img.height} px) are too small for an e-reader screensaver. Minimum resolution is 200×200 px.`);
          replaceSelectedFile = null;
          return;
        }
        const kb = (file.size / 1024).toFixed(0);
        replaceSelectedMeta = `${img.width} × ${img.height} px · ${kb} KB`;
        if (replacePreviewName) replacePreviewName.textContent = file.name;
        if (replacePreviewMeta) replacePreviewMeta.textContent = replaceSelectedMeta;
        if (replacePrompt) replacePrompt.style.display = 'none';
        if (replacePreview) replacePreview.style.display = 'flex';
      };
      img.onerror = () => {
        alert('Failed to decode replacement image data. The file appears to be corrupted or invalid.');
        replaceSelectedFile = null;
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }

  if (btnCloseSuggest) btnCloseSuggest.addEventListener('click', closeSuggestDrawer);
  if (drawerBackdrop) drawerBackdrop.addEventListener('click', closeSuggestDrawer);
  if (suggestTypeSelect) suggestTypeSelect.addEventListener('change', updateDrawerFormState);

  if (suggestForm) {
    suggestForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const itemId = document.getElementById('suggest-item-id').value;
      const targetTitle = document.getElementById('suggest-target-title').textContent;
      const type = suggestTypeSelect ? suggestTypeSelect.value : 'metadata';
      const isDmca = (type === 'dmca');
      const isReplacement = (type === 'replacement');

      const typeLabels = {
        metadata: 'Metadata Correction',
        replacement: 'Replacement Image',
        dmca: 'DMCA/Copyright Infringement Notice',
        issue: 'Low Quality/Issue Report'
      };

      const issueTitle = encodeURIComponent(isDmca ? `DMCA Takedown Notice: [${itemId}] ${targetTitle}` : `Change Suggestion: [${itemId}] ${targetTitle}`);
      const issueLabel = isDmca ? 'dmca-takedown' : 'suggest-change';

      let replacementImageUrl = '';
      let replaceFileName = '';
      if (isReplacement) {
        const enteredUrl = document.getElementById('suggest-url') ? document.getElementById('suggest-url').value.trim() : '';
        if (replaceSelectedFile) {
          replaceFileName = replaceSelectedFile.name || 'replacement.jpg';
          if (btnSubmitSuggest) {
            btnSubmitSuggest.disabled = true;
            btnSubmitSuggest.textContent = 'Uploading replacement image... ⏳';
          }
          const uploadedUrl = await uploadImageFile(replaceSelectedFile, replaceFileName);
          replacementImageUrl = uploadedUrl || `[Uploaded Image: ${replaceFileName}]`;
          if (btnSubmitSuggest) {
            btnSubmitSuggest.disabled = false;
            btnSubmitSuggest.textContent = 'Submit Suggestion on GitHub →';
          }
        } else if (enteredUrl) {
          replacementImageUrl = enteredUrl;
          replaceFileName = enteredUrl.split('/').pop().split('?')[0] || 'replacement.jpg';
        } else {
          alert('Please upload an image file or enter an image URL for the replacement.');
          return;
        }
      }

      const bodyLines = [
        isDmca ? `### DMCA/Copyright Infringement Notice` : `### Catalog Change Suggestion`,
        ``,
        `**Target Item ID:** \`${itemId}\``,
        `**Target Title:** ${targetTitle}`,
        `**Report/Change Type:** ${typeLabels[type] || type}`,
        ``,
      ];

      if (isDmca) {
        const dmcaOwner = document.getElementById('dmca-owner') ? document.getElementById('dmca-owner').value.trim() : '';
        const dmcaProof = document.getElementById('dmca-proof') ? document.getElementById('dmca-proof').value.trim() : '';
        const reason = document.getElementById('suggest-reason').value;

        bodyLines.push(
          `**Copyright Owner/Authorized Representative:** ${dmcaOwner || 'Not specified'}`,
          `**Proof of Ownership/Original Source:** ${dmcaProof || 'Attached below'}`,
          ``,
          `**Infringement Details:**`,
          reason,
          ``,
          `**Statement of Good Faith:**`,
          `I have a good faith belief that use of the material in the manner complained of is not authorized by the copyright owner, its agent, or the law.`
        );
      } else {
        const newTitle = document.getElementById('suggest-title').value;
        const newAuthor = document.getElementById('suggest-author').value;
        const newCategory = document.getElementById('suggest-category').value;
        const newTags = document.getElementById('suggest-tags') ? document.getElementById('suggest-tags').value.trim() : '';
        const reason = document.getElementById('suggest-reason').value;

        bodyLines.push(
          `**Proposed Title:** ${newTitle}`,
          `**Proposed Author:** ${newAuthor}`,
          `**Proposed Category:** ${newCategory}`,
        );

        if (newTags) {
          bodyLines.push(`**Proposed Tags:** ${newTags}`);
        }

        if (isReplacement && replacementImageUrl) {
          if (replaceFileName) {
            bodyLines.push(`**Replacement Filename:** ${replaceFileName}`);
          }
          bodyLines.push(`**Replacement Image:** ${replacementImageUrl}`);
          if (replacementImageUrl.startsWith('http')) {
            bodyLines.push(``, `### Replacement Preview`, `![Replacement Preview](${replacementImageUrl})`, ``);
          }
          if (replaceSelectedMeta) {
            bodyLines.push(`**Replacement Specs:** ${replaceSelectedMeta}`);
          }
        }

        bodyLines.push(``, `**Reason/Details:**`, reason);
      }

      bodyLines.push(``, `---`, `*Submitted via Storefront Screensaver Catalog Site*`);

      const issueBody = encodeURIComponent(bodyLines.join('\n'));
      const repoUrl = 'https://github.com/ultimatejimmy/storefront-screensavers';
      const githubIssueUrl = `${repoUrl}/issues/new?title=${issueTitle}&labels=${issueLabel}&body=${issueBody}`;

      window.open(githubIssueUrl, '_blank');
      closeSuggestDrawer();
    });
  }
});
