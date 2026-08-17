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

  // Fetch catalog (cache-busted for instant updates)
  fetch(`screensavers.json?t=${Date.now()}`, { cache: 'no-cache' })
    .then(res => res.json())
    .then(data => {
      catalogData = data;
      applyFilters();
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

  // Helper to check if item matches selected categories
  function itemMatchesCategories(item, activeCats) {
    if (!activeCats || activeCats.length === 0 || activeCats.includes('all')) return true;
    let itemCats = [];
    if (Array.isArray(item.category)) {
      itemCats = item.category.map(c => String(c).toLowerCase());
    } else if (typeof item.category === 'string') {
      itemCats = item.category.split(',').map(c => c.trim().toLowerCase());
    }
    return activeCats.some(ac => itemCats.includes(ac));
  }

  function getActiveFilterCategories() {
    const activeBtns = document.querySelectorAll('.category-tags .tag-btn.active');
    const cats = Array.from(activeBtns).map(b => b.getAttribute('data-category').toLowerCase());
    return cats;
  }

  function applyFilters() {
    const activeCats = getActiveFilterCategories();
    const q = (searchInput ? searchInput.value : '').trim().toLowerCase();

    const filtered = catalogData.filter(item => {
      const matchCat = itemMatchesCategories(item, activeCats);
      const matchSearch = !q || (
        (item.title && item.title.toLowerCase().includes(q)) ||
        (item.author && item.author.toLowerCase().includes(q)) ||
        (item.category && String(item.category).toLowerCase().includes(q))
      );
      return matchCat && matchSearch;
    });

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

      bodyLines.push(
        ``,
        `> ☑️ **Community Agreement:** Submitted freely for community use under open non-commercial terms. Contributor confirms catalog maintainers do not claim ownership and generate zero profit.`
      );

      bodyLines.push(``, `---`, `*Submitted via Storefront Screensaver Catalog Site*`);

      const issueBody = encodeURIComponent(bodyLines.join('\n'));
      const repoUrl = 'https://github.com/ultimatejimmy/storefront-screensavers';
      const githubIssueUrl = `${repoUrl}/issues/new?title=${issueTitle}&body=${issueBody}`;

      window.open(githubIssueUrl, '_blank');
    });
  }
});
