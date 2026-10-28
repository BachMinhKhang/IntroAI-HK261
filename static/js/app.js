/**
 * app.js
 * Puzzle Pipes AI Solver - Interactive Visualizer Controller
 * Clean English UI: Direct testcases in inputs/, scrubber, playback controls, compare both.
 */

// Bitmask directional constants
const NORTH = 1;
const EAST = 2;
const SOUTH = 4;
const WEST = 8;
const DIRECTIONS = [NORTH, EAST, SOUTH, WEST];
const OPPOSITE = { [NORTH]: SOUTH, [EAST]: WEST, [SOUTH]: NORTH, [WEST]: EAST };
const DELTAS = {
  [NORTH]: [-1, 0],
  [EAST]:  [0, 1],
  [SOUTH]: [1, 0],
  [WEST]:  [0, -1]
};

// Global App State
const state = {
  rows: 0,
  cols: 0,
  grid: [],
  initialGrid: [],
  steps: [],
  currentStepIndex: -1,
  isPlaying: false,
  timerId: null,
  speed: 150,
  selectedAlgo: 'astar',
  currentFilename: ''
};

// Cached DOM Elements
const el = {
  gridContainer: document.getElementById('grid-container'),
  boardViewport: document.getElementById('board-viewport'),
  levelSelect: document.getElementById('level-select'),
  randomSize: document.getElementById('random-size'),
  btnGenerate: document.getElementById('btn-generate'),
  btnSolve: document.getElementById('btn-solve'),
  btnCompare: document.getElementById('btn-compare'),
  btnStart: document.getElementById('btn-start'),
  btnPrev: document.getElementById('btn-prev'),
  btnPlay: document.getElementById('btn-play'),
  btnNext: document.getElementById('btn-next'),
  btnEnd: document.getElementById('btn-end'),
  btnReset: document.getElementById('btn-reset'),
  stepScrubber: document.getElementById('step-scrubber'),
  scrubberLabel: document.getElementById('scrubber-label'),
  scrubberPct: document.getElementById('scrubber-pct'),
  levelTitle: document.getElementById('level-title'),
  tileCountBadge: document.getElementById('tile-count-badge'),
  conflictBadge: document.getElementById('conflict-badge'),
  boardStatus: document.getElementById('board-status'),
  headerLevelBadge: document.getElementById('header-level-badge'),
  statTime: document.getElementById('stat-time'),
  statMemory: document.getElementById('stat-memory'),
  statNodes: document.getElementById('stat-nodes'),
  statSteps: document.getElementById('stat-steps'),
  stepLog: document.getElementById('step-log'),
  btnClearLog: document.getElementById('btn-clear-log'),
  activeAlgoBadge: document.getElementById('active-algo-badge'),
  comparisonCard: document.getElementById('comparison-card'),
  btnCloseComp: document.getElementById('btn-close-comp'),
  compLevelName: document.getElementById('comp-level-name'),
  compDfsTime: document.getElementById('comp-dfs-time'),
  compAstarTime: document.getElementById('comp-astar-time'),
  compDfsRam: document.getElementById('comp-dfs-ram'),
  compAstarRam: document.getElementById('comp-astar-ram'),
  compDfsNodes: document.getElementById('comp-dfs-nodes'),
  compAstarNodes: document.getElementById('comp-astar-nodes'),
  compDfsSteps: document.getElementById('comp-dfs-steps'),
  compAstarSteps: document.getElementById('comp-astar-steps'),
  themeToggle: document.getElementById('theme-toggle'),
  themeIcon: document.getElementById('theme-icon')
};

// ==========================================
// 1. App Initialization & Event Listeners
// ==========================================
document.addEventListener('DOMContentLoaded', async () => {
  initTheme();
  setupEventListeners();
  await fetchLevels();
});

function initTheme() {
  const saved = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const isDark = saved === 'dark' || (!saved && prefersDark);

  if (isDark) {
    document.documentElement.classList.add('dark');
    el.themeIcon.textContent = '☀️';
  } else {
    document.documentElement.classList.remove('dark');
    el.themeIcon.textContent = '🌙';
  }
}

function toggleTheme() {
  const isDark = document.documentElement.classList.toggle('dark');
  localStorage.setItem('theme', isDark ? 'dark' : 'light');
  el.themeIcon.textContent = isDark ? '☀️' : '🌙';
}

function setupEventListeners() {
  el.themeToggle.addEventListener('click', toggleTheme);
  el.levelSelect.addEventListener('change', onLevelSelected);
  el.btnGenerate.addEventListener('click', onGenerateRandom);
  el.btnSolve.addEventListener('click', onStartSolve);
  el.btnCompare.addEventListener('click', onCompareBoth);
  el.btnCloseComp.addEventListener('click', () => el.comparisonCard.classList.add('hidden'));

  // Playback Navigation
  el.btnStart.addEventListener('click', jumpToStart);
  el.btnPrev.addEventListener('click', stepBackward);
  el.btnPlay.addEventListener('click', togglePlay);
  el.btnNext.addEventListener('click', stepForward);
  el.btnEnd.addEventListener('click', jumpToEnd);
  el.btnReset.addEventListener('click', resetBoard);

  // Scrubber
  el.stepScrubber.addEventListener('input', (e) => {
    const targetStep = parseInt(e.target.value);
    scrubToStep(targetStep);
  });

  // Clear Log
  el.btnClearLog.addEventListener('click', () => {
    el.stepLog.innerHTML = '<div>Log cleared.</div>';
  });

  // Algorithm Radio Switchers
  document.querySelectorAll('input[name="algo"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
      state.selectedAlgo = e.target.value;
      updateAlgoCardUI();
    });
  });
}

function updateAlgoCardUI() {
  document.querySelectorAll('.algo-card').forEach(card => {
    const input = card.querySelector('input[type="radio"]');
    if (input.checked) {
      card.classList.add('active', 'border-sky-400', 'dark:border-sky-700', 'bg-sky-50/70', 'dark:bg-sky-950/40');
      card.classList.remove('border-slate-200', 'dark:border-slate-800');
    } else {
      card.classList.remove('active', 'border-sky-400', 'dark:border-sky-700', 'bg-sky-50/70', 'dark:bg-sky-950/40');
      card.classList.add('border-slate-200', 'dark:border-slate-800');
    }
  });

  if (state.selectedAlgo === 'astar') {
    el.activeAlgoBadge.textContent = 'A* SEARCH';
    el.activeAlgoBadge.className = 'text-[10px] font-mono px-2 py-0.5 rounded bg-sky-100 dark:bg-sky-950 text-sky-700 dark:text-sky-300';
  } else {
    el.activeAlgoBadge.textContent = 'DFS';
    el.activeAlgoBadge.className = 'text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300';
  }
}

// ==========================================
// 2. Fetching Testcases Directly From inputs/
// ==========================================
async function fetchLevels() {
  try {
    const res = await fetch('/api/levels');
    const data = await res.json();
    el.levelSelect.innerHTML = '';

    data.levels.forEach(lvl => {
      const opt = document.createElement('option');
      opt.value = lvl.filename;
      opt.textContent = lvl.label;
      el.levelSelect.appendChild(opt);
    });

    if (data.levels.length > 0) {
      el.levelSelect.value = data.levels[0].filename;
      await loadLevelFile(data.levels[0].filename);
    }
  } catch (err) {
    console.error('Failed to load levels list:', err);
    el.levelSelect.innerHTML = '<option value="">-- Error loading testcases --</option>';
  }
}

async function onLevelSelected(e) {
  const filename = e.target.value;
  if (filename) {
    await loadLevelFile(filename);
  }
}

async function loadLevelFile(filename) {
  try {
    setStatus('Loading...', 'idle');
    const res = await fetch('/api/load_level', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename })
    });
    const data = await res.json();
    state.currentFilename = filename;
    setNewBoard(data.grid, `Level: ${filename}`, data.conflicts);
  } catch (err) {
    console.error('Failed to load level file:', err);
    setStatus('Error', 'unsolvable');
  }
}

async function onGenerateRandom() {
  const size = parseInt(el.randomSize.value);
  try {
    setStatus('Generating...', 'solving');
    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ size })
    });
    const data = await res.json();
    state.currentFilename = `random_${size}x${size}`;
    setNewBoard(data.grid, `Random Map: ${size} × ${size}`, data.conflicts);
    el.levelSelect.value = '';
  } catch (err) {
    console.error('Failed to generate random map:', err);
    setStatus('Error', 'unsolvable');
  }
}

// ==========================================
// 3. Dynamic Tile Sizing & Board Rendering
// ==========================================
function getTileSize(cols, rows) {
  const maxDim = Math.max(cols, rows);
  if (maxDim <= 3) return 64;
  if (maxDim <= 5) return 56;
  if (maxDim <= 8) return 44;
  if (maxDim <= 10) return 34;
  if (maxDim <= 12) return 28;
  if (maxDim <= 15) return 24;
  if (maxDim <= 20) return 18;
  return 15; // 25x25
}

function setStatus(text, type = 'idle') {
  el.boardStatus.textContent = text;
  const base = 'px-3 py-1 text-xs font-semibold rounded-full border transition-colors ';
  if (type === 'solving') {
    el.boardStatus.className = base + 'bg-amber-50 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800';
  } else if (type === 'solved') {
    el.boardStatus.className = base + 'bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800';
  } else if (type === 'unsolvable') {
    el.boardStatus.className = base + 'bg-rose-50 dark:bg-rose-950/50 text-rose-700 dark:text-rose-300 border-rose-200 dark:border-rose-800';
  } else {
    el.boardStatus.className = base + 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700';
  }
}

function setNewBoard(grid, title, serverConflicts = null) {
  stopPlay();
  state.rows = grid.length;
  state.cols = grid[0].length;
  state.grid = grid.map(row => [...row]);
  state.initialGrid = grid.map(row => [...row]);
  state.steps = [];
  state.currentStepIndex = -1;

  el.levelTitle.textContent = title;
  el.tileCountBadge.textContent = `${state.rows * state.cols} tiles (${state.rows}x${state.cols})`;
  el.headerLevelBadge.textContent = `Grid: ${state.rows}x${state.cols}`;
  setStatus('Ready', 'idle');

  // Conflict Counter
  const conflicts = serverConflicts !== null ? serverConflicts : countBoardConflicts();
  el.conflictBadge.textContent = conflicts;

  // Reset Scrubber
  el.stepScrubber.min = 0;
  el.stepScrubber.max = 0;
  el.stepScrubber.value = 0;
  el.stepScrubber.disabled = true;
  el.scrubberLabel.textContent = 'Step 0 / 0';
  el.scrubberPct.textContent = '0%';

  // Reset Navigation Buttons
  el.btnSolve.disabled = false;
  el.btnStart.disabled = true;
  el.btnPrev.disabled = true;
  el.btnPlay.disabled = true;
  el.btnNext.disabled = true;
  el.btnEnd.disabled = true;

  // Reset Metrics HUD
  el.statTime.textContent = '-- ms';
  el.statMemory.textContent = '-- KB';
  el.statNodes.textContent = '--';
  el.statSteps.textContent = '0 / 0';
  el.stepLog.innerHTML = `<div>Loaded board [${state.rows}x${state.cols}]. Click "Solve Puzzle" to start search.</div>`;

  renderGrid();
}

function renderGrid() {
  el.gridContainer.innerHTML = '';
  const tileSize = getTileSize(state.cols, state.rows);
  const maxDim = Math.max(state.cols, state.rows);
  const gap = maxDim >= 20 ? 1 : (maxDim >= 10 ? 2 : 3);

  el.gridContainer.style.gap = `${gap}px`;
  el.gridContainer.style.gridTemplateColumns = `repeat(${state.cols}, ${tileSize}px)`;
  el.gridContainer.style.gridTemplateRows = `repeat(${state.rows}, ${tileSize}px)`;

  for (let r = 0; r < state.rows; r++) {
    for (let c = 0; c < state.cols; c++) {
      const tile = document.createElement('div');
      tile.className = 'pipe-tile';
      tile.style.width = `${tileSize}px`;
      tile.style.height = `${tileSize}px`;
      tile.id = `tile-${r}-${c}`;
      tile.innerHTML = createPipeSVG(state.grid[r][c]);

      // Allow interactive manual rotation
      tile.addEventListener('click', () => {
        if (!state.isPlaying) {
          rotateCellManual(r, c);
        }
      });

      el.gridContainer.appendChild(tile);
    }
  }

  checkBoardSolved();
}

function rotateCellManual(r, c) {
  const current = state.grid[r][c];
  const next = ((current << 1) & 0b1111) | (current >> 3);
  state.grid[r][c] = next;
  updateTile(r, c, next, true);
  
  const conflicts = countBoardConflicts();
  el.conflictBadge.textContent = conflicts;
  checkBoardSolved();
}

function createPipeSVG(mask) {
  const lines = [];
  if (mask & NORTH) lines.push('<line class="pipe-line" x1="50" y1="50" x2="50" y2="0" />');
  if (mask & EAST)  lines.push('<line class="pipe-line" x1="50" y1="50" x2="100" y2="50" />');
  if (mask & SOUTH) lines.push('<line class="pipe-line" x1="50" y1="50" x2="50" y2="100" />');
  if (mask & WEST)  lines.push('<line class="pipe-line" x1="50" y1="50" x2="0" y2="50" />');

  return `
    <svg class="pipe-svg" viewBox="0 0 100 100">
      ${lines.join('')}
      <circle class="pipe-hub" cx="50" cy="50" r="14" />
    </svg>
  `;
}

function updateTile(r, c, mask, highlight = false) {
  const tile = document.getElementById(`tile-${r}-${c}`);
  if (!tile) return;
  tile.innerHTML = createPipeSVG(mask);
  if (highlight) {
    tile.classList.add('highlight');
    setTimeout(() => tile.classList.remove('highlight'), Math.min(300, state.speed * 0.8));
  }
}

// Client-side conflict counter for real-time responsiveness
function countBoardConflicts() {
  let conflicts = 0;
  for (let r = 0; r < state.rows; r++) {
    for (let c = 0; c < state.cols; c++) {
      const mask = state.grid[r][c];
      for (const d of DIRECTIONS) {
        if (mask & d) {
          const [dr, dc] = DELTAS[d];
          const nr = r + dr;
          const nc = c + dc;
          if (nr < 0 || nr >= state.rows || nc < 0 || nc >= state.cols) {
            conflicts++;
          } else {
            const neighborMask = state.grid[nr][nc];
            if (!(neighborMask & OPPOSITE[d])) {
              conflicts++;
            }
          }
        }
      }
    }
  }
  return conflicts;
}

// ==========================================
// 4. AI Solver & Playback Execution
// ==========================================
async function onStartSolve() {
  const algo = state.selectedAlgo;
  el.btnSolve.disabled = true;
  setStatus('Solving...', 'solving');
  el.stepLog.innerHTML = `<div>Running [${algo.toUpperCase()}] solver on backend...</div>`;

  try {
    const res = await fetch('/api/solve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        algorithm: algo,
        grid: state.initialGrid
      })
    });
    const result = await res.json();

    if (!result.success) {
      setStatus('Unsolvable', 'unsolvable');
      el.stepLog.innerHTML = '<div>No valid solution found for this board configuration.</div>';
      el.btnSolve.disabled = false;
      return;
    }

    // Update HUD Statistics
    el.statTime.textContent = `${result.time_ms.toFixed(2)} ms`;
    el.statMemory.textContent = `${result.memory_kb.toFixed(2)} KB`;
    el.statNodes.textContent = result.nodes_explored.toLocaleString();
    el.statSteps.textContent = `0 / ${result.steps.length}`;

    state.steps = result.steps;
    state.currentStepIndex = -1;

    // Setup Step Scrubber
    el.stepScrubber.max = result.steps.length;
    el.stepScrubber.value = 0;
    el.stepScrubber.disabled = false;
    updateScrubberDisplay(0, result.steps.length);

    setStatus('Solved', 'solved');
    el.stepLog.innerHTML = `<div>Solution found with ${result.steps.length} steps. Playing animation...</div>`;

    // Enable navigation buttons
    el.btnStart.disabled = true;
    el.btnPrev.disabled = true;
    el.btnPlay.disabled = false;
    el.btnNext.disabled = false;
    el.btnEnd.disabled = false;

    // Adapt animation speed if trajectory is large
    if (result.steps.length > 400) {
      state.speed = 35;
    } else if (result.steps.length > 100) {
      state.speed = 80;
    } else {
      state.speed = 150;
    }

    togglePlay();

  } catch (err) {
    console.error('Solve error:', err);
    setStatus('Error', 'unsolvable');
    el.btnSolve.disabled = false;
  }
}

// Step Playback Engine
function stepForward() {
  if (state.currentStepIndex + 1 >= state.steps.length) {
    stopPlay();
    checkBoardSolved();
    return;
  }

  state.currentStepIndex++;
  const step = state.steps[state.currentStepIndex];
  state.grid[step.r][step.c] = step.new_mask;
  updateTile(step.r, step.c, step.new_mask, true);

  updatePlaybackState();
  logStep(step);

  if (state.currentStepIndex + 1 >= state.steps.length) {
    stopPlay();
    checkBoardSolved();
  }
}

function stepBackward() {
  if (state.currentStepIndex < 0) return;

  const step = state.steps[state.currentStepIndex];
  state.grid[step.r][step.c] = step.old_mask;
  updateTile(step.r, step.c, step.old_mask, true);

  state.currentStepIndex--;
  updatePlaybackState();
  removeConnectedClasses();
}

function jumpToStart() {
  stopPlay();
  scrubToStep(0);
}

function jumpToEnd() {
  stopPlay();
  scrubToStep(state.steps.length);
}

function scrubToStep(targetStep) {
  // Reconstruct board from initialGrid up to targetStep
  state.grid = state.initialGrid.map(row => [...row]);
  
  const limit = Math.min(targetStep, state.steps.length);
  for (let i = 0; i < limit; i++) {
    const s = state.steps[i];
    state.grid[s.r][s.c] = s.new_mask;
  }

  state.currentStepIndex = limit - 1;

  // Re-render all tiles
  for (let r = 0; r < state.rows; r++) {
    for (let c = 0; c < state.cols; c++) {
      updateTile(r, c, state.grid[r][c], false);
    }
  }

  updatePlaybackState();

  if (limit >= state.steps.length && state.steps.length > 0) {
    checkBoardSolved();
  } else {
    removeConnectedClasses();
  }
}

function updatePlaybackState() {
  const current = state.currentStepIndex + 1;
  const total = state.steps.length;

  el.stepScrubber.value = current;
  updateScrubberDisplay(current, total);

  el.statSteps.textContent = `${current} / ${total}`;
  el.conflictBadge.textContent = countBoardConflicts();

  el.btnStart.disabled = current <= 0;
  el.btnPrev.disabled = current <= 0;
  el.btnNext.disabled = current >= total;
  el.btnEnd.disabled = current >= total;
}

function updateScrubberDisplay(current, total) {
  el.scrubberLabel.textContent = `Step ${current} / ${total}`;
  const pct = total > 0 ? Math.round((current / total) * 100) : 0;
  el.scrubberPct.textContent = `${pct}%`;
}

function togglePlay() {
  if (state.isPlaying) {
    stopPlay();
  } else {
    if (state.currentStepIndex + 1 >= state.steps.length) {
      scrubToStep(0);
    }
    state.isPlaying = true;
    el.btnPlay.textContent = '⏸ Pause';
    el.btnPlay.className = 'control-btn';
    state.timerId = setInterval(stepForward, state.speed);
  }
}

function stopPlay() {
  state.isPlaying = false;
  clearInterval(state.timerId);
  el.btnPlay.textContent = '▶ Auto Play';
  el.btnPlay.className = 'control-btn-primary';
}

function resetBoard() {
  stopPlay();
  state.grid = state.initialGrid.map(row => [...row]);
  state.currentStepIndex = -1;
  renderGrid();
  removeConnectedClasses();

  el.conflictBadge.textContent = countBoardConflicts();
  el.statSteps.textContent = `0 / ${state.steps.length}`;
  el.stepScrubber.value = 0;
  updateScrubberDisplay(0, state.steps.length);

  el.btnStart.disabled = true;
  el.btnPrev.disabled = true;
  el.btnNext.disabled = state.steps.length === 0;
  el.btnEnd.disabled = state.steps.length === 0;
  el.btnSolve.disabled = false;
  setStatus('Ready', 'idle');
}

function logStep(step) {
  const line = document.createElement('div');
  line.textContent = `[Step ${step.step}] Cell (${step.r}, ${step.c}): Mask ${step.old_mask} → ${step.new_mask}`;
  el.stepLog.appendChild(line);
  el.stepLog.scrollTop = el.stepLog.scrollHeight;
}

function checkBoardSolved() {
  const conflicts = countBoardConflicts();
  el.conflictBadge.textContent = conflicts;
  if (conflicts === 0) {
    for (let r = 0; r < state.rows; r++) {
      for (let c = 0; c < state.cols; c++) {
        const tile = document.getElementById(`tile-${r}-${c}`);
        if (tile) tile.classList.add('connected');
      }
    }
    setStatus('Solved', 'solved');
  }
}

function removeConnectedClasses() {
  document.querySelectorAll('.pipe-tile.connected').forEach(el => el.classList.remove('connected'));
}

// ==========================================
// 5. Compare Both Algorithms (Head-to-Head)
// ==========================================
async function onCompareBoth() {
  el.btnCompare.disabled = true;
  el.btnCompare.textContent = '⏳ Comparing...';
  setStatus('Comparing...', 'solving');

  try {
    const res = await fetch('/api/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ grid: state.initialGrid })
    });
    const data = await res.json();

    if (!data.success) {
      alert('One of the algorithms failed to find a solution.');
      return;
    }

    // Populate Comparison Card
    el.compLevelName.textContent = `(${state.rows}x${state.cols} - ${state.currentFilename || 'Map'})`;
    
    // Time
    el.compDfsTime.textContent = `${data.dfs.time_ms.toFixed(2)} ms`;
    el.compAstarTime.textContent = `${data.astar.time_ms.toFixed(2)} ms`;

    // RAM
    el.compDfsRam.textContent = `${data.dfs.memory_kb.toFixed(2)} KB`;
    el.compAstarRam.textContent = `${data.astar.memory_kb.toFixed(2)} KB`;

    // Nodes
    el.compDfsNodes.textContent = data.dfs.nodes_explored.toLocaleString();
    el.compAstarNodes.textContent = data.astar.nodes_explored.toLocaleString();

    // Steps
    el.compDfsSteps.textContent = data.dfs.steps_count;
    el.compAstarSteps.textContent = data.astar.steps_count;

    // Show Card with animation
    el.comparisonCard.classList.remove('hidden');
    el.comparisonCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    setStatus('Solved', 'solved');

  } catch (err) {
    console.error('Compare error:', err);
    alert('Error during algorithm comparison.');
  } finally {
    el.btnCompare.disabled = false;
    el.btnCompare.textContent = '⚡ Compare Both';
  }
}
