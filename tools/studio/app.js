/**
 * Storefront Catalog Management Studio - Frontend Application
 */

(function () {
  'use strict';

  // State
  let state = {
    catalog: [],
    categories: [],
    backups: [],
    selectedIds: new Set(),
    activeCategory: 'all',
    searchQuery: '',
    statusFilter: 'all',
    sortBy: 'default',
    viewMode: 'grid', // 'grid' | 'table'
    overlayMode: 'grid', // 'grid' | 'book'
    activeItem: null,
    previewMode: 'device', // 'device' | 'grid' | 'book'
    newItemImageData: null,
    replaceImageData: null,
    pendingDeleteId: null
  };

  // DOM Elements
  const el = {
    search: document.getElementById('catalog-search'),
    clearSearchBtn: document.getElementById('clear-search-btn'),
    categoryChips: document.getElementById('category-chips'),
    filterStatus: document.getElementById('filter-status'),
    sortBy: document.getElementById('sort-by'),
    btnModeGrid: document.getElementById('btn-mode-grid'),
    btnModeBook: document.getElementById('btn-mode-book'),
    viewGridBtn: document.getElementById('view-grid-btn'),
    viewTableBtn: document.getElementById('view-table-btn'),
    catalogGrid: document.getElementById('catalog-grid'),
    catalogTableWrapper: document.getElementById('catalog-table-wrapper'),
    catalogTableBody: document.getElementById('catalog-table-body'),
    tableSelectAll: document.getElementById('table-select-all'),
    emptyState: document.getElementById('empty-state'),
    emptyResetBtn: document.getElementById('empty-reset-btn'),

    // Stats
    statTotal: document.getElementById('stat-total'),
    statCategories: document.getElementById('stat-categories'),
    statTransparent: document.getElementById('stat-transparent'),
    countAll: document.getElementById('count-all'),

    // Batch Bar
    batchBar: document.getElementById('batch-bar'),
    batchCount: document.getElementById('batch-count'),
    batchClearBtn: document.getElementById('batch-clear-btn'),
    batchCategorySelect: document.getElementById('batch-category-select'),
    batchApplyCategory: document.getElementById('batch-apply-category'),
    batchDeleteBtn: document.getElementById('batch-delete-btn'),

    // Inspector
    inspector: document.getElementById('inspector-drawer'),
    inspectorCloseBtn: document.getElementById('inspector-close-btn'),
    inspectorEyebrow: document.getElementById('inspector-eyebrow'),
    inspectorTitle: document.getElementById('inspector-title'),
    inspectorPreviewImg: document.getElementById('inspector-preview-img'),
    deviceScreenContainer: document.getElementById('device-screen-container'),
    bookTextSim: document.getElementById('book-text-sim'),
    inspectorFileExtBadge: document.getElementById('inspector-file-ext-badge'),
    previewModeFrame: document.getElementById('preview-mode-frame'),
    previewModeGrid: document.getElementById('preview-mode-grid'),
    previewModeBook: document.getElementById('preview-mode-book'),

    // Image replacement
    replaceDropzone: document.getElementById('replace-dropzone'),
    replaceFileInput: document.getElementById('replace-file-input'),
    replaceUrlInput: document.getElementById('replace-url-input'),
    btnReplaceFromUrl: document.getElementById('btn-replace-from-url'),

    // Inspector Form
    editTitle: document.getElementById('edit-title'),
    editId: document.getElementById('edit-id'),
    editAuthor: document.getElementById('edit-author'),
    editCategoryPills: document.getElementById('edit-category-pills'),
    editCategoryCustomInput: document.getElementById('edit-category-custom-input'),
    btnAddCustomCategoryEdit: document.getElementById('btn-add-custom-category-edit'),
    editLicense: document.getElementById('edit-license'),
    editLicenseCustom: document.getElementById('edit-license-custom'),
    editAuthorUrl: document.getElementById('edit-author-url'),
    editSourceUrl: document.getElementById('edit-source-url'),
    editSourceUrlTest: document.getElementById('edit-source-url-test'),
    editAttribution: document.getElementById('edit-attribution'),
    editLikes: document.getElementById('edit-likes'),
    editDownloads: document.getElementById('edit-downloads'),

    btnSaveEdit: document.getElementById('btn-save-edit'),
    btnCancelEdit: document.getElementById('btn-cancel-edit'),
    btnDeleteItem: document.getElementById('btn-delete-item'),

    // Add Modal
    btnAddItem: document.getElementById('btn-add-item'),
    addModal: document.getElementById('add-modal'),
    addModalCloseBtn: document.getElementById('add-modal-close-btn'),
    addModalCancelBtn: document.getElementById('add-modal-cancel-btn'),
    addModalSubmitBtn: document.getElementById('add-modal-submit-btn'),
    addDropzone: document.getElementById('add-dropzone'),
    addFileInput: document.getElementById('add-file-input'),
    addDropzoneContent: document.getElementById('add-dropzone-content'),
    addPreviewContainer: document.getElementById('add-preview-container'),
    addPreviewImg: document.getElementById('add-preview-img'),
    addRemovePreviewBtn: document.getElementById('add-remove-preview-btn'),
    addImageUrl: document.getElementById('add-image-url'),
    addTitle: document.getElementById('add-title'),
    addCategoryPills: document.getElementById('add-category-pills'),
    addCategoryCustomInput: document.getElementById('add-category-custom-input'),
    btnAddCustomCategoryAdd: document.getElementById('btn-add-custom-category-add'),
    addAuthor: document.getElementById('add-author'),
    addLicense: document.getElementById('add-license'),
    addSourceUrl: document.getElementById('add-source-url'),
    addAttribution: document.getElementById('add-attribution'),

    // Sync & Backups
    btnSyncAll: document.getElementById('btn-sync-all'),
    btnBackups: document.getElementById('btn-backups'),
    backupsModal: document.getElementById('backups-modal'),
    backupsModalCloseBtn: document.getElementById('backups-modal-close-btn'),
    backupsModalCloseBtn2: document.getElementById('backups-modal-close-btn2'),
    backupsList: document.getElementById('backups-list'),

    // Delete confirmation
    deleteConfirmModal: document.getElementById('delete-confirm-modal'),
    deleteConfirmCloseBtn: document.getElementById('delete-confirm-close-btn'),
    deleteConfirmCancelBtn: document.getElementById('delete-confirm-cancel-btn'),
    deleteConfirmActionBtn: document.getElementById('delete-confirm-action-btn'),
    deleteConfirmMessage: document.getElementById('delete-confirm-message'),
    deleteFilesCheckbox: document.getElementById('delete-files-checkbox'),

    toastContainer: document.getElementById('toast-container')
  };

  // Helper to extract clean category list from an item
  function getItemCategories(item) {
    if (!item) return [];
    const cat = item.category;
    if (Array.isArray(cat)) {
      return cat.map(c => String(c).trim()).filter(Boolean);
    }
    if (typeof cat === 'string' && cat.trim()) {
      return cat.split(',').map(c => c.trim()).filter(Boolean);
    }
    return [];
  }

  // Initialize
  async function init() {
    setupEventListeners();
    await loadCatalogData();
  }

  // API Calls
  async function loadCatalogData() {
    try {
      const res = await fetch('/api/catalog');
      if (!res.ok) throw new Error('Failed to load catalog');
      const data = await res.json();
      state.catalog = data.items || [];
      state.categories = data.categories || [];
      state.backups = data.backups || [];
      
      updateHeaderStats();
      renderCategoryChips();
      populateCategoryDropdowns();
      renderCategoryPills(el.addCategoryPills, ['Nature']);
      renderCatalog();
    } catch (err) {
      showToast('Error loading catalog: ' + err.message, 'error');
    }
  }

  // Stats & Category chips
  function updateHeaderStats() {
    el.statTotal.textContent = state.catalog.length;
    el.countAll.textContent = state.catalog.length;
    el.statCategories.textContent = state.categories.length;

    const transparentCount = state.catalog.filter(isTransparentItem).length;
    el.statTransparent.textContent = transparentCount;
  }

  function isTransparentItem(item) {
    const cats = getItemCategories(item).map(c => c.toLowerCase());
    const isCat = cats.includes('transparent');
    const isPng = (item.thumbnailUrl || '').endsWith('.png') || (item.fullUrl || '').endsWith('.png');
    return isCat || isPng;
  }

  function renderCategoryChips() {
    // Count per category
    const catCounts = {};
    for (const item of state.catalog) {
      const cats = getItemCategories(item);
      if (cats.length === 0) {
        catCounts['General'] = (catCounts['General'] || 0) + 1;
      } else {
        for (const cat of cats) {
          catCounts[cat] = (catCounts[cat] || 0) + 1;
        }
      }
    }

    const html = ['<button class="chip ' + (state.activeCategory === 'all' ? 'active' : '') + '" data-category="all">All <span class="chip-count">' + state.catalog.length + '</span></button>'];
    for (const cat of state.categories) {
      const count = catCounts[cat] || 0;
      const isActive = state.activeCategory === cat ? 'active' : '';
      html.push(`<button class="chip ${isActive}" data-category="${escapeHtml(cat)}">${escapeHtml(cat)} <span class="chip-count">${count}</span></button>`);
    }
    el.categoryChips.innerHTML = html.join('');
  }

  function populateCategoryDropdowns() {
    // Batch add category options
    const batchOpts = ['<option value="">Add Category...</option>'];
    for (const cat of state.categories) {
      batchOpts.push(`<option value="${escapeHtml(cat)}">${escapeHtml(cat)}</option>`);
    }
    el.batchCategorySelect.innerHTML = batchOpts.join('');
  }

  // Render multi-select category pills container
  function renderCategoryPills(container, selectedCategories = []) {
    if (!container) return;
    const selectedSet = new Set(selectedCategories.map(c => String(c).trim()));
    
    // Combine state.categories with any custom selected categories
    const allCats = Array.from(new Set([...state.categories, ...selectedSet])).sort();

    const pillsHtml = allCats.map(cat => {
      const isChecked = selectedSet.has(cat);
      return `
        <label class="category-pill">
          <input type="checkbox" value="${escapeHtml(cat)}" ${isChecked ? 'checked' : ''}>
          <span>${escapeHtml(cat)}</span>
        </label>
      `;
    }).join('');

    container.innerHTML = pillsHtml;
  }

  function getSelectedCategoriesFromPills(container) {
    if (!container) return [];
    const checked = [];
    container.querySelectorAll('input[type="checkbox"]:checked').forEach(cb => {
      checked.push(cb.value);
    });
    return checked;
  }

  function addCategoryToPillContainer(container, categoryName) {
    if (!container || !categoryName) return;
    const clean = categoryName.trim();
    if (!clean) return;

    // Check if already in container
    let existingInput = container.querySelector(`input[value="${CSS.escape(clean)}"]`);
    if (existingInput) {
      existingInput.checked = true;
    } else {
      const label = document.createElement('label');
      label.className = 'category-pill';
      label.innerHTML = `
        <input type="checkbox" value="${escapeHtml(clean)}" checked>
        <span>${escapeHtml(clean)}</span>
      `;
      container.appendChild(label);
    }
  }

  // Filter & Sort
  function getFilteredItems() {
    let list = [...state.catalog];

    // Search filter
    if (state.searchQuery.trim()) {
      const q = state.searchQuery.toLowerCase().trim();
      list = list.filter(item => {
        const cats = getItemCategories(item).join(' ').toLowerCase();
        return (item.title && item.title.toLowerCase().includes(q)) ||
               (item.id && item.id.toLowerCase().includes(q)) ||
               (item.author && item.author.toLowerCase().includes(q)) ||
               cats.includes(q) ||
               (item.license && item.license.toLowerCase().includes(q)) ||
               (item.attribution && item.attribution.toLowerCase().includes(q));
      });
    }

    // Category filter (item matches if it includes activeCategory)
    if (state.activeCategory !== 'all') {
      list = list.filter(item => {
        const cats = getItemCategories(item);
        return cats.includes(state.activeCategory);
      });
    }

    // Status filter
    if (state.statusFilter === 'transparent') {
      list = list.filter(isTransparentItem);
    } else if (state.statusFilter === 'missing-source') {
      list = list.filter(item => !item.sourceUrl);
    } else if (state.statusFilter === 'missing-attribution') {
      list = list.filter(item => !item.attribution);
    }

    // Sorting
    if (state.sortBy === 'title-asc') {
      list.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
    } else if (state.sortBy === 'title-desc') {
      list.sort((a, b) => (b.title || '').localeCompare(a.title || ''));
    } else if (state.sortBy === 'author-asc') {
      list.sort((a, b) => (a.author || '').localeCompare(b.author || ''));
    } else if (state.sortBy === 'category') {
      list.sort((a, b) => {
        const ca = getItemCategories(a)[0] || '';
        const cb = getItemCategories(b)[0] || '';
        return ca.localeCompare(cb);
      });
    } else if (state.sortBy === 'likes-desc') {
      list.sort((a, b) => (b.likes || 0) - (a.likes || 0));
    } else if (state.sortBy === 'downloads-desc') {
      list.sort((a, b) => (b.downloads || 0) - (a.downloads || 0));
    }

    return list;
  }

  // Render Catalog
  function renderCatalog() {
    const items = getFilteredItems();

    if (items.length === 0) {
      el.catalogGrid.innerHTML = '';
      el.catalogTableBody.innerHTML = '';
      el.emptyState.classList.remove('hidden');
      return;
    }

    el.emptyState.classList.add('hidden');

    if (state.viewMode === 'grid') {
      renderGrid(items);
    } else {
      renderTable(items);
    }
  }

  function getLocalImageUrl(url) {
    if (!url) return '';
    if (url.includes('githubusercontent.com/ultimatejimmy/storefront-screensavers/main/images/')) {
      const sub = url.split('/images/')[1];
      return `/images/${sub}?t=${Date.now()}`;
    }
    return url;
  }

  function renderGrid(items) {
    const cardsHtml = items.map(item => {
      const isSelected = state.selectedIds.has(item.id);
      const isTransparent = isTransparentItem(item);
      const thumbUrl = getLocalImageUrl(item.thumbnailUrl || item.fullUrl);
      const isPng = (item.thumbnailUrl || '').endsWith('.png') || (item.fullUrl || '').endsWith('.png');
      const formatBadge = isPng ? '<span class="card-badge-format png">PNG</span>' : '<span class="card-badge-format">JPG</span>';

      const categories = getItemCategories(item);
      const catBadges = categories.length > 0
        ? categories.map(c => `<span class="card-category-tag">${escapeHtml(c)}</span>`).join('')
        : '<span class="card-category-tag">General</span>';
      const isBookText = state.overlayMode === 'book';
      const transparentClasses = isTransparent ? (isBookText ? 'is-transparent booktext-mode' : 'is-transparent') : '';

      return `
        <div class="catalog-card ${isSelected ? 'selected' : ''}" data-id="${escapeHtml(item.id)}">
          <div class="card-thumb-wrapper ${transparentClasses}">
            <input type="checkbox" class="card-checkbox" data-id="${escapeHtml(item.id)}" ${isSelected ? 'checked' : ''}>
            ${formatBadge}
            <img class="card-thumb-img" src="${escapeHtml(thumbUrl)}" alt="${escapeHtml(item.title)}" loading="lazy" onerror="this.src='data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'300\\' height=\\'400\\'><rect fill=\\'%23161b22\\' width=\\'300\\' height=\\'400\\'/><text fill=\\'%236e7681\\' x=\\'50%\\' y=\\'50%\\' text-anchor=\\'middle\\' font-family=\\'sans-serif\\'>No Preview</text></svg>'">
          </div>
          <div class="card-details">
            <div class="card-title" title="${escapeHtml(item.title)}">${escapeHtml(item.title)}</div>
            <div class="card-author" title="${escapeHtml(item.author || '')}">by ${escapeHtml(item.author || 'Unknown')}</div>
            <div class="card-categories-row">${catBadges}</div>
            <div class="card-actions">
              <button class="card-btn btn-edit-card" data-id="${escapeHtml(item.id)}" title="Edit metadata & images">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                Edit
              </button>
              <button class="card-btn btn-delete-card text-danger" data-id="${escapeHtml(item.id)}" title="Delete item">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
              </button>
            </div>
          </div>
        </div>
      `;
    }).join('');

    el.catalogGrid.innerHTML = cardsHtml;
  }

  function renderTable(items) {
    const allSelected = items.length > 0 && items.every(item => state.selectedIds.has(item.id));
    el.tableSelectAll.checked = allSelected;

    const rowsHtml = items.map(item => {
      const isSelected = state.selectedIds.has(item.id);
      const thumbUrl = getLocalImageUrl(item.thumbnailUrl || item.fullUrl);
      const categories = getItemCategories(item);
      const catBadges = categories.length > 0
        ? categories.map(c => `<span class="card-category-tag">${escapeHtml(c)}</span>`).join(' ')
        : '<span class="card-category-tag">General</span>';

      return `
        <tr class="${isSelected ? 'selected' : ''}" data-id="${escapeHtml(item.id)}">
          <td><input type="checkbox" class="table-row-checkbox" data-id="${escapeHtml(item.id)}" ${isSelected ? 'checked' : ''}></td>
          <td><img class="table-thumb" src="${escapeHtml(thumbUrl)}" alt="${escapeHtml(item.title)}" loading="lazy"></td>
          <td><strong>${escapeHtml(item.title)}</strong><br><small class="text-tertiary">${escapeHtml(item.id)}</small></td>
          <td><div class="card-categories-row">${catBadges}</div></td>
          <td>${escapeHtml(item.author || 'Unknown')}</td>
          <td><small>${escapeHtml(item.license || 'Community')}</small></td>
          <td>
            <div style="display: flex; gap: 4px;">
              <button class="card-btn btn-edit-card" data-id="${escapeHtml(item.id)}">Edit</button>
              <button class="card-btn btn-delete-card text-danger" data-id="${escapeHtml(item.id)}">✕</button>
            </div>
          </td>
        </tr>
      `;
    }).join('');

    el.catalogTableBody.innerHTML = rowsHtml;
  }

  // Inspector & Editing
  function openInspector(itemId) {
    const item = state.catalog.find(x => x.id === itemId);
    if (!item) return;

    state.activeItem = JSON.parse(JSON.stringify(item));
    state.replaceImageData = null;

    // Set UI fields
    el.inspectorTitle.textContent = item.title;
    el.inspectorEyebrow.textContent = `ID: ${item.id}`;
    
    // Preview image
    const previewUrl = getLocalImageUrl(item.fullUrl || item.thumbnailUrl);
    el.inspectorPreviewImg.src = previewUrl;

    const isPng = (item.thumbnailUrl || '').endsWith('.png') || (item.fullUrl || '').endsWith('.png');
    el.inspectorFileExtBadge.textContent = isPng ? 'PNG (Alpha)' : 'JPG (Solid)';

    // Form inputs
    el.editTitle.value = item.title || '';
    el.editId.value = item.id || '';
    el.editAuthor.value = item.author || '';
    
    // Categories multi-pill selector
    const currentCats = getItemCategories(item);
    renderCategoryPills(el.editCategoryPills, currentCats);
    if (el.editCategoryCustomInput) el.editCategoryCustomInput.value = '';

    // License
    const knownLicenses = ['CC0', 'Public Domain', 'Community Share', 'Unsplash License', 'Pexels License', 'Creative Commons'];
    if (knownLicenses.includes(item.license)) {
      el.editLicense.value = item.license;
      el.editLicenseCustom.classList.add('hidden');
    } else {
      el.editLicense.value = 'custom';
      el.editLicenseCustom.value = item.license || '';
      el.editLicenseCustom.classList.remove('hidden');
    }

    el.editAuthorUrl.value = item.authorUrl || '';
    el.editSourceUrl.value = item.sourceUrl || '';
    if (item.sourceUrl) {
      el.editSourceUrlTest.href = item.sourceUrl;
      el.editSourceUrlTest.classList.remove('hidden');
    } else {
      el.editSourceUrlTest.classList.add('hidden');
    }

    el.editAttribution.value = item.attribution || '';
    el.editLikes.value = item.likes !== undefined ? item.likes : 1;
    el.editDownloads.value = item.downloads !== undefined ? item.downloads : 0;

    // Reset preview mode
    setPreviewMode('device');

    // Open drawer
    el.inspector.classList.add('open');
  }

  function closeInspector() {
    el.inspector.classList.remove('open');
    state.activeItem = null;
    state.replaceImageData = null;
  }

  function setPreviewMode(mode) {
    state.previewMode = mode;
    el.previewModeFrame.classList.toggle('active', mode === 'device');
    el.previewModeGrid.classList.toggle('active', mode === 'grid');
    el.previewModeBook.classList.toggle('active', mode === 'book');

    el.deviceScreenContainer.classList.remove('mode-grid', 'mode-book');
    el.bookTextSim.classList.add('hidden');

    if (mode === 'grid') {
      el.deviceScreenContainer.classList.add('mode-grid');
    } else if (mode === 'book') {
      el.deviceScreenContainer.classList.add('mode-book');
      el.bookTextSim.classList.remove('hidden');
    }
  }

  async function saveItemEdits() {
    if (!state.activeItem) return;

    const originalId = state.activeItem.id;
    const newTitle = el.editTitle.value.trim();
    const newId = el.editId.value.trim();

    if (!newTitle || !newId) {
      showToast('Title and ID cannot be empty', 'error');
      return;
    }

    // Categories
    const chosenCategories = getSelectedCategoriesFromPills(el.editCategoryPills);
    const categoryValue = chosenCategories.length > 1
      ? chosenCategories
      : (chosenCategories[0] || 'General');

    // License
    let license = el.editLicense.value;
    if (license === 'custom') {
      license = el.editLicenseCustom.value.trim() || 'Community Share';
    }

    const updates = {
      id: newId,
      title: newTitle,
      author: el.editAuthor.value.trim(),
      authorUrl: el.editAuthorUrl.value.trim(),
      category: categoryValue,
      license: license,
      sourceUrl: el.editSourceUrl.value.trim(),
      attribution: el.editAttribution.value.trim(),
      likes: parseInt(el.editLikes.value) || 0,
      downloads: parseInt(el.editDownloads.value) || 0
    };

    try {
      el.btnSaveEdit.disabled = true;
      el.btnSaveEdit.textContent = 'Saving...';

      const res = await fetch(`/api/catalog/item/${encodeURIComponent(originalId)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || 'Failed to update item');
      }

      showToast(`Updated "${newTitle}" successfully!`, 'success');
      await loadCatalogData();
      closeInspector();
    } catch (err) {
      showToast('Error saving edits: ' + err.message, 'error');
    } finally {
      el.btnSaveEdit.disabled = false;
      el.btnSaveEdit.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
        <span>Save Changes</span>
      `;
    }
  }

  // Image Replacement
  async function handleImageReplacement(fileOrBase64, isUrl = false) {
    if (!state.activeItem) return;

    try {
      showToast('Processing and uploading replacement image...', 'info');

      let payload = {};
      if (isUrl) {
        payload = { imageUrl: fileOrBase64 };
      } else {
        payload = {
          imageData: fileOrBase64,
          isPng: fileOrBase64.startsWith('data:image/png')
        };
      }

      const res = await fetch(`/api/catalog/item/${encodeURIComponent(state.activeItem.id)}/replace-image`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || 'Failed to replace image');
      }

      showToast('Image replaced and resized successfully!', 'success');
      
      const freshUrl = `/images/${state.activeItem.id}.${data.image.format}?t=${Date.now()}`;
      el.inspectorPreviewImg.src = freshUrl;
      el.inspectorFileExtBadge.textContent = data.image.format === 'png' ? 'PNG (Alpha)' : 'JPG (Solid)';

      await loadCatalogData();
    } catch (err) {
      showToast('Error replacing image: ' + err.message, 'error');
    }
  }

  // Delete Action
  function confirmDeleteItem(itemId) {
    const item = state.catalog.find(x => x.id === itemId);
    if (!item) return;

    state.pendingDeleteId = itemId;
    el.deleteConfirmMessage.textContent = `Are you sure you want to permanently delete "${item.title}" (${item.id})?`;
    el.deleteConfirmModal.classList.remove('hidden');
  }

  async function executeDeleteItem() {
    if (!state.pendingDeleteId) return;

    const itemId = state.pendingDeleteId;
    const deleteFiles = el.deleteFilesCheckbox.checked;

    try {
      el.deleteConfirmActionBtn.disabled = true;
      el.deleteConfirmActionBtn.textContent = 'Deleting...';

      const res = await fetch(`/api/catalog/item/${encodeURIComponent(itemId)}?deleteFiles=${deleteFiles ? '1' : '0'}`, {
        method: 'DELETE'
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || 'Failed to delete item');
      }

      showToast('Screensaver removed from catalog', 'success');
      el.deleteConfirmModal.classList.add('hidden');
      state.pendingDeleteId = null;

      if (state.activeItem && state.activeItem.id === itemId) {
        closeInspector();
      }

      await loadCatalogData();
    } catch (err) {
      showToast('Error deleting: ' + err.message, 'error');
    } finally {
      el.deleteConfirmActionBtn.disabled = false;
      el.deleteConfirmActionBtn.textContent = 'Permanently Delete';
    }
  }

  // Add Item Modal
  function openAddModal() {
    state.newItemImageData = null;
    el.addFileInput.value = '';
    el.addImageUrl.value = '';
    el.addTitle.value = '';
    el.addAuthor.value = '';
    el.addSourceUrl.value = '';
    el.addAttribution.value = '';
    renderCategoryPills(el.addCategoryPills, ['Nature']);
    if (el.addCategoryCustomInput) el.addCategoryCustomInput.value = '';
    el.addPreviewContainer.classList.add('hidden');
    el.addDropzoneContent.classList.remove('hidden');
    el.addModal.classList.remove('hidden');
  }

  function closeAddModal() {
    el.addModal.classList.add('hidden');
    state.newItemImageData = null;
  }

  async function createNewScreensaver() {
    const title = el.addTitle.value.trim();
    if (!title) {
      showToast('Title is required', 'error');
      return;
    }

    const chosenCategories = getSelectedCategoriesFromPills(el.addCategoryPills);
    const categoryValue = chosenCategories.length > 1
      ? chosenCategories
      : (chosenCategories[0] || 'Nature');

    const payload = {
      item: {
        title: title,
        category: categoryValue,
        author: el.addAuthor.value.trim() || 'Community Share',
        license: el.addLicense.value,
        sourceUrl: el.addSourceUrl.value.trim(),
        attribution: el.addAttribution.value.trim() || el.addAuthor.value.trim()
      },
      imageData: state.newItemImageData,
      imageUrl: el.addImageUrl.value.trim(),
      isPng: state.newItemImageData ? state.newItemImageData.startsWith('data:image/png') : false
    };

    try {
      el.addModalSubmitBtn.disabled = true;
      el.addModalSubmitBtn.textContent = 'Creating...';

      const res = await fetch('/api/catalog/item', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || 'Failed to create item');
      }

      showToast(`Created screensaver "${title}"!`, 'success');
      closeAddModal();
      await loadCatalogData();
      
      if (data.item && data.item.id) {
        openInspector(data.item.id);
      }
    } catch (err) {
      showToast('Error creating screensaver: ' + err.message, 'error');
    } finally {
      el.addModalSubmitBtn.disabled = false;
      el.addModalSubmitBtn.innerHTML = `
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
        <span>Create Screensaver</span>
      `;
    }
  }

  // Batch Operations
  function updateBatchBar() {
    const count = state.selectedIds.size;
    if (count > 0) {
      el.batchCount.textContent = `${count} ${count === 1 ? 'item' : 'items'} selected`;
      el.batchBar.classList.remove('hidden');
    } else {
      el.batchBar.classList.add('hidden');
    }
  }

  async function executeBatchAddCategory(category) {
    if (!category || state.selectedIds.size === 0) return;

    try {
      const res = await fetch('/api/catalog/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'add_category',
          categories: [category],
          ids: Array.from(state.selectedIds)
        })
      });

      const data = await res.json();
      if (!res.ok || !data.success) throw new Error(data.error || 'Batch failed');

      showToast(`Added category "${category}" to ${state.selectedIds.size} items`, 'success');
      el.batchCategorySelect.value = '';
      await loadCatalogData();
    } catch (err) {
      showToast('Batch error: ' + err.message, 'error');
    }
  }

  async function executeBatchDelete() {
    const count = state.selectedIds.size;
    if (count === 0) return;

    if (!confirm(`Are you sure you want to delete ${count} selected screensavers from the catalog?`)) {
      return;
    }

    try {
      const res = await fetch('/api/catalog/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'delete',
          deleteFiles: true,
          ids: Array.from(state.selectedIds)
        })
      });

      const data = await res.json();
      if (!res.ok || !data.success) throw new Error(data.error || 'Batch delete failed');

      showToast(`Deleted ${count} screensavers`, 'success');
      state.selectedIds.clear();
      updateBatchBar();
      await loadCatalogData();
    } catch (err) {
      showToast('Batch delete error: ' + err.message, 'error');
    }
  }

  // Comprehensive Sync & Backups
  async function syncEverything() {
    try {
      el.btnSyncAll.disabled = true;
      el.btnSyncAll.innerHTML = `
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
        <span>Syncing...</span>
      `;

      const res = await fetch('/api/catalog/sync-all', { method: 'POST' });
      if (!res.ok) {
        if (res.status === 404) {
          throw new Error('Please restart the local server in your terminal to enable the new Sync Everything endpoint.');
        }
        const text = await res.text();
        throw new Error(`Server returned status ${res.status}: ${text.slice(0, 100)}`);
      }
      const data = await res.json();
      if (!data.success) throw new Error(data.error || 'Sync failed');

      let msg = `Synced ${data.total_items} items: Credits & files verified.`;
      if (data.thumbnails_regenerated > 0) {
        msg += ` (${data.thumbnails_regenerated} thumbnails generated)`;
      }
      if (data.git && data.git.message) {
        msg += `\nGit: ${data.git.message}`;
      }
      showToast(msg, data.git && data.git.pushed ? 'success' : 'info');
      await loadCatalogData();
    } catch (err) {
      showToast('Error syncing catalog: ' + err.message, 'error');
    } finally {
      el.btnSyncAll.disabled = false;
      el.btnSyncAll.innerHTML = `
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
        <span>Sync Everything</span>
      `;
    }
  }

  function openBackupsModal() {
    renderBackupsList();
    el.backupsModal.classList.remove('hidden');
  }

  function renderBackupsList() {
    if (!state.backups || state.backups.length === 0) {
      el.backupsList.innerHTML = '<p class="text-tertiary">No backups found in <code>tools/backups/</code>.</p>';
      return;
    }

    const html = state.backups.map(b => {
      return `
        <div class="backup-item">
          <div>
            <div class="backup-filename">${escapeHtml(b)}</div>
            <div class="backup-time">Snapshot saved before edit</div>
          </div>
          <button class="btn btn-secondary btn-small btn-restore-backup" data-backup="${escapeHtml(b)}">Restore This Version</button>
        </div>
      `;
    }).join('');

    el.backupsList.innerHTML = html;
  }

  async function restoreBackup(backupName) {
    if (!confirm(`Restore catalog from snapshot "${backupName}"? Current state will be backed up before restoration.`)) {
      return;
    }

    try {
      const res = await fetch('/api/catalog/restore-backup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ backup: backupName })
      });

      const data = await res.json();
      if (!res.ok || !data.success) throw new Error(data.error || 'Restore failed');

      showToast(`Restored catalog (${data.count} items) from ${backupName}!`, 'success');
      el.backupsModal.classList.add('hidden');
      await loadCatalogData();
    } catch (err) {
      showToast('Restore error: ' + err.message, 'error');
    }
  }

  // Toast Helper
  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    el.toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 200ms ease-out';
      setTimeout(() => toast.remove(), 200);
    }, 4000);
  }

  // Escape HTML helper
  function escapeHtml(str) {
    if (typeof str !== 'string') return '';
    return str.replace(/[&<>"']/g, function (m) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m];
    });
  }

  // Event Listeners Setup
  function setupEventListeners() {
    // Search
    let searchDebounce;
    el.search.addEventListener('input', (e) => {
      clearTimeout(searchDebounce);
      searchDebounce = setTimeout(() => {
        state.searchQuery = e.target.value;
        el.clearSearchBtn.style.display = state.searchQuery ? 'block' : 'none';
        renderCatalog();
      }, 150);
    });

    el.clearSearchBtn.addEventListener('click', () => {
      el.search.value = '';
      state.searchQuery = '';
      el.clearSearchBtn.style.display = 'none';
      renderCatalog();
    });

    // Category chips
    el.categoryChips.addEventListener('click', (e) => {
      const chip = e.target.closest('.chip');
      if (!chip) return;
      const category = chip.getAttribute('data-category');
      state.activeCategory = category;
      renderCategoryChips();
      renderCatalog();
    });

    // Status & Sort
    el.filterStatus.addEventListener('change', (e) => {
      state.statusFilter = e.target.value;
      renderCatalog();
    });

    el.sortBy.addEventListener('change', (e) => {
      state.sortBy = e.target.value;
      renderCatalog();
    });

    // Transparency preview mode toggles (Grid vs Book Text)
    if (el.btnModeGrid && el.btnModeBook) {
      el.btnModeGrid.addEventListener('click', () => {
        state.overlayMode = 'grid';
        el.btnModeGrid.classList.add('active');
        el.btnModeBook.classList.remove('active');
        renderCatalog();
      });

      el.btnModeBook.addEventListener('click', () => {
        state.overlayMode = 'book';
        el.btnModeBook.classList.add('active');
        el.btnModeGrid.classList.remove('active');
        renderCatalog();
      });
    }

    // View toggles
    el.viewGridBtn.addEventListener('click', () => {
      state.viewMode = 'grid';
      el.viewGridBtn.classList.add('active');
      el.viewTableBtn.classList.remove('active');
      el.catalogGrid.classList.remove('hidden');
      el.catalogTableWrapper.classList.add('hidden');
      renderCatalog();
    });

    el.viewTableBtn.addEventListener('click', () => {
      state.viewMode = 'table';
      el.viewTableBtn.classList.add('active');
      el.viewGridBtn.classList.remove('active');
      el.catalogGrid.classList.add('hidden');
      el.catalogTableWrapper.classList.remove('hidden');
      renderCatalog();
    });

    // Empty state reset
    el.emptyResetBtn.addEventListener('click', () => {
      el.search.value = '';
      state.searchQuery = '';
      state.activeCategory = 'all';
      state.statusFilter = 'all';
      el.filterStatus.value = 'all';
      renderCategoryChips();
      renderCatalog();
    });

    // Grid Card clicks & delegations
    el.catalogGrid.addEventListener('click', (e) => {
      const editBtn = e.target.closest('.btn-edit-card');
      const delBtn = e.target.closest('.btn-delete-card');
      const checkbox = e.target.closest('.card-checkbox');
      const card = e.target.closest('.catalog-card');

      if (checkbox) {
        const id = checkbox.getAttribute('data-id');
        if (checkbox.checked) state.selectedIds.add(id);
        else state.selectedIds.delete(id);
        card.classList.toggle('selected', checkbox.checked);
        updateBatchBar();
        return;
      }

      if (delBtn) {
        e.stopPropagation();
        confirmDeleteItem(delBtn.getAttribute('data-id'));
        return;
      }

      if (card) {
        const id = card.getAttribute('data-id');
        openInspector(id);
      }
    });

    // Table Row clicks
    el.catalogTableBody.addEventListener('click', (e) => {
      const editBtn = e.target.closest('.btn-edit-card');
      const delBtn = e.target.closest('.btn-delete-card');
      const checkbox = e.target.closest('.table-row-checkbox');
      const row = e.target.closest('tr');

      if (checkbox) {
        const id = checkbox.getAttribute('data-id');
        if (checkbox.checked) state.selectedIds.add(id);
        else state.selectedIds.delete(id);
        row.classList.toggle('selected', checkbox.checked);
        updateBatchBar();
        return;
      }

      if (delBtn) {
        confirmDeleteItem(delBtn.getAttribute('data-id'));
        return;
      }

      if (row) {
        const id = row.getAttribute('data-id');
        openInspector(id);
      }
    });

    // Table Select All
    el.tableSelectAll.addEventListener('change', (e) => {
      const checked = e.target.checked;
      const items = getFilteredItems();
      for (const item of items) {
        if (checked) state.selectedIds.add(item.id);
        else state.selectedIds.delete(item.id);
      }
      renderTable(items);
      updateBatchBar();
    });

    // Batch Bar Actions
    el.batchClearBtn.addEventListener('click', () => {
      state.selectedIds.clear();
      updateBatchBar();
      renderCatalog();
    });

    el.batchApplyCategory.addEventListener('click', () => {
      const cat = el.batchCategorySelect.value;
      if (cat) executeBatchAddCategory(cat);
    });

    el.batchDeleteBtn.addEventListener('click', () => {
      executeBatchDelete();
    });

    // Custom category inline adders
    if (el.btnAddCustomCategoryEdit && el.editCategoryCustomInput) {
      el.btnAddCustomCategoryEdit.addEventListener('click', () => {
        const name = el.editCategoryCustomInput.value.trim();
        if (name) {
          addCategoryToPillContainer(el.editCategoryPills, name);
          el.editCategoryCustomInput.value = '';
        }
      });
      el.editCategoryCustomInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          el.btnAddCustomCategoryEdit.click();
        }
      });
    }

    if (el.btnAddCustomCategoryAdd && el.addCategoryCustomInput) {
      el.btnAddCustomCategoryAdd.addEventListener('click', () => {
        const name = el.addCategoryCustomInput.value.trim();
        if (name) {
          addCategoryToPillContainer(el.addCategoryPills, name);
          el.addCategoryCustomInput.value = '';
        }
      });
      el.addCategoryCustomInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          el.btnAddCustomCategoryAdd.click();
        }
      });
    }

    // Inspector
    el.inspectorCloseBtn.addEventListener('click', closeInspector);
    el.btnCancelEdit.addEventListener('click', closeInspector);
    el.btnSaveEdit.addEventListener('click', saveItemEdits);
    el.btnDeleteItem.addEventListener('click', () => {
      if (state.activeItem) confirmDeleteItem(state.activeItem.id);
    });

    el.editLicense.addEventListener('change', (e) => {
      el.editLicenseCustom.classList.toggle('hidden', e.target.value !== 'custom');
    });

    // Preview Mode Toggles
    el.previewModeFrame.addEventListener('click', () => setPreviewMode('device'));
    el.previewModeGrid.addEventListener('click', () => setPreviewMode('grid'));
    el.previewModeBook.addEventListener('click', () => setPreviewMode('book'));

    // Image replacement Dropzone & Input
    el.replaceDropzone.addEventListener('click', () => el.replaceFileInput.click());
    el.replaceDropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      el.replaceDropzone.classList.add('dragover');
    });
    el.replaceDropzone.addEventListener('dragleave', () => el.replaceDropzone.classList.remove('dragover'));
    el.replaceDropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      el.replaceDropzone.classList.remove('dragover');
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        const file = e.dataTransfer.files[0];
        const reader = new FileReader();
        reader.onload = () => handleImageReplacement(reader.result, false);
        reader.readAsDataURL(file);
      }
    });

    el.replaceFileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) {
        const file = e.target.files[0];
        const reader = new FileReader();
        reader.onload = () => handleImageReplacement(reader.result, false);
        reader.readAsDataURL(file);
      }
    });

    el.btnReplaceFromUrl.addEventListener('click', () => {
      const url = el.replaceUrlInput.value.trim();
      if (!url) {
        showToast('Please enter a valid image URL', 'error');
        return;
      }
      handleImageReplacement(url, true);
    });

    // Add Item Modal
    el.btnAddItem.addEventListener('click', openAddModal);
    el.addModalCloseBtn.addEventListener('click', closeAddModal);
    el.addModalCancelBtn.addEventListener('click', closeAddModal);
    el.addModalSubmitBtn.addEventListener('click', createNewScreensaver);

    el.addDropzone.addEventListener('click', (e) => {
      if (e.target !== el.addRemovePreviewBtn) el.addFileInput.click();
    });
    el.addDropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      el.addDropzone.classList.add('dragover');
    });
    el.addDropzone.addEventListener('dragleave', () => el.addDropzone.classList.remove('dragover'));
    el.addDropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      el.addDropzone.classList.remove('dragover');
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        processAddFile(e.dataTransfer.files[0]);
      }
    });

    el.addFileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) {
        processAddFile(e.target.files[0]);
      }
    });

    function processAddFile(file) {
      const reader = new FileReader();
      reader.onload = () => {
        state.newItemImageData = reader.result;
        el.addPreviewImg.src = reader.result;
        el.addDropzoneContent.classList.add('hidden');
        el.addPreviewContainer.classList.remove('hidden');

        // Auto-fill title if empty
        if (!el.addTitle.value) {
          const rawName = file.name.replace(/\.[^/.]+$/, "").replace(/[-_]+/g, ' ');
          el.addTitle.value = rawName.charAt(0).toUpperCase() + rawName.slice(1);
        }
      };
      reader.readAsDataURL(file);
    }

    el.addRemovePreviewBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      state.newItemImageData = null;
      el.addFileInput.value = '';
      el.addPreviewContainer.classList.add('hidden');
      el.addDropzoneContent.classList.remove('hidden');
    });

    // Sync & Backups
    if (el.btnSyncAll) el.btnSyncAll.addEventListener('click', syncEverything);
    el.btnBackups.addEventListener('click', openBackupsModal);
    el.backupsModalCloseBtn.addEventListener('click', () => el.backupsModal.classList.add('hidden'));
    el.backupsModalCloseBtn2.addEventListener('click', () => el.backupsModal.classList.add('hidden'));
    el.backupsList.addEventListener('click', (e) => {
      const btn = e.target.closest('.btn-restore-backup');
      if (btn) restoreBackup(btn.getAttribute('data-backup'));
    });

    // Delete confirmation modal
    el.deleteConfirmCloseBtn.addEventListener('click', () => el.deleteConfirmModal.classList.add('hidden'));
    el.deleteConfirmCancelBtn.addEventListener('click', () => el.deleteConfirmModal.classList.add('hidden'));
    el.deleteConfirmActionBtn.addEventListener('click', executeDeleteItem);

    // Keyboard Shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.key === '/' && document.activeElement !== el.search && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) {
        e.preventDefault();
        el.search.focus();
      }
      if (e.key === 'Escape') {
        if (!el.deleteConfirmModal.classList.contains('hidden')) {
          el.deleteConfirmModal.classList.add('hidden');
        } else if (!el.addModal.classList.contains('hidden')) {
          closeAddModal();
        } else if (!el.backupsModal.classList.contains('hidden')) {
          el.backupsModal.classList.add('hidden');
        } else if (el.inspector.classList.contains('open')) {
          closeInspector();
        }
      }
      if ((e.ctrlKey || e.metaKey) && e.key === 's' && el.inspector.classList.contains('open')) {
        e.preventDefault();
        saveItemEdits();
      }
    });
  }

  // Run on load
  document.addEventListener('DOMContentLoaded', init);
})();
