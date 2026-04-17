'use strict';

// ── Live table search with row count ─────────────────────────────────────────
function initTableSearch(inputId, tableId) {
  const input   = document.getElementById(inputId);
  const table   = document.getElementById(tableId);
  const countEl = document.getElementById(inputId + '-count');
  const clearEl = document.getElementById(inputId + '-clear');
  if (!input || !table) return;

  const rows = Array.from(table.querySelectorAll('tbody tr'));
  const total = rows.length;

  function filter() {
    const q = input.value.trim().toLowerCase();
    const activeStatus = table.dataset.activeStatus || '';
    let visible = 0;
    rows.forEach(row => {
      const textMatch = !q || row.textContent.toLowerCase().includes(q);
      const statusBadge = row.querySelector('.status-badge');
      const statusMatch = !activeStatus || (statusBadge && statusBadge.textContent.trim() === activeStatus);
      const match = textMatch && statusMatch;
      row.style.display = match ? '' : 'none';
      if (match) visible++;
    });
    if (countEl) countEl.textContent = (q || activeStatus) ? `${visible} of ${total}` : `${total}`;
    if (clearEl) clearEl.style.display = q ? 'flex' : 'none';
  }

  input.addEventListener('input', filter);

  if (clearEl) {
    clearEl.style.display = 'none';
    clearEl.addEventListener('click', () => { input.value = ''; filter(); input.focus(); });
  }

  filter();
  return filter;
}

// ── Sortable column headers ───────────────────────────────────────────────────
function initSortableTable(tableId) {
  const table = document.getElementById(tableId);
  if (!table) return;

  const allTh = Array.from(table.querySelectorAll('thead th'));
  // Mark all non-action headers as sortable
  allTh.forEach((th, i) => {
    if (th.textContent.trim() === 'Actions') return;
    th.style.cursor = 'pointer';
    th.style.userSelect = 'none';
    th.title = 'Click to sort';
    // Add sort icon placeholder
    const icon = document.createElement('span');
    icon.className = 'sort-icon ms-1 text-muted';
    icon.textContent = '⇅';
    th.appendChild(icon);

    let asc = true;
    th.addEventListener('click', () => {
      const tbody = table.querySelector('tbody');
      const rows  = Array.from(tbody.querySelectorAll('tr[style=""], tr:not([style])')).concat(
                    Array.from(tbody.querySelectorAll('tr[style*="display"]'))
                    .filter(r => r.style.display !== 'none'));
      const allRows = Array.from(tbody.querySelectorAll('tr'));

      allRows.sort((a, b) => {
        const aVal = (a.cells[i]?.innerText || '').trim();
        const bVal = (b.cells[i]?.innerText || '').trim();
        const aNum = parseFloat(aVal.replace(/[$,%]/g, ''));
        const bNum = parseFloat(bVal.replace(/[$,%]/g, ''));
        if (!isNaN(aNum) && !isNaN(bNum)) return asc ? aNum - bNum : bNum - aNum;
        return asc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      });

      allRows.forEach(r => tbody.appendChild(r));

      // Reset all icons
      allTh.forEach(h => { const ic = h.querySelector('.sort-icon'); if (ic) ic.textContent = '⇅'; });
      icon.textContent = asc ? '▲' : '▼';
      asc = !asc;
    });
  });
}

// ── Delete confirmation modal ─────────────────────────────────────────────────
function initDeleteModal() {
  const modalEl = document.getElementById('deleteModal');
  if (!modalEl) return;

  let pendingForm = null;
  const bsModal   = new bootstrap.Modal(modalEl);
  const bodyEl    = document.getElementById('deleteModalBody');
  const confirmEl = document.getElementById('deleteModalConfirm');

  document.addEventListener('submit', e => {
    const form = e.target.closest('form[data-confirm]');
    if (!form) return;
    e.preventDefault();
    pendingForm = form;
    if (bodyEl) bodyEl.textContent = form.dataset.confirm;
    bsModal.show();
  });

  confirmEl.addEventListener('click', () => {
    bsModal.hide();
    if (pendingForm) {
      const f = pendingForm;
      pendingForm = null;
      // Remove intercept so it submits normally
      const saved = f.dataset.confirm;
      delete f.dataset.confirm;
      f.submit();
      f.dataset.confirm = saved;
    }
  });
}

// ── Queue auto-refresh countdown ──────────────────────────────────────────────
function initQueueRefresh(seconds) {
  const countEl = document.getElementById('refresh-countdown');
  const barEl   = document.getElementById('refresh-bar');
  if (!countEl) return;

  let remaining = seconds;
  setInterval(() => {
    remaining--;
    if (countEl) countEl.textContent = remaining;
    if (barEl)   barEl.style.width = `${(remaining / seconds) * 100}%`;
    if (remaining <= 0) location.reload();
  }, 1000);
}

// ── Status filter pills (appointments) ───────────────────────────────────────
function initStatusFilter(tableId, refilterFn) {
  const pills = document.querySelectorAll('[data-filter-status]');
  const table = document.getElementById(tableId);
  if (!pills.length || !table) return;

  function applyFilter(status) {
    table.dataset.activeStatus = status;
    if (refilterFn) {
      refilterFn();
    } else {
      Array.from(table.querySelectorAll('tbody tr')).forEach(row => {
        const badge = row.querySelector('.status-badge');
        row.style.display = (!status || (badge && badge.textContent.trim() === status)) ? '' : 'none';
      });
    }
    pills.forEach(p => p.classList.toggle('active', p.dataset.filterStatus === status));
  }

  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      const current = pill.classList.contains('active') && pill.dataset.filterStatus;
      applyFilter(current ? '' : pill.dataset.filterStatus);
    });
  });
}

// ── Auto-dismiss alerts after 4s ─────────────────────────────────────────────
function initAutoDismissAlerts() {
  document.querySelectorAll('.alert.alert-success, .alert.alert-info').forEach(el => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      if (bsAlert) bsAlert.close();
    }, 4000);
  });
}

// ── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initDeleteModal();
  initAutoDismissAlerts();
});
