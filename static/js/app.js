/**
 * app.js
 * Board state management, Flask REST API client, SVG pipe rendering,
 * and step-by-step playback controller.
 */

const NORTH = 1;
const EAST = 2;
const SOUTH = 4;
const WEST = 8;

const state = {
  rows: 0,
  cols: 0,
  grid: [],
  initialGrid: [],
  steps: [],
  currentStepIndex: -1,
  isPlaying: false,
  timerId: null,
  speed: 300,
  solved: false
};

// DOM Elements
const elements = {
  gridContainer: document.getElementById('grid-container'),
  levelSelect: document.getElementById('level-select'),
  randomSize: document.getElementById('random-size'),
  btnGenerate: document.getElementById('btn-generate'),
  algoSelect: document.getElementById('algo-select'),
  btnSolve: document.getElementById('btn-solve'),
  btnPrev: document.getElementById('btn-prev'),
  btnPlay: document.getElementById('btn-play'),
  btnNext: document.getElementById('btn-next'),
  btnReset: document.getElementById('btn-reset'),
  speedSlider: document.getElementById('speed-slider'),
  speedVal: document.getElementById('speed-val'),
  levelTitle: document.getElementById('level-title'),
  boardStatus: document.getElementById('board-status'),
  statTime: document.getElementById('stat-time'),
  statMemory: document.getElementById('stat-memory'),
  statNodes: document.getElementById('stat-nodes'),
  statSteps: document.getElementById('stat-steps'),
  stepLog: document.getElementById('step-log')
};

// ==========================================
// 1. Initialization and Data Loading
// ==========================================
document.addEventListener('DOMContentLoaded', async () => {
  setupEventListeners();
  await fetchLevels();
});

function setupEventListeners() {
  elements.levelSelect.addEventListener('change', onLevelSelected);
  elements.btnGenerate.addEventListener('click', onGenerateRandom);
  elements.btnSolve.addEventListener('click', onStartSolve);
  elements.btnNext.addEventListener('click', stepForward);
  elements.btnPrev.addEventListener('click', stepBackward);
  elements.btnPlay.addEventListener('click', togglePlay);
  elements.btnReset.addEventListener('click', resetBoard);

  elements.speedSlider.addEventListener('input', (e) => {
    state.speed = parseInt(e.target.value);
    elements.speedVal.textContent = `${state.speed}ms`;
    if (state.isPlaying) {
      clearInterval(state.timerId);
      state.timerId = setInterval(stepForward, state.speed);
    }
  });
}

async function fetchLevels() {
  try {
    const res = await fetch('/api/levels');
    const data = await res.json();
    elements.levelSelect.innerHTML = '<option value="">-- Select a level --</option>';
    data.levels.forEach(lvl => {
      const opt = document.createElement('option');
      opt.value = lvl;
      opt.textContent = lvl;
      elements.levelSelect.appendChild(opt);
    });

    if (data.levels.length > 0) {
      elements.levelSelect.value = data.levels[0];
      await loadLevelFile(data.levels[0]);
    }
  } catch (err) {
    console.error('Failed to load levels list:', err);
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
    const res = await fetch('/api/load_level', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename })
    });
    const data = await res.json();
    setNewBoard(data.grid, `Level: ${filename}`);
  } catch (err) {
    console.error('Failed to load level file:', err);
  }
}

async function onGenerateRandom() {
  const size = parseInt(elements.randomSize.value);
  try {
    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ size })
    });
    const data = await res.json();
    setNewBoard(data.grid, `Random Map: ${size}x${size}`);
    elements.levelSelect.value = '';
  } catch (err) {
    console.error('Failed to generate random map:', err);
  }
}

// ==========================================
// 2. SVG Board Rendering
// ==========================================
function setNewBoard(grid, title) {
  stopPlay();
  state.rows = grid.length;
  state.cols = grid[0].length;
  state.grid = grid.map(row => [...row]);
  state.initialGrid = grid.map(row => [...row]);
  state.steps = [];
  state.currentStepIndex = -1;
  state.solved = false;

  elements.levelTitle.textContent = title;
  elements.boardStatus.textContent = 'Ready';
  elements.boardStatus.className = 'status-tag status-idle';

  elements.btnSolve.disabled = false;
  elements.btnPrev.disabled = true;
  elements.btnPlay.disabled = true;
  elements.btnNext.disabled = true;

  elements.statTime.textContent = '-- ms';
  elements.statMemory.textContent = '-- KB';
  elements.statNodes.textContent = '--';
  elements.statSteps.textContent = '0 / 0';
  elements.stepLog.innerHTML = 'Board loaded. Click "Solve Puzzle" to run AI solver.';

  renderGrid();
}

function renderGrid() {
  elements.gridContainer.innerHTML = '';
  elements.gridContainer.style.gridTemplateColumns = `repeat(${state.cols}, 60px)`;
  elements.gridContainer.style.gridTemplateRows = `repeat(${state.rows}, 60px)`;

  for (let r = 0; r < state.rows; r++) {
    for (let c = 0; c < state.cols; c++) {
      const tile = document.createElement('div');
      tile.className = 'pipe-tile';
      tile.id = `tile-${r}-${c}`;
      tile.innerHTML = createPipeSVG(state.grid[r][c]);

      // Allow interactive manual rotation by clicking
      tile.addEventListener('click', () => {
        if (!state.isPlaying) {
          rotateCellManual(r, c);
        }
      });

      elements.gridContainer.appendChild(tile);
    }
  }
}

function rotateCellManual(r, c) {
  const current = state.grid[r][c];
  const next = ((current << 1) & 0b1111) | (current >> 3);
  state.grid[r][c] = next;
  updateTile(r, c, next);
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
    setTimeout(() => tile.classList.remove('highlight'), state.speed * 0.8);
  }
}

// ==========================================
// 3. AI Solver & Step-by-Step Playback
// ==========================================
async function onStartSolve() {
  const algo = elements.algoSelect.value;
  elements.btnSolve.disabled = true;
  elements.boardStatus.textContent = 'Solving...';
  elements.boardStatus.className = 'status-tag status-solving';
  elements.stepLog.innerHTML = `Running ${algo.toUpperCase()} solver on Python backend...`;

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
      elements.boardStatus.textContent = 'Unsolvable';
      elements.boardStatus.className = 'status-tag';
      elements.stepLog.innerHTML = 'No solution found for this board configuration.';
      elements.btnSolve.disabled = false;
      return;
    }

    elements.statTime.textContent = `${result.time_ms} ms`;
    elements.statMemory.textContent = `${result.memory_kb} KB`;
    elements.statNodes.textContent = result.nodes_explored.toLocaleString();
    elements.statSteps.textContent = `0 / ${result.steps.length}`;

    state.steps = result.steps;
    state.currentStepIndex = -1;

    elements.boardStatus.textContent = 'Solved';
    elements.boardStatus.className = 'status-tag status-solved';
    elements.stepLog.innerHTML = `Solution found in ${result.steps.length} steps. Click ▶ Auto Play to visualize.`;

    elements.btnNext.disabled = false;
    elements.btnPlay.disabled = false;
    elements.btnPrev.disabled = true;

    togglePlay();

  } catch (err) {
    console.error('Solve error:', err);
    elements.boardStatus.textContent = 'System Error';
    elements.btnSolve.disabled = false;
  }
}

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

  elements.statSteps.textContent = `${state.currentStepIndex + 1} / ${state.steps.length}`;
  logStep(step);

  elements.btnPrev.disabled = false;
  if (state.currentStepIndex + 1 >= state.steps.length) {
    elements.btnNext.disabled = true;
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
  elements.statSteps.textContent = `${Math.max(0, state.currentStepIndex + 1)} / ${state.steps.length}`;

  elements.btnNext.disabled = false;
  if (state.currentStepIndex < 0) {
    elements.btnPrev.disabled = true;
  }
  removeConnectedClasses();
}

function togglePlay() {
  if (state.isPlaying) {
    stopPlay();
  } else {
    state.isPlaying = true;
    elements.btnPlay.textContent = '⏸ Pause';
    elements.btnPlay.className = 'btn btn-secondary';
    state.timerId = setInterval(stepForward, state.speed);
  }
}

function stopPlay() {
  state.isPlaying = false;
  clearInterval(state.timerId);
  elements.btnPlay.textContent = '▶ Auto Play';
  elements.btnPlay.className = 'btn btn-primary';
}

function resetBoard() {
  stopPlay();
  state.grid = state.initialGrid.map(row => [...row]);
  state.currentStepIndex = -1;
  renderGrid();
  removeConnectedClasses();
  elements.statSteps.textContent = `0 / ${state.steps.length}`;
  elements.btnNext.disabled = state.steps.length === 0;
  elements.btnPrev.disabled = true;
  elements.btnSolve.disabled = false;
  elements.boardStatus.textContent = 'Ready';
  elements.boardStatus.className = 'status-tag status-idle';
}

function logStep(step) {
  const line = document.createElement('div');
  const actionText = step.action === 'backtrack' ? 'Backtrack' : 'Place Rotation';
  line.textContent = `[Step ${step.step}] Cell (${step.r}, ${step.c}): ${actionText}`;
  elements.stepLog.appendChild(line);
  elements.stepLog.scrollTop = elements.stepLog.scrollHeight;
}

function checkBoardSolved() {
  for (let r = 0; r < state.rows; r++) {
    for (let c = 0; c < state.cols; c++) {
      const tile = document.getElementById(`tile-${r}-${c}`);
      if (tile) tile.classList.add('connected');
    }
  }
}

function removeConnectedClasses() {
  document.querySelectorAll('.pipe-tile.connected').forEach(el => el.classList.remove('connected'));
}
