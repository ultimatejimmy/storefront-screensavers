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
    sortBy: 'newest',
    viewMode: 'grid', // 'grid' | 'table'
    overlayMode: 'grid', // 'grid' | 'book'
    activeItem: null,
    previewMode: 'device', // 'device' | 'grid' | 'book'
    newItemImageData: null,
    replaceImageData: null,
    pendingDeleteId: null,
    stagedBulkItems: [],
    bulkSourceMode: 'files',
    isBulkImporting: false,
    totalDownloads: 0,
    lowPerformingCount: 0
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
    thSortDownloads: document.getElementById('th-sort-downloads'),
    thSortDate: document.getElementById('th-sort-date'),
    emptyState: document.getElementById('empty-state'),
    emptyResetBtn: document.getElementById('empty-reset-btn'),

    // Stats
    statTotal: document.getElementById('stat-total'),
    statCategories: document.getElementById('stat-categories'),
    statTransparent: document.getElementById('stat-transparent'),
    statDownloads: document.getElementById('stat-downloads'),
    statLowPerforming: document.getElementById('stat-low-performing'),
    statLowPerformingBtn: document.getElementById('stat-low-performing-btn'),
    countAll: document.getElementById('count-all'),
    countFeatured: document.getElementById('count-featured'),
    btnSyncDownloads: document.getElementById('btn-sync-downloads'),

    // Batch Bar
    batchBar: document.getElementById('batch-bar'),
    batchCount: document.getElementById('batch-count'),
    batchSelectVisibleBtn: document.getElementById('batch-select-visible-btn'),
    visibleCount: document.getElementById('visible-count'),
    batchClearBtn: document.getElementById('batch-clear-btn'),
    batchCategorySelect: document.getElementById('batch-category-select'),
    batchApplyCategory: document.getElementById('batch-apply-category'),
    batchFeatureDurationSelect: document.getElementById('batch-feature-duration-select'),
    batchFeatureBtn: document.getElementById('batch-feature-btn'),
    batchUnfeatureBtn: document.getElementById('batch-unfeature-btn'),
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
    inspectorDateBadge: document.getElementById('inspector-date-badge'),
    inspectorDownloadsBadge: document.getElementById('inspector-downloads-badge'),
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
    editTagsContainer: document.getElementById('edit-tags-container'),
    editTagsChips: document.getElementById('edit-tags-chips'),
    editTagInput: document.getElementById('edit-tag-input'),
    btnAddTagEdit: document.getElementById('btn-add-tag-edit'),
    batchTagInput: document.getElementById('batch-tag-input'),
    batchApplyTag: document.getElementById('batch-apply-tag'),
    editLicense: document.getElementById('edit-license'),
    editLicenseCustom: document.getElementById('edit-license-custom'),
    editAuthorUrl: document.getElementById('edit-author-url'),
    editSourceUrl: document.getElementById('edit-source-url'),
    editSourceUrlTest: document.getElementById('edit-source-url-test'),
    editAttribution: document.getElementById('edit-attribution'),
    editDateAdded: document.getElementById('edit-date-added'),
    editLikes: document.getElementById('edit-likes'),
    editDownloads: document.getElementById('edit-downloads'),
    editFeaturedToggle: document.getElementById('edit-featured-toggle'),
    editFeaturedDetails: document.getElementById('edit-featured-details'),
    editFeaturedUntil: document.getElementById('edit-featured-until'),
    editFeaturedRankBadge: document.getElementById('edit-featured-rank-badge'),
    editOpenReorderBtn: document.getElementById('edit-open-reorder-btn'),
    editFeaturedTopBtn: document.getElementById('edit-featured-top-btn'),
    featureScheduleRankBadge: document.getElementById('feature-schedule-rank-badge'),
    featureScheduleOpenReorderBtn: document.getElementById('feature-schedule-open-reorder-btn'),
    featureSchedulePriorityInput: document.getElementById('feature-schedule-priority-input'),
    featureScheduleTopBtn: document.getElementById('feature-schedule-top-btn'),
    featureSchedulePriorityHint: document.getElementById('feature-schedule-priority-hint'),
    editFeaturedStatusText: document.getElementById('edit-featured-status-text'),

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
    addFeaturedToggle: document.getElementById('add-featured-toggle'),
    addFeaturedDetails: document.getElementById('add-featured-details'),
    addFeaturedUntil: document.getElementById('add-featured-until'),

    // Bulk Add Modal
    btnBulkAdd: document.getElementById('btn-bulk-add'),
    btnSwitchToBulk: document.getElementById('btn-switch-to-bulk'),
    bulkModal: document.getElementById('bulk-add-modal'),
    bulkModalCloseBtn: document.getElementById('bulk-modal-close-btn'),
    bulkModalCancelBtn: document.getElementById('bulk-modal-cancel-btn'),
    bulkModalSubmitBtn: document.getElementById('bulk-modal-submit-btn'),
    bulkSubmitText: document.getElementById('bulk-submit-text'),
    bulkAutoFeatureToggle: document.getElementById('bulk-auto-feature-toggle'),
    bulkAutoFeatureDuration: document.getElementById('bulk-auto-feature-duration'),
    bulkAutoFeatureDate: document.getElementById('bulk-auto-feature-date'),
    tabBulkFiles: document.getElementById('tab-bulk-files'),
    tabBulkFolder: document.getElementById('tab-bulk-folder'),
    bulkFilesSection: document.getElementById('bulk-files-section'),
    bulkFolderSection: document.getElementById('bulk-folder-section'),
    bulkDropzone: document.getElementById('bulk-dropzone'),
    bulkFileInput: document.getElementById('bulk-file-input'),
    bulkFolderInputPath: document.getElementById('bulk-folder-input-path'),
    btnScanFolder: document.getElementById('btn-scan-folder'),
    bulkDefaultAuthor: document.getElementById('bulk-default-author'),
    bulkDefaultLicense: document.getElementById('bulk-default-license'),
    bulkDefaultSource: document.getElementById('bulk-default-source'),
    bulkDefaultTags: document.getElementById('bulk-default-tags'),
    bulkCategoryPills: document.getElementById('bulk-category-pills'),
    bulkStagedContainer: document.getElementById('bulk-staged-container'),
    bulkStagedCount: document.getElementById('bulk-staged-count'),
    bulkStagedList: document.getElementById('bulk-staged-list'),
    btnClearStaged: document.getElementById('btn-clear-staged'),
    bulkProgressContainer: document.getElementById('bulk-progress-container'),
    bulkProgressText: document.getElementById('bulk-progress-text'),
    bulkProgressPercent: document.getElementById('bulk-progress-percent'),
    bulkProgressFill: document.getElementById('bulk-progress-fill'),

    // Feature Schedule Modal
    featureScheduleModal: document.getElementById('feature-schedule-modal'),
    featureScheduleModalTitle: document.getElementById('feature-schedule-modal-title'),
    featureScheduleTitle: document.getElementById('feature-schedule-item-title'),
    featureScheduleCloseBtn: document.getElementById('feature-schedule-close-btn'),
    featureScheduleCancelBtn: document.getElementById('feature-schedule-cancel-btn'),
    featureScheduleSaveBtn: document.getElementById('feature-schedule-save-btn'),
    featureScheduleUnfeatureBtn: document.getElementById('feature-schedule-unfeature-btn'),
    featureScheduleDateInput: document.getElementById('feature-schedule-date-input'),

    // Reorder Featured Modal
    btnOpenReorderModal: document.getElementById('btn-open-reorder-modal'),
    batchPrioritizeBtn: document.getElementById('batch-prioritize-btn'),
    reorderModal: document.getElementById('reorder-featured-modal'),
    reorderModalCloseBtn: document.getElementById('reorder-modal-close-btn'),
    reorderCancelBtn: document.getElementById('reorder-cancel-btn'),
    reorderSaveBtn: document.getElementById('reorder-save-btn'),
    reorderList: document.getElementById('reorder-list'),
    reorderCount: document.getElementById('reorder-count'),
    reorderSearchInput: document.getElementById('reorder-search-input'),
    reorderSortNewestBtn: document.getElementById('reorder-sort-newest-btn'),
    reorderSortDownloadsBtn: document.getElementById('reorder-sort-downloads-btn'),
    reorderStatusIndicator: document.getElementById('reorder-status-indicator'),

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

  // Helper to extract clean tags list from an item
  function getItemTags(item) {
    if (!item || !item.tags) return [];
    if (Array.isArray(item.tags)) {
      return item.tags.map(t => String(t).trim().toLowerCase()).filter(Boolean);
    }
    if (typeof item.tags === 'string' && item.tags.trim()) {
      return item.tags.split(',').map(t => t.trim().toLowerCase()).filter(Boolean);
    }
    return [];
  }

  function renderTagsEditor(tagsList) {
    if (!el.editTagsChips) return;
    el.editTagsChips.innerHTML = '';
    
    tagsList.forEach((tag, idx) => {
      const chip = document.createElement('span');
      chip.className = 'tag-chip-editor';
      chip.innerHTML = `
        <span>#${escapeHtml(tag)}</span>
        <button type="button" class="tag-remove-btn" data-idx="${idx}" title="Remove tag">✕</button>
      `;
      chip.querySelector('.tag-remove-btn').addEventListener('click', () => {
        tagsList.splice(idx, 1);
        renderTagsEditor(tagsList);
      });
      el.editTagsChips.appendChild(chip);
    });
  }

  function addTagToEditor(tagsList, newTagStr) {
    if (!newTagStr) return;
    const parts = newTagStr.split(',').map(t => t.trim().toLowerCase().replace(/^#/, '')).filter(Boolean);
    for (const p of parts) {
      if (!tagsList.includes(p)) {
        tagsList.push(p);
      }
    }
    renderTagsEditor(tagsList);
  }

  // Initialize
  async function init() {
    setupEventListeners();
    await loadCatalogData();
  }

  const DEFAULT_CATEGORIES = [
    'Abstract', 'Anime', 'Architecture', 'Art', 'Fantasy',
    'Minimalist', 'Nature', 'Pop Culture', 'Quotes', 'Religion',
    'Sci-Fi', 'Transparent'
  ];

  const RATINGS_API_URL = 'https://storefront-vote.ultimatejimmy.workers.dev';

  function applyRatingsToCatalog(ratings) {
    if (!ratings || !Array.isArray(state.catalog)) return false;
    let anyUpdated = false;
    for (const item of state.catalog) {
      const r = ratings[item.id] || (item.id && ratings[item.id.toLowerCase()]);
      if (r) {
        if (r.downloads !== undefined) {
          item.downloads = r.downloads;
          anyUpdated = true;
        }
        if (r.up !== undefined || r.down !== undefined) {
          item.likes = Math.max(0, (r.up || 0) - (r.down || 0));
        }
        if (r.wilson !== undefined) item.wilson = r.wilson;
      } else if (item.downloads === undefined) {
        item.downloads = 0;
      }
    }
    state.totalDownloads = state.catalog.reduce((acc, x) => acc + (x.downloads || 0), 0);
    state.lowPerformingCount = state.catalog.filter(x => (x.downloads || 0) <= 5).length;
    return anyUpdated;
  }

  async function fetchLiveRatingsDirect() {
    try {
      const res = await fetch(`${RATINGS_API_URL}/ratings`);
      if (res.ok) {
        const fresh = await res.json();
        if (fresh && typeof fresh === 'object' && Object.keys(fresh).length > 0) {
          if (applyRatingsToCatalog(fresh)) {
            updateHeaderStats();
            renderCatalog();
          }
        }
      }
    } catch (e) {
      console.warn('Direct ratings fetch fallback failed:', e);
    }
  }

  // API Calls
  async function loadCatalogData(forceRefreshDownloads = false) {
    try {
      const url = forceRefreshDownloads ? '/api/catalog?refresh_downloads=1' : '/api/catalog';
      const res = await fetch(url);
      if (!res.ok) throw new Error('Failed to load catalog');
      const data = await res.json();
      state.catalog = (data.items || []).map((item, idx) => ({
        ...item,
        _originalIndex: idx,
        dateAdded: item.dateAdded || '',
        downloads: item.downloads !== undefined ? item.downloads : 0,
        likes: item.likes !== undefined ? item.likes : 0
      }));
      state.categories = Array.from(new Set([...DEFAULT_CATEGORIES, ...(data.categories || [])])).sort();
      state.backups = data.backups || [];
      state.totalDownloads = data.totalDownloads !== undefined
        ? data.totalDownloads
        : state.catalog.reduce((acc, x) => acc + (x.downloads || 0), 0);
      state.lowPerformingCount = data.lowPerformingCount !== undefined
        ? data.lowPerformingCount
        : state.catalog.filter(x => (x.downloads || 0) <= 5).length;
      
      updateHeaderStats();
      renderCategoryChips();
      populateCategoryDropdowns();
      renderCategoryPills(el.addCategoryPills, ['Nature']);
      renderCatalog();

      // Ensure fresh live ratings from Cloudflare worker
      fetchLiveRatingsDirect();
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

    const totalDl = state.totalDownloads || state.catalog.reduce((acc, x) => acc + (x.downloads || 0), 0);
    if (el.statDownloads) el.statDownloads.textContent = totalDl.toLocaleString();

    const lowCount = state.catalog.filter(x => (x.downloads || 0) <= 5).length;
    if (el.statLowPerforming) el.statLowPerforming.textContent = lowCount.toLocaleString();
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

    const featuredCount = state.catalog.filter(x => Boolean(x.featured)).length;
    if (el.countFeatured) el.countFeatured.textContent = featuredCount;
    const isFeaturedActive = state.activeCategory === 'featured' ? 'active' : '';

    const html = [
      '<button class="chip ' + (state.activeCategory === 'all' ? 'active' : '') + '" data-category="all">All <span class="chip-count">' + state.catalog.length + '</span></button>',
      `<button class="chip chip-featured ${isFeaturedActive}" data-category="featured">⭐ Featured <span class="chip-count">${featuredCount}</span></button>`
    ];
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
    
    // Combine DEFAULT_CATEGORIES, state.categories with any custom selected categories
    const allCats = Array.from(new Set([...DEFAULT_CATEGORIES, ...state.categories, ...selectedSet])).sort();

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
        const tags = getItemTags(item);
        return (item.title && item.title.toLowerCase().includes(q)) ||
               (item.id && item.id.toLowerCase().includes(q)) ||
               (item.author && item.author.toLowerCase().includes(q)) ||
               cats.includes(q) ||
               tags.some(t => t.includes(q)) ||
               (item.license && item.license.toLowerCase().includes(q)) ||
               (item.attribution && item.attribution.toLowerCase().includes(q));
      });
    }

    // Category filter (item matches if it includes activeCategory or featured)
    if (state.activeCategory === 'featured') {
      list = list.filter(item => Boolean(item.featured));
    } else if (state.activeCategory !== 'all') {
      list = list.filter(item => {
        const cats = getItemCategories(item);
        return cats.includes(state.activeCategory);
      });
    }

    // Status filter
    if (state.statusFilter === 'transparent') {
      list = list.filter(isTransparentItem);
    } else if (state.statusFilter === 'zero-downloads') {
      list = list.filter(item => (item.downloads || 0) === 0);
    } else if (state.statusFilter === 'low-downloads-5') {
      list = list.filter(item => (item.downloads || 0) <= 5);
    } else if (state.statusFilter === 'low-downloads-10') {
      list = list.filter(item => (item.downloads || 0) <= 10);
    } else if (state.statusFilter === 'low-downloads-25') {
      list = list.filter(item => (item.downloads || 0) <= 25);
    } else if (state.statusFilter === 'missing-source') {
      list = list.filter(item => !item.sourceUrl);
    } else if (state.statusFilter === 'missing-attribution') {
      list = list.filter(item => !item.attribution);
    }

    // Sorting
    if (state.sortBy === 'featured') {
      list.sort((a, b) => {
        const fa = a.featured ? 1 : 0;
        const fb = b.featured ? 1 : 0;
        if (fa !== fb) return fb - fa;
        if (fa && fb) {
          const pa = Number(a.featuredPriority) || 0;
          const pb = Number(b.featuredPriority) || 0;
          if (pa !== pb) return pb - pa;
          const da = String(a.dateAdded || '');
          const db = String(b.dateAdded || '');
          if (da !== db) return db.localeCompare(da);
        }
        return (b.downloads || 0) - (a.downloads || 0);
      });
    } else if (state.sortBy === 'newest') {
      list.sort((a, b) => {
        if (a.dateAdded && b.dateAdded) return new Date(b.dateAdded) - new Date(a.dateAdded);
        return (b._originalIndex || 0) - (a._originalIndex || 0);
      });
    } else if (state.sortBy === 'oldest') {
      list.sort((a, b) => {
        if (a.dateAdded && b.dateAdded) return new Date(a.dateAdded) - new Date(b.dateAdded);
        return (a._originalIndex || 0) - (b._originalIndex || 0);
      });
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
    } else if (state.sortBy === 'downloads-asc') {
      list.sort((a, b) => (a.downloads || 0) - (b.downloads || 0));
    } else if (state.sortBy === 'downloads-desc') {
      list.sort((a, b) => (b.downloads || 0) - (a.downloads || 0));
    }

    return list;
  }

  // Render Catalog
  function renderCatalog() {
    const items = getFilteredItems();

    if (el.visibleCount) {
      el.visibleCount.textContent = items.length;
    }

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

      const dlCount = item.downloads !== undefined ? item.downloads : 0;
      const isLow = dlCount <= 5;
      const dlBadge = `<span class="card-badge-downloads ${isLow ? 'is-low' : ''}" title="${dlCount.toLocaleString()} total downloads">⬇ ${dlCount.toLocaleString()}</span>`;

      const isFeatured = Boolean(item.featured);
      const isFeaturedView = state.activeCategory === 'featured';
      const rank = isFeatured ? getItemFeaturedRank(item.id) : null;
      const featBadge = isFeatured
        ? `<span class="card-badge-featured" title="${item.featuredUntil ? 'Featured until ' + escapeHtml(item.featuredUntil) : 'Featured indefinitely'} · Spotlight Rank #${rank || 1}">⭐ Featured${rank ? ' #' + rank : ''}</span>`
        : '';
      const rankBadge = (isFeaturedView && rank)
        ? `<span class="card-rank-badge ${rank === 1 ? 'rank-1' : (rank === 2 ? 'rank-2' : (rank === 3 ? 'rank-3' : ''))}">#${rank}</span>`
        : '';
      const dragIndicator = isFeaturedView
        ? `<span class="card-drag-indicator" title="Drag to reorder spotlight order">⠿</span>`
        : '';
      const draggableAttr = '';
      const draggableClass = isFeaturedView ? 'is-draggable' : '';

      const categories = getItemCategories(item);
      const catBadges = categories.length > 0
        ? categories.map(c => `<span class="card-category-tag">${escapeHtml(c)}</span>`).join('')
        : '<span class="card-category-tag">General</span>';
      const isBookText = state.overlayMode === 'book';
      const transparentClasses = isTransparent ? (isBookText ? 'is-transparent booktext-mode' : 'is-transparent') : '';

      const tags = getItemTags(item);
      const tagBadges = tags.length > 0
        ? `<div class="card-tags-row">${tags.slice(0, 3).map(t => `<span class="card-tag-badge">#${escapeHtml(t)}</span>`).join('')}${tags.length > 3 ? `<span class="card-tag-badge" title="${escapeHtml(tags.slice(3).join(', '))}">+${tags.length - 3}</span>` : ''}</div>`
        : '';

      const dateAddedStr = item.dateAdded || '-';

      return `
        <div class="catalog-card ${isSelected ? 'selected' : ''} ${isLow ? 'is-low-performing' : ''} ${draggableClass}" ${draggableAttr} data-id="${escapeHtml(item.id)}">
          <div class="card-thumb-wrapper ${transparentClasses}">
            <img class="card-thumb-img" src="${escapeHtml(thumbUrl)}" alt="${escapeHtml(item.title)}" loading="lazy" onerror="this.src='data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'300\\' height=\\'400\\'><rect fill=\\'%23161b22\\' width=\\'300\\' height=\\'400\\'/><text fill=\\'%236e7681\\' x=\\'50%\\' y=\\'50%\\' text-anchor=\\'middle\\' font-family=\\'sans-serif\\'>No Preview</text></svg>'">
            <input type="checkbox" class="card-checkbox" data-id="${escapeHtml(item.id)}" ${isSelected ? 'checked' : ''}>
            ${rankBadge}
            ${dragIndicator}
            ${formatBadge}
            ${dlBadge}
            ${featBadge}
          </div>
          <div class="card-details">
            <div class="card-title" title="${escapeHtml(item.title)}">${escapeHtml(item.title)}</div>
            <div class="card-meta-row">
              <span class="card-author" title="${escapeHtml(item.author || '')}">by ${escapeHtml(item.author || 'Unknown')}</span>
              <span class="card-date" title="Submitted: ${escapeHtml(dateAddedStr)}">📅 ${escapeHtml(dateAddedStr)}</span>
            </div>
            <div class="card-downloads-info">
              <span class="dl-count ${isLow ? 'is-low' : ''}"><strong>${dlCount.toLocaleString()}</strong> downloads</span>
              ${item.likes ? `<span class="dl-likes">• ❤️ ${item.likes}</span>` : ''}
            </div>
            <div class="card-categories-row">${catBadges}</div>
            ${tagBadges}
            <div class="card-actions">
              <button class="card-btn btn-feature-card ${isFeatured ? 'is-featured' : ''}" data-id="${escapeHtml(item.id)}" title="${isFeatured ? '⭐ Featured (Click to reschedule/remove)' : 'Feature this screensaver'}">
                ${isFeatured ? '⭐' : '☆'}
              </button>
              <button class="card-btn btn-edit-card" data-id="${escapeHtml(item.id)}" title="Edit metadata & images">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                Edit
              </button>
              <button class="card-btn btn-delete-card text-danger" data-id="${escapeHtml(item.id)}" title="Prune / Delete item">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
              </button>
            </div>
          </div>
        </div>
      `;
    }).join('');

    el.catalogGrid.innerHTML = cardsHtml;
    syncGridSortableState();
  }

  function renderTable(items) {
    const allSelected = items.length > 0 && items.every(item => state.selectedIds.has(item.id));
    el.tableSelectAll.checked = allSelected;

    const rowsHtml = items.map(item => {
      const isSelected = state.selectedIds.has(item.id);
      const isFeatured = Boolean(item.featured);
      const thumbUrl = getLocalImageUrl(item.thumbnailUrl || item.fullUrl);
      const categories = getItemCategories(item);
      const catBadges = categories.length > 0
        ? categories.map(c => `<span class="card-category-tag">${escapeHtml(c)}</span>`).join(' ')
        : '<span class="card-category-tag">General</span>';

      const tags = getItemTags(item);
      const tagCells = tags.length > 0
        ? `<div class="table-tags-cell">${tags.slice(0, 3).map(t => `<span class="card-tag-badge">#${escapeHtml(t)}</span>`).join(' ')}</div>`
        : '<span class="text-tertiary">-</span>';

      const dlCount = item.downloads !== undefined ? item.downloads : 0;
      const isLow = dlCount <= 5;
      const dateAddedStr = item.dateAdded || '-';

      return `
        <tr class="${isSelected ? 'selected' : ''} ${isLow ? 'row-low-dl' : ''}" data-id="${escapeHtml(item.id)}">
          <td><input type="checkbox" class="table-row-checkbox" data-id="${escapeHtml(item.id)}" ${isSelected ? 'checked' : ''}></td>
          <td><img class="table-thumb" src="${escapeHtml(thumbUrl)}" alt="${escapeHtml(item.title)}" loading="lazy"></td>
          <td>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="table-featured-star ${isFeatured ? 'text-warning' : 'text-tertiary'}" data-id="${escapeHtml(item.id)}" title="${isFeatured ? '⭐ Featured (Click to reschedule/remove)' : 'Click to feature'}">${isFeatured ? '⭐' : '☆'}</span>
              <div>
                <strong>${escapeHtml(item.title)}</strong><br><small class="text-tertiary">${escapeHtml(item.id)}</small>
              </div>
            </div>
          </td>
          <td>
            <span class="table-dl-badge ${isLow ? 'is-low' : ''}" title="${dlCount.toLocaleString()} downloads">
              ⬇ ${dlCount.toLocaleString()}
            </span>
          </td>
          <td>
            <span class="table-date" title="Submitted: ${escapeHtml(dateAddedStr)}">
              ${escapeHtml(dateAddedStr)}
            </span>
          </td>
          <td><div class="card-categories-row">${catBadges}</div></td>
          <td>${tagCells}</td>
          <td>${escapeHtml(item.author || 'Unknown')}</td>
          <td><small>${escapeHtml(item.license || 'Community')}</small></td>
          <td>
            <div style="display: flex; gap: 4px;">
              <button class="card-btn btn-edit-card" data-id="${escapeHtml(item.id)}">Edit</button>
              <button class="card-btn btn-delete-card text-danger" data-id="${escapeHtml(item.id)}" title="Prune / Delete">✕</button>
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

    // Tags editor
    state.activeItemTags = getItemTags(item);
    renderTagsEditor(state.activeItemTags);
    if (el.editTagInput) el.editTagInput.value = '';

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
    if (el.editDateAdded) el.editDateAdded.value = item.dateAdded || '';
    el.editLikes.value = item.likes !== undefined ? item.likes : 1;
    el.editDownloads.value = item.downloads !== undefined ? item.downloads : 0;

    if (el.editFeaturedToggle) {
      el.editFeaturedToggle.checked = Boolean(item.featured);
      if (el.editFeaturedDetails) {
        el.editFeaturedDetails.classList.toggle('hidden', !item.featured);
      }
      if (el.editFeaturedUntil) {
        el.editFeaturedUntil.value = item.featuredUntil || '';
      }
      const rank = getItemFeaturedRank(item.id);
      const totalFeat = getFeaturedItemsSorted().length;
      if (el.editFeaturedRankBadge) {
        if (item.featured && rank) {
          el.editFeaturedRankBadge.textContent = `Spotlight Rank: #${rank} of ${totalFeat}`;
          el.editFeaturedRankBadge.className = `reorder-rank ${rank === 1 ? 'rank-1' : (rank === 2 ? 'rank-2' : (rank === 3 ? 'rank-3' : ''))}`;
          el.editFeaturedRankBadge.style.width = 'auto';
          el.editFeaturedRankBadge.style.padding = '2px 8px';
          el.editFeaturedRankBadge.classList.remove('hidden');
        } else {
          el.editFeaturedRankBadge.classList.add('hidden');
        }
      }
      if (el.editFeaturedStatusText) {
        el.editFeaturedStatusText.textContent = item.featured
          ? (item.featuredUntil ? `Featured until ${item.featuredUntil}` : 'Featured indefinitely')
          : 'Spots at top of catalog';
      }
    }

    if (el.inspectorDateBadge) {
      el.inspectorDateBadge.textContent = item.dateAdded ? `📅 ${item.dateAdded}` : '📅 No date';
      el.inspectorDateBadge.title = item.dateAdded ? `Submitted on ${item.dateAdded}` : 'No date recorded';
    }

    const inspectorDl = item.downloads !== undefined ? item.downloads : 0;
    if (el.inspectorDownloadsBadge) {
      el.inspectorDownloadsBadge.textContent = `⬇ ${inspectorDl.toLocaleString()} dl`;
      el.inspectorDownloadsBadge.title = `${inspectorDl.toLocaleString()} total downloads`;
      if (inspectorDl <= 5) {
        el.inspectorDownloadsBadge.style.background = 'rgba(245, 158, 11, 0.2)';
        el.inspectorDownloadsBadge.style.color = '#f59e0b';
        el.inspectorDownloadsBadge.style.borderColor = 'rgba(245, 158, 11, 0.4)';
      } else {
        el.inspectorDownloadsBadge.style.background = 'rgba(56, 189, 248, 0.2)';
        el.inspectorDownloadsBadge.style.color = '#38bdf8';
        el.inspectorDownloadsBadge.style.borderColor = 'rgba(56, 189, 248, 0.35)';
      }
    }

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
      tags: state.activeItemTags || [],
      license: license,
      sourceUrl: el.editSourceUrl.value.trim(),
      attribution: el.editAttribution.value.trim(),
      likes: parseInt(el.editLikes.value) || 0,
      downloads: parseInt(el.editDownloads.value) || 0,
      dateAdded: el.editDateAdded ? el.editDateAdded.value.trim() : (state.activeItem.dateAdded || '')
    };

    if (el.editFeaturedToggle) {
      updates.featured = el.editFeaturedToggle.checked;
      if (el.editFeaturedToggle.checked) {
        updates.featuredPriority = (state.activeItem && state.activeItem.featuredPriority !== undefined)
          ? state.activeItem.featuredPriority
          : getTopFeaturedPriority() + 10;
      }
      if (el.editFeaturedToggle.checked && el.editFeaturedUntil && el.editFeaturedUntil.value) {
        updates.featuredUntil = el.editFeaturedUntil.value.trim();
      } else {
        updates.featuredUntil = null;
      }
    }

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
    if (el.addFeaturedToggle) {
      el.addFeaturedToggle.checked = false;
      if (el.addFeaturedDetails) el.addFeaturedDetails.classList.add('hidden');
      if (el.addFeaturedUntil) el.addFeaturedUntil.value = getDatePreset(14);
    }
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

    if (el.addFeaturedToggle && el.addFeaturedToggle.checked) {
      payload.item.featured = true;
      if (el.addFeaturedUntil && el.addFeaturedUntil.value) {
        payload.item.featuredUntil = el.addFeaturedUntil.value.trim();
      }
    }

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

  // ==========================================
  // Bulk Add Modal & Operations
  // ==========================================
  function cleanFilenameToTitle(filename) {
    if (!filename) return 'Screensaver';
    const base = filename.replace(/\.[^/.]+$/, '');
    const clean = base.replace(/[-_.]+/g, ' ').trim();
    return clean.split(/\s+/).map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ') || base;
  }

  function formatFileSize(bytes) {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return (bytes / Math.pow(k, i)).toFixed(1) + ' ' + sizes[i];
  }

  function readFileAsBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  function openBulkModal() {
    state.stagedBulkItems = [];
    state.bulkSourceMode = 'files';
    state.isBulkImporting = false;

    if (el.bulkFileInput) el.bulkFileInput.value = '';
    if (el.bulkFolderInputPath) el.bulkFolderInputPath.value = '';
    if (el.bulkDefaultAuthor) el.bulkDefaultAuthor.value = 'Community Share';
    if (el.bulkDefaultLicense) el.bulkDefaultLicense.value = 'Community Share';
    if (el.bulkDefaultSource) el.bulkDefaultSource.value = '';
    if (el.bulkDefaultTags) el.bulkDefaultTags.value = '';
    if (el.bulkAutoFeatureToggle) el.bulkAutoFeatureToggle.checked = false;
    if (el.bulkAutoFeatureDuration) el.bulkAutoFeatureDuration.value = '14';
    if (el.bulkAutoFeatureDate) {
      el.bulkAutoFeatureDate.value = '';
      el.bulkAutoFeatureDate.classList.add('hidden');
    }
    updateBulkAutoFeatureState();

    renderCategoryPills(el.bulkCategoryPills, ['Nature']);
    renderBulkStagedList();
    setBulkSourceTab('files');

    if (el.bulkProgressContainer) el.bulkProgressContainer.classList.add('hidden');
    if (el.bulkModalSubmitBtn) {
      el.bulkModalSubmitBtn.disabled = true;
      el.bulkSubmitText.textContent = 'Import Wallpapers';
    }

    el.bulkModal.classList.remove('hidden');
  }

  function updateBulkAutoFeatureState() {
    const isChecked = Boolean(el.bulkAutoFeatureToggle && el.bulkAutoFeatureToggle.checked);
    if (el.bulkAutoFeatureDuration) {
      el.bulkAutoFeatureDuration.disabled = !isChecked;
      el.bulkAutoFeatureDuration.style.opacity = isChecked ? '1' : '0.5';
    }
    if (el.bulkAutoFeatureDate) {
      el.bulkAutoFeatureDate.disabled = !isChecked;
      el.bulkAutoFeatureDate.style.opacity = isChecked ? '1' : '0.5';
    }
  }

  function closeBulkModal() {
    if (state.isBulkImporting) {
      if (!confirm('An import is currently in progress. Are you sure you want to cancel?')) {
        return;
      }
    }
    el.bulkModal.classList.add('hidden');
    // Clean up created object URLs
    state.stagedBulkItems.forEach(item => {
      if (item.previewUrl && item.previewUrl.startsWith('blob:')) {
        URL.revokeObjectURL(item.previewUrl);
      }
    });
    state.stagedBulkItems = [];
    state.isBulkImporting = false;
  }

  function setBulkSourceTab(mode) {
    state.bulkSourceMode = mode;
    if (mode === 'files') {
      el.tabBulkFiles.classList.add('active');
      el.tabBulkFolder.classList.remove('active');
      el.bulkFilesSection.classList.remove('hidden');
      el.bulkFolderSection.classList.add('hidden');
    } else {
      el.tabBulkFiles.classList.remove('active');
      el.tabBulkFolder.classList.add('active');
      el.bulkFilesSection.classList.add('hidden');
      el.bulkFolderSection.classList.remove('hidden');
    }
  }

  function addFilesToBulkStaged(files) {
    if (!files || files.length === 0) return;
    const validExtensions = ['png', 'jpg', 'jpeg', 'webp', 'bmp'];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const ext = file.name.split('.').pop().toLowerCase();
      if (!validExtensions.includes(ext) && !file.type.startsWith('image/')) {
        continue;
      }

      const id = 'staged-' + Date.now() + '-' + Math.random().toString(36).substring(2, 7);
      const title = cleanFilenameToTitle(file.name);
      const previewUrl = URL.createObjectURL(file);

      state.stagedBulkItems.push({
        id: id,
        file: file,
        localFilePath: null,
        previewUrl: previewUrl,
        filename: file.name,
        title: title,
        size: file.size,
        ext: ext
      });
    }

    renderBulkStagedList();
  }

  async function scanLocalFolder() {
    const folder = el.bulkFolderInputPath.value.trim();
    if (!folder) {
      showToast('Please enter a folder path to scan', 'error');
      return;
    }

    try {
      el.btnScanFolder.disabled = true;
      el.btnScanFolder.textContent = 'Scanning...';

      const res = await fetch('/api/catalog/scan-folder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folder: folder })
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || 'Failed scanning directory');
      }

      if (data.files.length === 0) {
        showToast('No supported images (PNG, JPG, WebP, BMP) found in folder', 'info');
        return;
      }

      for (const f of data.files) {
        const id = 'staged-' + Date.now() + '-' + Math.random().toString(36).substring(2, 7);
        const previewUrl = `/api/catalog/preview-local-image?path=${encodeURIComponent(f.path)}`;

        state.stagedBulkItems.push({
          id: id,
          file: null,
          localFilePath: f.path,
          previewUrl: previewUrl,
          filename: f.filename,
          title: f.title,
          size: f.size,
          ext: f.ext
        });
      }

      renderBulkStagedList();
      showToast(`Added ${data.files.length} images from folder!`, 'success');
    } catch (err) {
      showToast('Error scanning folder: ' + err.message, 'error');
    } finally {
      el.btnScanFolder.disabled = false;
      el.btnScanFolder.textContent = 'Scan Directory';
    }
  }

  function renderBulkStagedList() {
    const count = state.stagedBulkItems.length;
    el.bulkStagedCount.textContent = count;

    if (count === 0) {
      el.bulkStagedContainer.classList.add('hidden');
      el.bulkModalSubmitBtn.disabled = true;
      el.bulkSubmitText.textContent = 'Import Wallpapers';
      el.bulkStagedList.innerHTML = '';
      return;
    }

    el.bulkStagedContainer.classList.remove('hidden');
    el.bulkModalSubmitBtn.disabled = false;
    el.bulkSubmitText.textContent = `Import ${count} ${count === 1 ? 'Wallpaper' : 'Wallpapers'}`;

    el.bulkStagedList.innerHTML = '';

    state.stagedBulkItems.forEach((item) => {
      const itemEl = document.createElement('div');
      itemEl.className = 'bulk-staged-item';
      itemEl.innerHTML = `
        <div class="staged-thumb-wrapper">
          <img class="staged-thumb" src="${escapeHtml(item.previewUrl)}" alt="Preview" onerror="this.src='';">
        </div>
        <div class="staged-info-wrapper">
          <input type="text" class="text-input staged-title-input" value="${escapeHtml(item.title)}" placeholder="Wallpaper title..." data-id="${item.id}">
          <div class="staged-meta-row">
            <span>${escapeHtml(item.filename)}</span>
            <span>•</span>
            <span>${formatFileSize(item.size)}</span>
            <span class="format-badge">${escapeHtml(item.ext.toUpperCase())}</span>
          </div>
        </div>
        <button type="button" class="btn-remove-staged" title="Remove from batch" data-id="${item.id}">✕</button>
      `;

      // Title change listener
      const titleInput = itemEl.querySelector('.staged-title-input');
      titleInput.addEventListener('input', (e) => {
        item.title = e.target.value;
      });

      // Remove button listener
      const removeBtn = itemEl.querySelector('.btn-remove-staged');
      removeBtn.addEventListener('click', () => {
        if (item.previewUrl && item.previewUrl.startsWith('blob:')) {
          URL.revokeObjectURL(item.previewUrl);
        }
        state.stagedBulkItems = state.stagedBulkItems.filter(x => x.id !== item.id);
        renderBulkStagedList();
      });

      el.bulkStagedList.appendChild(itemEl);
    });
  }

  async function executeBulkImport() {
    if (state.stagedBulkItems.length === 0) {
      showToast('No images queued for import', 'error');
      return;
    }

    const defaultAuthor = el.bulkDefaultAuthor.value.trim() || 'Community Share';
    const defaultLicense = el.bulkDefaultLicense.value;
    const defaultSource = el.bulkDefaultSource.value.trim();
    const defaultTagsRaw = el.bulkDefaultTags.value.trim();
    const defaultTags = defaultTagsRaw ? defaultTagsRaw.split(',').map(t => t.trim().toLowerCase()).filter(Boolean) : [];

    const chosenCategories = getSelectedCategoriesFromPills(el.bulkCategoryPills);
    const categoryValue = chosenCategories.length > 1
      ? chosenCategories
      : (chosenCategories[0] || 'Nature');

    state.isBulkImporting = true;
    el.bulkModalSubmitBtn.disabled = true;
    el.bulkModalCancelBtn.disabled = true;
    el.btnClearStaged.disabled = true;
    el.bulkProgressContainer.classList.remove('hidden');

    const total = state.stagedBulkItems.length;
    let processed = 0;
    let successCount = 0;
    let failedCount = 0;
    const errors = [];

    // Process in chunks of 4 to keep payloads responsive and show smooth progress
    const CHUNK_SIZE = 4;
    const itemsToProcess = [...state.stagedBulkItems];

    for (let i = 0; i < itemsToProcess.length; i += CHUNK_SIZE) {
      const chunk = itemsToProcess.slice(i, i + CHUNK_SIZE);
      const payloadItems = [];

      for (const item of chunk) {
        let imageData = null;
        let isPng = item.ext.toLowerCase() === 'png';

        if (item.file) {
          try {
            imageData = await readFileAsBase64(item.file);
            isPng = item.file.type === 'image/png' || isPng;
          } catch (e) {
            failedCount++;
            errors.push(`${item.filename}: could not read file`);
            continue;
          }
        }

        const autoFeature = Boolean(el.bulkAutoFeatureToggle && el.bulkAutoFeatureToggle.checked);
        let autoFeatureUntil = null;
        if (autoFeature) {
          const durationVal = el.bulkAutoFeatureDuration ? el.bulkAutoFeatureDuration.value : '14';
          if (durationVal === 'custom' && el.bulkAutoFeatureDate && el.bulkAutoFeatureDate.value) {
            autoFeatureUntil = el.bulkAutoFeatureDate.value.trim();
          } else if (durationVal !== '0') {
            autoFeatureUntil = getDatePreset(durationVal) || null;
          }
        }

        const entry = {
          title: item.title.trim() || cleanFilenameToTitle(item.filename),
          filename: item.filename,
          category: categoryValue,
          author: defaultAuthor,
          license: defaultLicense,
          sourceUrl: defaultSource,
          attribution: defaultAuthor,
          tags: defaultTags,
          imageData: imageData,
          localFilePath: item.localFilePath,
          isPng: isPng
        };
        if (autoFeature) {
          entry.featured = true;
          entry.featuredUntil = autoFeatureUntil;
        }
        payloadItems.push(entry);
      }

      if (payloadItems.length === 0) continue;

      try {
        const res = await fetch('/api/catalog/bulk-add', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ items: payloadItems })
        });

        const data = await res.json();
        if (!res.ok || !data.success) {
          throw new Error(data.error || 'Server error during batch');
        }

        successCount += (data.addedCount || 0);
        failedCount += (data.failedCount || 0);
        if (data.errors && data.errors.length) {
          data.errors.forEach(e => errors.push(e.error || e.title));
        }
      } catch (err) {
        failedCount += payloadItems.length;
        errors.push(err.message);
      }

      processed += chunk.length;
      const pct = Math.min(100, Math.round((processed / total) * 100));
      el.bulkProgressFill.style.width = pct + '%';
      el.bulkProgressPercent.textContent = pct + '%';
      el.bulkProgressText.textContent = `Imported ${Math.min(processed, total)} of ${total} wallpapers...`;
    }

    state.isBulkImporting = false;
    el.bulkModalSubmitBtn.disabled = false;
    el.bulkModalCancelBtn.disabled = false;
    el.btnClearStaged.disabled = false;

    if (successCount > 0) {
      showToast(`Successfully bulk added ${successCount} screensavers!`, 'success');
      closeBulkModal();
      await loadCatalogData();
    } else {
      showToast(`Bulk add failed: ${errors.join(', ')}`, 'error');
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
      if (el.batchFeatureDurationSelect) el.batchFeatureDurationSelect.value = '14';
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

    const isPruning = state.statusFilter.startsWith('low-downloads') || state.statusFilter === 'zero-downloads';
    const confirmMsg = isPruning
      ? `Prune Confirmation:\n\nAre you sure you want to permanently prune and delete ${count} low-performing screensaver(s)?\n\nAll associated image files (master 1860×2480, 600×800 thumbnail, plugin thumbnail) and catalog entries will be removed.`
      : `Are you sure you want to delete ${count} selected screensaver(s) and their image files from the catalog?`;

    if (!confirm(confirmMsg)) {
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

      showToast(`Successfully pruned and deleted ${count} screensavers`, 'success');
      state.selectedIds.clear();
      updateBatchBar();
      await loadCatalogData();
    } catch (err) {
      showToast('Batch delete error: ' + err.message, 'error');
    }
  }

  async function executeBatchFeature(isFeatured = true) {
    const count = state.selectedIds.size;
    if (count === 0) return;

    if (!isFeatured) {
      try {
        const res = await fetch('/api/catalog/batch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action: 'unfeature',
            ids: Array.from(state.selectedIds)
          })
        });
        const data = await res.json();
        if (!res.ok || !data.success) throw new Error(data.error || 'Batch operation failed');

        showToast(`Removed featured status from ${count} screensavers`, 'info');
        state.selectedIds.clear();
        updateBatchBar();
        await loadCatalogData();
      } catch (err) {
        showToast('Batch feature error: ' + err.message, 'error');
      }
      return;
    }

    const durationVal = el.batchFeatureDurationSelect ? el.batchFeatureDurationSelect.value : '14';
    if (durationVal === 'custom') {
      openFeatureScheduleModal(null, true);
      return;
    }

    const until = durationVal === '0' ? null : getDatePreset(durationVal);
    try {
      const res = await fetch('/api/catalog/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'feature',
          ids: Array.from(state.selectedIds),
          featuredUntil: until
        })
      });
      const data = await res.json();
      if (!res.ok || !data.success) throw new Error(data.error || 'Batch operation failed');

      let label = 'for 14 days';
      if (durationVal === '7') label = 'for 7 days';
      else if (durationVal === '30') label = 'for 30 days';
      else if (durationVal === 'month') label = `until ${until}`;
      else if (durationVal === '0') label = 'indefinitely';

      showToast(`⭐ Featured ${count} screensavers ${label}`, 'success');
      state.selectedIds.clear();
      updateBatchBar();
      await loadCatalogData();
    } catch (err) {
      showToast('Batch feature error: ' + err.message, 'error');
    }
  }

  // Feature Scheduling Modal & Date Helpers
  function formatDateLocal(d) {
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  function getDatePreset(days) {
    const d = new Date();
    if (days === 'month') {
      const endOfMonth = new Date(d.getFullYear(), d.getMonth() + 1, 0);
      return formatDateLocal(endOfMonth);
    }
    const numDays = parseInt(days, 10);
    if (!numDays || numDays <= 0) return '';
    const target = new Date(d.getFullYear(), d.getMonth(), d.getDate() + numDays);
    return formatDateLocal(target);
  }

  let activeFeatureItemId = null;
  let isBatchFeatureMode = false;

  function getFeaturedItemsSorted() {
    const featured = state.catalog.filter(x => Boolean(x.featured));
    featured.sort((a, b) => {
      const pa = Number(a.featuredPriority) || 0;
      const pb = Number(b.featuredPriority) || 0;
      if (pa !== pb) return pb - pa;
      const da = String(a.dateAdded || '');
      const db = String(b.dateAdded || '');
      if (da !== db) return db.localeCompare(da);
      return (a._originalIndex || 0) - (b._originalIndex || 0);
    });
    return featured;
  }

  function getItemFeaturedRank(itemId) {
    const sorted = getFeaturedItemsSorted();
    const idx = sorted.findIndex(x => x.id === itemId);
    return idx >= 0 ? idx + 1 : null;
  }

  function getTopFeaturedPriority() {
    return state.catalog.reduce((max, x) => (
      x.featured ? Math.max(max, Number(x.featuredPriority) || 0) : max
    ), 0);
  }

  let currentReorderItems = [];
  let unfeaturedInModal = new Set();

  function openReorderFeaturedModal() {
    currentReorderItems = getFeaturedItemsSorted().slice();
    unfeaturedInModal.clear();
    if (el.reorderSearchInput) el.reorderSearchInput.value = '';
    renderReorderList();
    if (el.reorderStatusIndicator) {
      el.reorderStatusIndicator.textContent = 'Drag rows using ⠿ to swap spotlight positions';
      el.reorderStatusIndicator.style.color = 'var(--text-secondary)';
    }
    if (el.reorderModal) el.reorderModal.classList.remove('hidden');
  }

  function closeReorderFeaturedModal() {
    if (el.reorderModal) el.reorderModal.classList.add('hidden');
    currentReorderItems = [];
    unfeaturedInModal.clear();
  }

  function renderReorderList() {
    if (!el.reorderList) return;
    const filterQuery = (el.reorderSearchInput ? el.reorderSearchInput.value : '').toLowerCase().trim();

    if (el.reorderCount) {
      el.reorderCount.textContent = currentReorderItems.length;
    }

    if (currentReorderItems.length === 0) {
      el.reorderList.innerHTML = `
        <div style="text-align: center; padding: 40px 20px; color: var(--text-secondary);">
          <div style="font-size: 2rem; margin-bottom: 8px;">⭐</div>
          <h4>No featured screensavers</h4>
          <p style="font-size: 0.85rem; opacity: 0.8;">Feature some wallpapers first to reorder them here.</p>
        </div>
      `;
      return;
    }

    const rowsHtml = currentReorderItems.map((item, idx) => {
      const isVisible = !filterQuery ||
        (item.title && item.title.toLowerCase().includes(filterQuery)) ||
        (item.author && item.author.toLowerCase().includes(filterQuery)) ||
        (item.id && item.id.toLowerCase().includes(filterQuery));

      const rankClass = idx === 0 ? 'rank-1' : (idx === 1 ? 'rank-2' : (idx === 2 ? 'rank-3' : ''));
      const thumbUrl = getLocalImageUrl(item.thumbnailUrl || item.fullUrl);
      const expiry = item.featuredUntil ? `📅 Until ${escapeHtml(item.featuredUntil)}` : '⭐ Indefinite';
      const dlCount = (item.downloads || 0).toLocaleString();

      return `
        <div class="reorder-item ${isVisible ? '' : 'hidden'}" draggable="true" data-id="${escapeHtml(item.id)}" data-index="${idx}">
          <div class="reorder-handle" title="Drag to reorder">⠿</div>
          <div class="reorder-rank ${rankClass}">#${idx + 1}</div>
          <div class="reorder-thumb-wrap ${isTransparentItem(item) ? (state.overlayMode === 'book' ? 'is-transparent booktext-mode' : 'is-transparent') : ''}">
            <img class="reorder-thumb" src="${escapeHtml(thumbUrl)}" alt="${escapeHtml(item.title)}" loading="lazy">
          </div>
          <div class="reorder-info">
            <div class="reorder-title" title="${escapeHtml(item.title)}">${escapeHtml(item.title)}</div>
            <div class="reorder-meta">
              <span>by ${escapeHtml(item.author || 'Unknown')}</span>
              <span>•</span>
              <span class="reorder-duration-badge">${expiry}</span>
              <span>•</span>
              <span>⬇ ${dlCount} dl</span>
            </div>
          </div>
          <div class="reorder-controls">
            <button type="button" class="btn btn-secondary reorder-btn btn-reorder-top" data-id="${escapeHtml(item.id)}" title="Move to Top (#1)">⬆ Top</button>
            <button type="button" class="btn btn-secondary reorder-btn btn-reorder-up" data-id="${escapeHtml(item.id)}" title="Move Up (▲)" ${idx === 0 ? 'disabled' : ''}>▲</button>
            <button type="button" class="btn btn-secondary reorder-btn btn-reorder-down" data-id="${escapeHtml(item.id)}" title="Move Down (▼)" ${idx === currentReorderItems.length - 1 ? 'disabled' : ''}>▼</button>
            <button type="button" class="btn btn-secondary reorder-btn btn-reorder-bottom" data-id="${escapeHtml(item.id)}" title="Move to Bottom (⬇)">⬇</button>
            <button type="button" class="btn btn-danger reorder-btn btn-reorder-remove" data-id="${escapeHtml(item.id)}" title="Remove from Featured">☆</button>
          </div>
        </div>
      `;
    }).join('');

    el.reorderList.innerHTML = rowsHtml;
    initReorderSortable();
  }

  // Re-slot a reordered subset of items back into the full ordered list.
  // Items not in `visibleIds` (e.g. hidden by a search filter) keep their slots.
  function mergeVisibleOrder(fullItems, visibleIds) {
    const visibleSet = new Set(visibleIds);
    const byId = new Map(fullItems.map(x => [x.id, x]));
    const queue = visibleIds.filter(id => byId.has(id));
    return fullItems.map(item => visibleSet.has(item.id) ? byId.get(queue.shift()) : item);
  }

  let reorderSortable = null;
  function initReorderSortable() {
    if (reorderSortable || typeof Sortable === 'undefined' || !el.reorderList) return;
    reorderSortable = Sortable.create(el.reorderList, {
      animation: 150,
      handle: '.reorder-handle',
      draggable: '.reorder-item',
      ghostClass: 'sortable-ghost',
      chosenClass: 'sortable-chosen',
      dragClass: 'sortable-drag',
      scroll: true,
      scrollSensitivity: 80,
      scrollSpeed: 14,
      onEnd: (evt) => {
        if (evt.oldIndex === evt.newIndex) return;
        const movedId = evt.item.getAttribute('data-id');
        const visibleIds = Array.from(el.reorderList.querySelectorAll('.reorder-item'))
          .filter(r => !r.classList.contains('hidden'))
          .map(r => r.getAttribute('data-id'));
        currentReorderItems = mergeVisibleOrder(currentReorderItems, visibleIds);
        const newPos = currentReorderItems.findIndex(x => x.id === movedId);
        const moved = currentReorderItems[newPos];
        if (el.reorderStatusIndicator && moved) {
          el.reorderStatusIndicator.textContent = `✨ Moved "${moved.title}" to #${newPos + 1} (Click Save to apply)`;
          el.reorderStatusIndicator.style.color = '#facc15';
        }
        setTimeout(renderReorderList, 0);
      }
    });
  }

  let gridSortable = null;
  function initGridSortable() {
    if (gridSortable || typeof Sortable === 'undefined' || !el.catalogGrid) return;
    gridSortable = Sortable.create(el.catalogGrid, {
      animation: 150,
      draggable: '.catalog-card',
      filter: '.card-actions, .card-checkbox',
      preventOnFilter: false,
      delay: 150,
      delayOnTouchOnly: true,
      ghostClass: 'sortable-ghost',
      chosenClass: 'sortable-chosen',
      dragClass: 'sortable-drag',
      scroll: true,
      disabled: state.activeCategory !== 'featured',
      onEnd: async (evt) => {
        if (evt.oldIndex === evt.newIndex || state.activeCategory !== 'featured') return;
        const movedId = evt.item.getAttribute('data-id');
        const visibleIds = Array.from(el.catalogGrid.querySelectorAll('.catalog-card'))
          .map(c => c.getAttribute('data-id'));
        const merged = mergeVisibleOrder(getFeaturedItemsSorted(), visibleIds);
        const newPos = merged.findIndex(x => x.id === movedId);
        const moved = merged[newPos];

        try {
          const res = await fetch('/api/catalog/batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              action: 'reorder_featured',
              orderedIds: merged.map(x => x.id)
            })
          });
          const data = await res.json();
          if (!res.ok || !data.success) throw new Error(data.error || 'Failed to reorder');
          showToast(`⭐ Moved "${moved ? moved.title : movedId}" to spotlight #${newPos + 1}!`, 'success');
        } catch (err) {
          showToast('Error reordering: ' + err.message, 'error');
        }
        await loadCatalogData();
      }
    });
  }

  function syncGridSortableState() {
    if (gridSortable) gridSortable.option('disabled', state.activeCategory !== 'featured');
  }

  async function saveFeaturedOrder() {
    if (!currentReorderItems) return;
    try {
      if (el.reorderSaveBtn) {
        el.reorderSaveBtn.disabled = true;
        el.reorderSaveBtn.textContent = 'Saving...';
      }

      const orderedIds = currentReorderItems.map(x => x.id);
      const unfeaturedIds = Array.from(unfeaturedInModal);

      const res = await fetch('/api/catalog/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'reorder_featured',
          orderedIds: orderedIds,
          unfeaturedIds: unfeaturedIds
        })
      });

      const data = await res.json();
      if (!res.ok || !data.success) throw new Error(data.error || 'Failed to save order');

      showToast(`⭐ Saved spotlight order for ${orderedIds.length} featured screensavers!`, 'success');
      closeReorderFeaturedModal();
      await loadCatalogData();
    } catch (err) {
      showToast('Error saving order: ' + err.message, 'error');
    } finally {
      if (el.reorderSaveBtn) {
        el.reorderSaveBtn.disabled = false;
        el.reorderSaveBtn.textContent = '⭐ Save Spotlight Order';
      }
    }
  }

  function updatePriorityHint() {
    if (!el.featureSchedulePriorityHint) return;
    const top = getTopFeaturedPriority();
    el.featureSchedulePriorityHint.textContent = isBatchFeatureMode
      ? `Leave blank to keep each item's current priority. Current top: ${top}.`
      : `Current top priority: ${top}. Ties are ordered newest first.`;
  }

  function openFeatureScheduleModal(itemId, isBatch = false) {
    isBatchFeatureMode = Boolean(isBatch);
    if (isBatchFeatureMode) {
      const count = state.selectedIds.size;
      if (count === 0) {
        showToast('No screensavers selected', 'info');
        return;
      }
      activeFeatureItemId = null;
      if (el.featureScheduleModalTitle) {
        el.featureScheduleModalTitle.textContent = '⭐ Bulk Feature Screensavers';
      }
      if (el.featureScheduleTitle) {
        el.featureScheduleTitle.textContent = `Schedule spotlight duration for ${count} selected wallpapers`;
      }
      if (el.featureScheduleSaveBtn) {
        el.featureScheduleSaveBtn.textContent = `⭐ Feature (${count})`;
      }
      if (el.featureScheduleUnfeatureBtn) {
        el.featureScheduleUnfeatureBtn.textContent = '☆ Unfeature Selected';
        el.featureScheduleUnfeatureBtn.classList.remove('hidden');
      }

      const curPreset = el.batchFeatureDurationSelect ? el.batchFeatureDurationSelect.value : '14';
      if (curPreset && curPreset !== 'custom') {
        el.featureScheduleDateInput.value = curPreset === '0' ? '' : getDatePreset(curPreset);
      } else {
        el.featureScheduleDateInput.value = getDatePreset(14);
      }

      if (el.featureSchedulePriorityInput) el.featureSchedulePriorityInput.value = '';
      updatePriorityHint();

      document.querySelectorAll('.feat-quick-btn').forEach(btn => {
        const days = btn.getAttribute('data-days');
        if (curPreset !== 'custom' && days === curPreset) {
          btn.classList.add('active');
        } else if (curPreset === 'custom' && days === '14') {
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
      });

      el.featureScheduleModal.classList.remove('hidden');
      return;
    }

    const item = state.catalog.find(x => x.id === itemId);
    if (!item) return;
    activeFeatureItemId = itemId;
    if (el.featureScheduleModalTitle) {
      el.featureScheduleModalTitle.textContent = '⭐ Feature Screensaver';
    }
    if (el.featureScheduleTitle) {
      el.featureScheduleTitle.textContent = item.title ? `Schedule: ${item.title}` : `Schedule item: ${itemId}`;
    }
    if (el.featureScheduleSaveBtn) {
      el.featureScheduleSaveBtn.textContent = '⭐ Apply Feature';
    }

    const isFeat = Boolean(item.featured);
    if (el.featureScheduleUnfeatureBtn) {
      el.featureScheduleUnfeatureBtn.textContent = '☆ Remove Featured';
      el.featureScheduleUnfeatureBtn.classList.toggle('hidden', !isFeat);
    }

    if (item.featuredUntil) {
      el.featureScheduleDateInput.value = item.featuredUntil;
    } else if (isFeat) {
      el.featureScheduleDateInput.value = '';
    } else {
      el.featureScheduleDateInput.value = getDatePreset(14);
    }

    const rank = getItemFeaturedRank(item.id);
    const totalFeat = getFeaturedItemsSorted().length;
    if (el.featureScheduleRankBadge) {
      if (item.featured && rank) {
        el.featureScheduleRankBadge.textContent = `Spotlight Rank: #${rank} of ${totalFeat}`;
        el.featureScheduleRankBadge.className = `reorder-rank ${rank === 1 ? 'rank-1' : (rank === 2 ? 'rank-2' : (rank === 3 ? 'rank-3' : ''))}`;
        el.featureScheduleRankBadge.style.width = 'auto';
        el.featureScheduleRankBadge.style.padding = '2px 10px';
      } else {
        el.featureScheduleRankBadge.textContent = 'Will be added to Spotlight';
        el.featureScheduleRankBadge.className = 'reorder-rank';
        el.featureScheduleRankBadge.style.width = 'auto';
        el.featureScheduleRankBadge.style.padding = '2px 10px';
      }
    }

    if (el.featureSchedulePriorityInput) {
      el.featureSchedulePriorityInput.value = item.featuredPriority ? String(item.featuredPriority) : '';
    }
    updatePriorityHint();

    document.querySelectorAll('.feat-quick-btn').forEach(btn => {
      const days = btn.getAttribute('data-days');
      if (item.featuredUntil && getDatePreset(days) === item.featuredUntil) {
        btn.classList.add('active');
      } else if (!item.featuredUntil && !isFeat && days === '14') {
        btn.classList.add('active');
      } else if (!item.featuredUntil && isFeat && days === '0') {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    el.featureScheduleModal.classList.remove('hidden');
  }

  function closeFeatureScheduleModal() {
    el.featureScheduleModal.classList.add('hidden');
    activeFeatureItemId = null;
    isBatchFeatureMode = false;
    if (el.batchFeatureDurationSelect && el.batchFeatureDurationSelect.value === 'custom') {
      el.batchFeatureDurationSelect.value = '14';
    }
  }

  function readPriorityInput() {
    if (!el.featureSchedulePriorityInput) return null;
    const raw = el.featureSchedulePriorityInput.value.trim();
    if (raw === '') return null;
    const n = parseInt(raw, 10);
    return Number.isFinite(n) ? Math.max(0, n) : null;
  }

  async function applyFeatureSchedule() {
    const dateVal = el.featureScheduleDateInput.value ? el.featureScheduleDateInput.value.trim() : null;

    if (isBatchFeatureMode) {
      const count = state.selectedIds.size;
      if (count === 0) {
        closeFeatureScheduleModal();
        return;
      }
      try {
        const res = await fetch('/api/catalog/batch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action: 'feature',
            ids: Array.from(state.selectedIds),
            featuredUntil: dateVal || null,
            featuredPriority: readPriorityInput()
          })
        });
        const data = await res.json();
        if (!res.ok || !data.success) throw new Error(data.error || 'Failed to bulk feature screensavers');

        showToast(dateVal ? `⭐ Featured ${count} screensavers until ${dateVal}` : `⭐ Featured ${count} screensavers indefinitely`, 'success');
        state.selectedIds.clear();
        updateBatchBar();
        closeFeatureScheduleModal();
        await loadCatalogData();
      } catch (err) {
        showToast(`Error: ${err.message}`, 'error');
      }
      return;
    }

    if (!activeFeatureItemId) return;
    try {
      const res = await fetch(`/api/catalog/item/${encodeURIComponent(activeFeatureItemId)}/feature`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          featured: true,
          featuredUntil: dateVal || null,
          featuredPriority: readPriorityInput() ?? 0
        })
      });
      const data = await res.json();
      if (!res.ok || !data.success) throw new Error(data.error || 'Failed to feature screensaver');

      showToast(dateVal ? `⭐ Featured until ${dateVal}` : '⭐ Featured indefinitely', 'success');
      closeFeatureScheduleModal();
      await loadCatalogData();
    } catch (err) {
      showToast(`Error: ${err.message}`, 'error');
    }
  }

  async function removeFeatureSchedule() {
    if (isBatchFeatureMode) {
      const count = state.selectedIds.size;
      if (count === 0) {
        closeFeatureScheduleModal();
        return;
      }
      try {
        const res = await fetch('/api/catalog/batch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action: 'unfeature',
            ids: Array.from(state.selectedIds)
          })
        });
        const data = await res.json();
        if (!res.ok || !data.success) throw new Error(data.error || 'Failed to unfeature screensavers');

        showToast(`Removed featured status from ${count} screensavers`, 'info');
        state.selectedIds.clear();
        updateBatchBar();
        closeFeatureScheduleModal();
        await loadCatalogData();
      } catch (err) {
        showToast(`Error: ${err.message}`, 'error');
      }
      return;
    }

    if (!activeFeatureItemId) return;
    try {
      const res = await fetch(`/api/catalog/item/${encodeURIComponent(activeFeatureItemId)}/feature`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ featured: false })
      });
      const data = await res.json();
      if (!res.ok || !data.success) throw new Error(data.error || 'Failed to remove featured status');

      showToast('Featured status removed', 'info');
      closeFeatureScheduleModal();
      await loadCatalogData();
    } catch (err) {
      showToast(`Error: ${err.message}`, 'error');
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

    // Clickable Low Performing Stat in Header
    if (el.statLowPerformingBtn) {
      el.statLowPerformingBtn.addEventListener('click', () => {
        state.statusFilter = 'low-downloads-5';
        if (el.filterStatus) el.filterStatus.value = 'low-downloads-5';
        state.sortBy = 'downloads-asc';
        if (el.sortBy) el.sortBy.value = 'downloads-asc';
        renderCatalog();
        showToast('Filtered to low-performing screensavers (≤ 5 downloads) for pruning', 'info');
      });
    }

    // Sort by Downloads Table Header Click
    if (el.thSortDownloads) {
      el.thSortDownloads.addEventListener('click', () => {
        state.sortBy = state.sortBy === 'downloads-asc' ? 'downloads-desc' : 'downloads-asc';
        if (el.sortBy) el.sortBy.value = state.sortBy;
        renderCatalog();
        showToast(`Sorted by downloads (${state.sortBy === 'downloads-asc' ? 'least' : 'most'} first)`, 'info');
      });
    }

    // Sort by Date Table Header Click
    if (el.thSortDate) {
      el.thSortDate.addEventListener('click', () => {
        state.sortBy = state.sortBy === 'newest' ? 'oldest' : 'newest';
        if (el.sortBy) el.sortBy.value = state.sortBy;
        renderCatalog();
        showToast(`Sorted by date (${state.sortBy === 'newest' ? 'newest' : 'oldest'} first)`, 'info');
      });
    }

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
      const featBtn = e.target.closest('.btn-feature-card');
      const editBtn = e.target.closest('.btn-edit-card');
      const delBtn = e.target.closest('.btn-delete-card');
      const checkbox = e.target.closest('.card-checkbox');
      const card = e.target.closest('.catalog-card');

      if (featBtn) {
        e.stopPropagation();
        openFeatureScheduleModal(featBtn.getAttribute('data-id'));
        return;
      }

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
      const featStar = e.target.closest('.table-featured-star');
      const editBtn = e.target.closest('.btn-edit-card');
      const delBtn = e.target.closest('.btn-delete-card');
      const checkbox = e.target.closest('.table-row-checkbox');
      const row = e.target.closest('tr');

      if (featStar) {
        e.stopPropagation();
        openFeatureScheduleModal(featStar.getAttribute('data-id'));
        return;
      }

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
    if (el.batchSelectVisibleBtn) {
      el.batchSelectVisibleBtn.addEventListener('click', () => {
        const visibleItems = getFilteredItems();
        visibleItems.forEach(item => state.selectedIds.add(item.id));
        updateBatchBar();
        renderCatalog();
        showToast(`Selected all ${visibleItems.length} visible screensavers`, 'info');
      });
    }

    el.batchClearBtn.addEventListener('click', () => {
      state.selectedIds.clear();
      updateBatchBar();
      renderCatalog();
    });

    el.batchApplyCategory.addEventListener('click', () => {
      const cat = el.batchCategorySelect.value;
      if (cat) executeBatchAddCategory(cat);
    });

    if (el.batchApplyTag && el.batchTagInput) {
      el.batchApplyTag.addEventListener('click', async () => {
        const tag = el.batchTagInput.value.trim().toLowerCase().replace(/^#/, '');
        if (!tag) {
          showToast('Please enter a tag name', 'error');
          return;
        }
        if (state.selectedIds.size === 0) return;

        try {
          const res = await fetch('/api/catalog/batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              action: 'add_tags',
              tags: [tag],
              ids: Array.from(state.selectedIds)
            })
          });
          const data = await res.json();
          if (data.success) {
            showToast(`Added #${tag} to ${state.selectedIds.size} items!`, 'success');
            el.batchTagInput.value = '';
            await loadCatalogData();
          }
        } catch (err) {
          showToast('Batch tag error: ' + err.message, 'error');
        }
      });
      el.batchTagInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          el.batchApplyTag.click();
        }
      });
    }

    el.batchDeleteBtn.addEventListener('click', () => {
      executeBatchDelete();
    });

    if (el.batchFeatureDurationSelect) {
      el.batchFeatureDurationSelect.addEventListener('change', (e) => {
        if (e.target.value === 'custom') {
          if (state.selectedIds.size === 0) {
            showToast('Select one or more screensavers first', 'info');
            e.target.value = '14';
            return;
          }
          openFeatureScheduleModal(null, true);
        }
      });
    }

    if (el.btnOpenReorderModal) {
      el.btnOpenReorderModal.addEventListener('click', openReorderFeaturedModal);
    }
    if (el.batchPrioritizeBtn) {
      el.batchPrioritizeBtn.addEventListener('click', openReorderFeaturedModal);
    }
    if (el.editOpenReorderBtn) {
      el.editOpenReorderBtn.addEventListener('click', () => {
        closeInspector();
        openReorderFeaturedModal();
      });
    }
    if (el.featureScheduleOpenReorderBtn) {
      el.featureScheduleOpenReorderBtn.addEventListener('click', () => {
        closeFeatureScheduleModal();
        openReorderFeaturedModal();
      });
    }
    if (el.reorderModalCloseBtn) {
      el.reorderModalCloseBtn.addEventListener('click', closeReorderFeaturedModal);
    }
    if (el.reorderCancelBtn) {
      el.reorderCancelBtn.addEventListener('click', closeReorderFeaturedModal);
    }
    if (el.reorderSaveBtn) {
      el.reorderSaveBtn.addEventListener('click', saveFeaturedOrder);
    }
    if (el.reorderSearchInput) {
      el.reorderSearchInput.addEventListener('input', renderReorderList);
    }
    if (el.reorderSortNewestBtn) {
      el.reorderSortNewestBtn.addEventListener('click', () => {
        currentReorderItems.sort((a, b) => String(b.dateAdded || '').localeCompare(String(a.dateAdded || '')));
        if (el.reorderStatusIndicator) {
          el.reorderStatusIndicator.textContent = '✨ Sorted by newest date (Click Save to apply)';
          el.reorderStatusIndicator.style.color = '#facc15';
        }
        renderReorderList();
      });
    }
    if (el.reorderSortDownloadsBtn) {
      el.reorderSortDownloadsBtn.addEventListener('click', () => {
        currentReorderItems.sort((a, b) => (b.downloads || 0) - (a.downloads || 0));
        if (el.reorderStatusIndicator) {
          el.reorderStatusIndicator.textContent = '✨ Sorted by most downloads (Click Save to apply)';
          el.reorderStatusIndicator.style.color = '#facc15';
        }
        renderReorderList();
      });
    }

    if (el.reorderList) {
      el.reorderList.addEventListener('click', (e) => {
        const topBtn = e.target.closest('.btn-reorder-top');
        const upBtn = e.target.closest('.btn-reorder-up');
        const downBtn = e.target.closest('.btn-reorder-down');
        const bottomBtn = e.target.closest('.btn-reorder-bottom');
        const removeBtn = e.target.closest('.btn-reorder-remove');

        if (topBtn) {
          const id = topBtn.getAttribute('data-id');
          const idx = currentReorderItems.findIndex(x => x.id === id);
          if (idx > 0) {
            const [item] = currentReorderItems.splice(idx, 1);
            currentReorderItems.unshift(item);
            if (el.reorderStatusIndicator) {
              el.reorderStatusIndicator.textContent = `✨ Moved "${item.title}" to #1 (Click Save to apply)`;
              el.reorderStatusIndicator.style.color = '#facc15';
            }
            renderReorderList();
          }
        } else if (upBtn) {
          const id = upBtn.getAttribute('data-id');
          const idx = currentReorderItems.findIndex(x => x.id === id);
          if (idx > 0) {
            const temp = currentReorderItems[idx - 1];
            currentReorderItems[idx - 1] = currentReorderItems[idx];
            currentReorderItems[idx] = temp;
            if (el.reorderStatusIndicator) {
              el.reorderStatusIndicator.textContent = `✨ Moved "${currentReorderItems[idx - 1].title}" up to #${idx} (Click Save to apply)`;
              el.reorderStatusIndicator.style.color = '#facc15';
            }
            renderReorderList();
          }
        } else if (downBtn) {
          const id = downBtn.getAttribute('data-id');
          const idx = currentReorderItems.findIndex(x => x.id === id);
          if (idx >= 0 && idx < currentReorderItems.length - 1) {
            const temp = currentReorderItems[idx + 1];
            currentReorderItems[idx + 1] = currentReorderItems[idx];
            currentReorderItems[idx] = temp;
            if (el.reorderStatusIndicator) {
              el.reorderStatusIndicator.textContent = `✨ Moved "${currentReorderItems[idx + 1].title}" down to #${idx + 2} (Click Save to apply)`;
              el.reorderStatusIndicator.style.color = '#facc15';
            }
            renderReorderList();
          }
        } else if (bottomBtn) {
          const id = bottomBtn.getAttribute('data-id');
          const idx = currentReorderItems.findIndex(x => x.id === id);
          if (idx >= 0 && idx < currentReorderItems.length - 1) {
            const [item] = currentReorderItems.splice(idx, 1);
            currentReorderItems.push(item);
            if (el.reorderStatusIndicator) {
              el.reorderStatusIndicator.textContent = `✨ Moved "${item.title}" to bottom (Click Save to apply)`;
              el.reorderStatusIndicator.style.color = '#facc15';
            }
            renderReorderList();
          }
        } else if (removeBtn) {
          const id = removeBtn.getAttribute('data-id');
          const idx = currentReorderItems.findIndex(x => x.id === id);
          if (idx >= 0) {
            const [removed] = currentReorderItems.splice(idx, 1);
            unfeaturedInModal.add(id);
            if (el.reorderStatusIndicator) {
              el.reorderStatusIndicator.textContent = `✨ Removed "${removed.title}" from spotlight (Click Save to apply)`;
              el.reorderStatusIndicator.style.color = '#f87171';
            }
            renderReorderList();
          }
        }
      });
    }

    // Direct Drag & Drop in Catalog Grid (SortableJS)
    initGridSortable();

    if (el.batchFeatureBtn) {
      el.batchFeatureBtn.addEventListener('click', () => executeBatchFeature(true));
    }
    if (el.batchUnfeatureBtn) {
      el.batchUnfeatureBtn.addEventListener('click', () => executeBatchFeature(false));
    }

    // Feature Schedule Modal Event Listeners
    if (el.featureScheduleCloseBtn) {
      el.featureScheduleCloseBtn.addEventListener('click', closeFeatureScheduleModal);
    }
    if (el.featureScheduleCancelBtn) {
      el.featureScheduleCancelBtn.addEventListener('click', closeFeatureScheduleModal);
    }
    if (el.featureScheduleSaveBtn) {
      el.featureScheduleSaveBtn.addEventListener('click', applyFeatureSchedule);
    }
    if (el.featureScheduleUnfeatureBtn) {
      el.featureScheduleUnfeatureBtn.addEventListener('click', removeFeatureSchedule);
    }

    if (el.featureScheduleDateInput) {
      el.featureScheduleDateInput.addEventListener('input', () => {
        const val = el.featureScheduleDateInput.value;
        document.querySelectorAll('.feat-quick-btn').forEach(b => {
          const days = b.getAttribute('data-days');
          b.classList.toggle('active', getDatePreset(days) === val || (!val && days === '0'));
        });
      });
    }

    // Quick presets inside feature schedule modal
    document.querySelectorAll('.feat-quick-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.feat-quick-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const days = btn.getAttribute('data-days');
        if (el.featureScheduleDateInput) {
          el.featureScheduleDateInput.value = getDatePreset(days);
        }
      });
    });

    if (el.featureScheduleTopBtn) {
      el.featureScheduleTopBtn.addEventListener('click', () => {
        if (el.featureSchedulePriorityInput) {
          el.featureSchedulePriorityInput.value = String(getTopFeaturedPriority() + 10);
        }
        if (el.featureScheduleRankBadge) {
          el.featureScheduleRankBadge.textContent = 'Rank #1 (Pending Apply)';
          el.featureScheduleRankBadge.className = 'reorder-rank rank-1';
        }
        showToast('Will be moved to #1 spotlight on apply', 'info');
      });
    }

    if (el.editFeaturedTopBtn) {
      el.editFeaturedTopBtn.addEventListener('click', async () => {
        if (!state.activeItem) return;
        const current = getFeaturedItemsSorted();
        const otherIds = current.filter(x => x.id !== state.activeItem.id).map(x => x.id);
        const newOrder = [state.activeItem.id, ...otherIds];
        try {
          const res = await fetch('/api/catalog/batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              action: 'reorder_featured',
              orderedIds: newOrder
            })
          });
          const data = await res.json();
          if (!res.ok || !data.success) throw new Error(data.error || 'Failed to move to top');
          showToast(`⭐ Moved "${state.activeItem.title}" to #1 spotlight!`, 'success');
          await loadCatalogData();
          openInspector(state.activeItem.id);
        } catch (err) {
          showToast('Error moving to top: ' + err.message, 'error');
        }
      });
    }

    if (el.editFeaturedToggle) {
      el.editFeaturedToggle.addEventListener('change', () => {
        if (el.editFeaturedDetails) {
          el.editFeaturedDetails.classList.toggle('hidden', !el.editFeaturedToggle.checked);
        }
        if (el.editFeaturedToggle.checked && el.editFeaturedUntil && !el.editFeaturedUntil.value) {
          el.editFeaturedUntil.value = getDatePreset(14);
        }
      });
    }

    document.querySelectorAll('.edit-feat-preset-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.edit-feat-preset-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const days = btn.getAttribute('data-days');
        if (el.editFeaturedUntil) {
          el.editFeaturedUntil.value = getDatePreset(days);
        }
      });
    });

    // Quick presets inside add modal
    if (el.addFeaturedToggle) {
      el.addFeaturedToggle.addEventListener('change', () => {
        if (el.addFeaturedDetails) {
          el.addFeaturedDetails.classList.toggle('hidden', !el.addFeaturedToggle.checked);
        }
        if (el.addFeaturedToggle.checked && el.addFeaturedUntil && !el.addFeaturedUntil.value) {
          el.addFeaturedUntil.value = getDatePreset(14);
        }
      });
    }

    document.querySelectorAll('.add-feat-preset-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.add-feat-preset-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const days = btn.getAttribute('data-days');
        if (el.addFeaturedUntil) {
          el.addFeaturedUntil.value = getDatePreset(days);
        }
      });
    });

    // Inspector Tag Editor
    if (el.editTagInput) {
      el.editTagInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ',') {
          e.preventDefault();
          if (state.activeItemTags) {
            addTagToEditor(state.activeItemTags, el.editTagInput.value);
            el.editTagInput.value = '';
          }
        }
      });
    }
    if (el.btnAddTagEdit && el.editTagInput) {
      el.btnAddTagEdit.addEventListener('click', () => {
        if (state.activeItemTags) {
          addTagToEditor(state.activeItemTags, el.editTagInput.value);
          el.editTagInput.value = '';
        }
      });
    }

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

    // Bulk Add Modal
    if (el.btnBulkAdd) el.btnBulkAdd.addEventListener('click', openBulkModal);
    if (el.btnSwitchToBulk) el.btnSwitchToBulk.addEventListener('click', () => {
      closeAddModal();
      openBulkModal();
    });
    if (el.bulkModalCloseBtn) el.bulkModalCloseBtn.addEventListener('click', closeBulkModal);
    if (el.bulkModalCancelBtn) el.bulkModalCancelBtn.addEventListener('click', closeBulkModal);
    if (el.bulkModalSubmitBtn) el.bulkModalSubmitBtn.addEventListener('click', executeBulkImport);

    if (el.tabBulkFiles) el.tabBulkFiles.addEventListener('click', () => setBulkSourceTab('files'));
    if (el.tabBulkFolder) el.tabBulkFolder.addEventListener('click', () => setBulkSourceTab('folder'));

    if (el.btnScanFolder) el.btnScanFolder.addEventListener('click', scanLocalFolder);
    if (el.bulkFolderInputPath) {
      el.bulkFolderInputPath.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          scanLocalFolder();
        }
      });
    }

    if (el.btnClearStaged) {
      el.btnClearStaged.addEventListener('click', () => {
        state.stagedBulkItems.forEach(item => {
          if (item.previewUrl && item.previewUrl.startsWith('blob:')) {
            URL.revokeObjectURL(item.previewUrl);
          }
        });
        state.stagedBulkItems = [];
        renderBulkStagedList();
      });
    }

    if (el.bulkDropzone) {
      el.bulkDropzone.addEventListener('click', () => {
        el.bulkFileInput.click();
      });
      el.bulkDropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        el.bulkDropzone.classList.add('dragover');
      });
      el.bulkDropzone.addEventListener('dragleave', () => {
        el.bulkDropzone.classList.remove('dragover');
      });
      el.bulkDropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        el.bulkDropzone.classList.remove('dragover');
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
          addFilesToBulkStaged(e.dataTransfer.files);
        }
      });
    }

    if (el.bulkFileInput) {
      el.bulkFileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
          addFilesToBulkStaged(e.target.files);
          el.bulkFileInput.value = '';
        }
      });
    }

    if (el.bulkAutoFeatureToggle) {
      el.bulkAutoFeatureToggle.addEventListener('change', updateBulkAutoFeatureState);
    }
    if (el.bulkAutoFeatureDuration) {
      el.bulkAutoFeatureDuration.addEventListener('change', (e) => {
        if (el.bulkAutoFeatureDate) {
          const isCustom = e.target.value === 'custom';
          el.bulkAutoFeatureDate.classList.toggle('hidden', !isCustom);
          if (isCustom && !el.bulkAutoFeatureDate.value) {
            el.bulkAutoFeatureDate.value = getDatePreset(14);
          }
        }
      });
    }

    // Sync & Backups
    if (el.btnSyncDownloads) {
      el.btnSyncDownloads.addEventListener('click', async () => {
        try {
          el.btnSyncDownloads.disabled = true;
          el.btnSyncDownloads.innerHTML = `
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
            <span>Syncing...</span>
          `;
          await loadCatalogData(true);
          showToast(`Successfully refreshed live downloads from Cloudflare!`, 'success');
        } catch (err) {
          showToast(`Error syncing downloads: ${err.message}`, 'error');
        } finally {
          el.btnSyncDownloads.disabled = false;
          el.btnSyncDownloads.innerHTML = `
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
            <span>Sync Downloads</span>
          `;
        }
      });
    }

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
        } else if (el.reorderModal && !el.reorderModal.classList.contains('hidden')) {
          closeReorderFeaturedModal();
        } else if (el.featureScheduleModal && !el.featureScheduleModal.classList.contains('hidden')) {
          closeFeatureScheduleModal();
        } else if (!el.addModal.classList.contains('hidden')) {
          closeAddModal();
        } else if (!el.bulkModal.classList.contains('hidden')) {
          closeBulkModal();
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
