import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Subscription, interval, startWith, switchMap, takeWhile } from 'rxjs';

interface SimulationModel {
  id: string;
  name: string;
  model_file: string;
  description: string;
}

interface SimulationRun {
  id: string;
  simulation_id: string;
  parameters: Record<string, any>;
  status: string;
  logs: string;
  result_images: string[];
  execution_time_seconds: number;
  created_at: string;
  simulation: SimulationModel;
}

@Component({
  selector: 'app-simulation-runner',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="sim-runner-container animate-fade-in">
      <header class="page-header">
        <h1>MATLAB Simulink Integration Workspace</h1>
        <p>Run control loop simulations via Model Context Protocol (MCP) clients.</p>
      </header>

      <div class="workspace-grid">
        <!-- Left: Model Select & Inputs -->
        <section class="controls-column glass-panel">
          <h3>Simulation Model Selection</h3>
          <div class="models-picker">
            <div 
              *ngFor="let m of models" 
              class="model-picker-item"
              [class.active]="selectedModel?.id === m.id"
              (click)="selectModel(m)"
            >
              <div class="model-picker-header">
                <span class="material-symbols-outlined">developer_board</span>
                <h4>{{ m.name }}</h4>
              </div>
              <p class="model-file-tag">{{ m.model_file }}</p>
              <p class="model-picker-desc">{{ m.description }}</p>
            </div>
          </div>

          <div class="divider" *ngIf="selectedModel"></div>

          <!-- Parameter Forms -->
          <div class="parameter-form" *ngIf="selectedModel">
            <h3>Configure Signal Inputs</h3>
            <p class="form-desc">Tune workspace variables before compiling targets.</p>

            <!-- PID parameters -->
            <div *ngIf="selectedModel.name === 'PID Control'" class="params-group">
              <div class="form-group">
                <label>Proportional Gain (Kp)</label>
                <input type="number" [(ngModel)]="params['Kp']" class="form-input" step="0.1" min="0.1">
              </div>
              <div class="form-group">
                <label>Integral Gain (Ki)</label>
                <input type="number" [(ngModel)]="params['Ki']" class="form-input" step="0.05" min="0.0">
              </div>
              <div class="form-group">
                <label>Derivative Gain (Kd)</label>
                <input type="number" [(ngModel)]="params['Kd']" class="form-input" step="0.05" min="0.0">
              </div>
            </div>

            <!-- CAN parameters -->
            <div *ngIf="selectedModel.name === 'CAN Bus'" class="params-group">
              <div class="form-group">
                <label>Baud Rate (bps)</label>
                <select [(ngModel)]="params['baud_rate']" class="form-input">
                  <option [value]="250000">250 Kbps (Low Speed)</option>
                  <option [value]="500000">500 Kbps (Standard Speed)</option>
                  <option [value]="1000000">1 Mbps (High Speed)</option>
                </select>
              </div>
              <div class="form-group">
                <label>Channel Noise Ratio (0.0 to 1.0)</label>
                <input type="number" [(ngModel)]="params['noise_ratio']" class="form-input" step="0.05" min="0" max="1">
              </div>
            </div>

            <!-- ECU parameters -->
            <div *ngIf="selectedModel.name === 'ECU Engine'" class="params-group">
              <div class="form-group">
                <label>Throttle Actuator Angle (Degrees)</label>
                <input type="number" [(ngModel)]="params['throttle_position']" class="form-input" min="0" max="90">
              </div>
            </div>

            <button class="btn-primary trigger-btn" (click)="triggerSimulation()" [disabled]="running">
              <span>{{ running ? 'Compiling & Simulating...' : 'Execute Telemetry' }}</span>
              <span class="material-symbols-outlined">play_arrow</span>
            </button>
          </div>
        </section>

        <!-- Right: Real-time status console, Graphs, AI reports -->
        <section class="outputs-column glass-panel">
          <div class="results-wrapper" *ngIf="activeRun">
            <header class="results-header">
              <h3>Simulation Execution Output</h3>
              <span class="badge" [class.badge-completed]="activeRun.status === 'COMPLETED'" [class.badge-progress]="activeRun.status === 'RUNNING' || activeRun.status === 'PENDING'">
                {{ activeRun.status }}
              </span>
            </header>

            <!-- Loading Spree -->
            <div class="queue-status-box" *ngIf="activeRun.status === 'PENDING' || activeRun.status === 'RUNNING'">
              <div class="spinner-container">
                <div class="loading-ring"></div>
                <p>Status: {{ activeRun.status }}</p>
                <p class="small-desc">Connecting to MATLAB server, loading slx model, and parsing variables...</p>
              </div>
            </div>

            <!-- Complete Results Display -->
            <div class="completed-results" *ngIf="activeRun.status === 'COMPLETED'">
              <!-- Output plot rendering -->
              <div class="plot-container glass-panel" *ngIf="activeRun.result_images && activeRun.result_images.length > 0">
                <img [src]="getPlotUrl(activeRun.id)" alt="Simulation Graph" class="telemetry-plot">
              </div>

              <!-- Compilation telemetry metadata -->
              <div class="metrics-row">
                <div class="metric-card">
                  <span class="label">Solver Solver Engine</span>
                  <span class="val">ode45 (RK)</span>
                </div>
                <div class="metric-card">
                  <span class="label">Total Execution Time</span>
                  <span class="val">{{ activeRun.execution_time_seconds }}s</span>
                </div>
              </div>

              <!-- Terminal console log -->
              <div class="terminal-box">
                <div class="terminal-header">
                  <span class="dot red"></span>
                  <span class="dot yellow"></span>
                  <span class="dot green"></span>
                  <span class="term-title">MATLAB CLI Core Terminal</span>
                </div>
                <pre class="terminal-logs">{{ activeRun.logs }}</pre>
              </div>
            </div>
          </div>

          <div class="results-empty" *ngIf="!activeRun">
            <span class="material-symbols-outlined placeholder-icon">terminal</span>
            <p>Ready to compile. Trigger a simulation run to load telemetry output here.</p>
          </div>
        </section>
      </div>

      <!-- History Table -->
      <section class="history-section glass-panel">
        <h3>Simulation Runs History log</h3>
        <div class="table-container" *ngIf="history.length > 0">
          <table class="history-table">
            <thead>
              <tr>
                <th>Executed At</th>
                <th>Model</th>
                <th>Status</th>
                <th>Duration</th>
                <th>Parameters Configuration</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let run of history">
                <td>{{ run.created_at | date:'medium' }}</td>
                <td>{{ run.simulation.name }}</td>
                <td>
                  <span class="badge" [class.badge-completed]="run.status === 'COMPLETED'" [class.badge-progress]="run.status === 'RUNNING' || run.status === 'PENDING'">
                    {{ run.status }}
                  </span>
                </td>
                <td>{{ run.execution_time_seconds }}s</td>
                <td class="params-cell">{{ formatParams(run.parameters) }}</td>
                <td>
                  <button class="view-run-btn" (click)="viewHistoryRun(run)">
                    <span class="material-symbols-outlined">visibility</span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="history-empty" *ngIf="history.length === 0">
          <p>No previous logs compiled. Runs executed will display in this audit log.</p>
        </div>
      </section>
    </div>
  `,
  styles: [`
    .sim-runner-container {
      max-width: 1400px;
      margin: 0 auto;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 2rem;
    }

    .page-header h1 {
      font-size: 2.25rem;
      margin-bottom: 0.25rem;
    }

    .page-header p {
      color: var(--text-secondary);
    }

    .workspace-grid {
      display: grid;
      grid-template-columns: 1fr 1.3fr;
      gap: 2rem;
      align-items: start;
    }

    .controls-column, .outputs-column {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .models-picker {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .model-picker-item {
      background: rgba(255, 255, 255, 0.01);
      border: 1px solid var(--glass-border);
      border-radius: 8px;
      padding: 1rem;
      cursor: pointer;
      transition: var(--transition-smooth);
    }

    .model-picker-item:hover {
      border-color: rgba(0, 124, 190, 0.3);
      background: rgba(255, 255, 255, 0.03);
    }

    .model-picker-item.active {
      background: rgba(0, 124, 190, 0.1);
      border-color: var(--color-primary);
    }

    .model-picker-header {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 0.25rem;
    }

    .model-file-tag {
      font-size: 0.7rem;
      color: var(--color-accent);
      text-transform: uppercase;
      font-family: var(--font-title);
      margin-bottom: 0.5rem;
    }

    .model-picker-desc {
      font-size: 0.8rem;
      color: var(--text-secondary);
    }

    .divider {
      height: 1px;
      background: var(--glass-border);
    }

    .form-desc {
      color: var(--text-muted);
      font-size: 0.8rem;
      margin-bottom: 1rem;
    }

    .params-group {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      margin-bottom: 1.5rem;
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
    }

    .form-group label {
      font-size: 0.85rem;
      color: var(--text-secondary);
      font-weight: 500;
    }

    .trigger-btn {
      width: 100%;
      justify-content: center;
    }

    /* Outputs Panel */
    .outputs-column {
      min-height: 550px;
    }

    .results-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .queue-status-box {
      display: flex;
      justify-content: center;
      padding: 6rem 0;
      text-align: center;
    }

    .spinner-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1rem;
    }

    .loading-ring {
      width: 48px;
      height: 48px;
      border: 4px solid var(--bg-tertiary);
      border-top-color: var(--color-primary);
      border-radius: 50%;
      animation: spin 1s infinite linear;
    }

    @keyframes spin {
      100% { transform: rotate(360deg); }
    }

    .small-desc {
      font-size: 0.8rem;
      color: var(--text-muted);
      max-width: 300px;
    }

    .plot-container {
      padding: 0.5rem;
      background: #000;
      border-radius: var(--border-radius);
      margin-bottom: 1rem;
      display: flex;
      justify-content: center;
      overflow: hidden;
    }

    .telemetry-plot {
      max-width: 100%;
      height: auto;
      border-radius: 8px;
    }

    .metrics-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
      margin-bottom: 1rem;
    }

    .metric-card {
      background: rgba(255, 255, 255, 0.01);
      border: 1px solid var(--glass-border);
      border-radius: 8px;
      padding: 0.75rem 1rem;
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }

    .metric-card .label {
      font-size: 0.75rem;
      color: var(--text-muted);
    }

    .metric-card .val {
      font-size: 1.1rem;
      font-weight: 600;
    }

    .terminal-box {
      background: #060913;
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 8px;
      overflow: hidden;
    }

    .terminal-header {
      background: #111827;
      padding: 0.5rem 1rem;
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }

    .terminal-header .dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
    }

    .dot.red { background: #ff5f56; }
    .dot.yellow { background: #ffbd2e; }
    .dot.green { background: #27c93f; }

    .term-title {
      font-size: 0.7rem;
      color: var(--text-secondary);
      font-family: monospace;
      margin-left: 0.5rem;
    }

    .terminal-logs {
      padding: 1rem;
      font-family: monospace;
      font-size: 0.85rem;
      color: #38bdf8;
      max-height: 250px;
      overflow-y: auto;
      white-space: pre-wrap;
    }

    .results-empty {
      text-align: center;
      padding: 8rem 0;
      color: var(--text-muted);
    }

    .placeholder-icon {
      font-size: 54px;
      margin-bottom: 1rem;
    }

    /* History Table Styles */
    .history-section {
      margin-top: 1rem;
    }

    .table-container {
      width: 100%;
      overflow-x: auto;
      margin-top: 1rem;
    }

    .history-table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }

    .history-table th, .history-table td {
      padding: 0.85rem 1rem;
      border-bottom: 1px solid var(--glass-border);
    }

    .history-table th {
      font-family: var(--font-title);
      font-size: 0.9rem;
      color: var(--text-secondary);
    }

    .params-cell {
      font-family: monospace;
      font-size: 0.8rem;
      color: var(--color-accent);
    }

    .view-run-btn {
      background: none;
      border: none;
      color: var(--text-secondary);
      cursor: pointer;
      display: flex;
      align-items: center;
      padding: 0.25rem;
      border-radius: 4px;
      transition: var(--transition-smooth);
    }

    .view-run-btn:hover {
      color: var(--color-primary);
      background: rgba(255, 255, 255, 0.05);
    }

    .history-empty {
      text-align: center;
      padding: 2rem;
      color: var(--text-muted);
    }
  `]
})
export class SimulationRunnerComponent implements OnInit, OnDestroy {
  models: SimulationModel[] = [];
  selectedModel: SimulationModel | null = null;
  params: Record<string, any> = {};
  
  activeRun: SimulationRun | null = null;
  history: SimulationRun[] = [];
  running = false;

  private pollingSub: Subscription | null = null;
  private http = inject(HttpClient);
  private backendUrl = 'http://localhost:8000/api/v1';

  ngOnInit(): void {
    this.loadModels();
    this.loadHistory();
  }

  ngOnDestroy(): void {
    this.stopPolling();
  }

  loadModels(): void {
    this.http.get<SimulationModel[]>(`${this.backendUrl}/simulations`).subscribe({
      next: (res) => {
        this.models = res;
        if (res.length > 0) {
          this.selectModel(res[0]);
        }
      },
      error: () => {}
    });
  }

  loadHistory(): void {
    this.http.get<SimulationRun[]>(`${this.backendUrl}/simulations/runs`).subscribe({
      next: (res) => this.history = res,
      error: () => {}
    });
  }

  selectModel(model: SimulationModel): void {
    this.selectedModel = model;
    this.activeRun = null;
    
    // Set default parameters based on simulation model
    if (model.name === 'PID Control') {
      this.params = { Kp: 2.5, Ki: 0.2, Kd: 0.1 };
    } else if (model.name === 'CAN Bus') {
      this.params = { baud_rate: 500000, noise_ratio: 0.05 };
    } else {
      this.params = { throttle_position: 45.0 };
    }
  }

  triggerSimulation(): void {
    if (!this.selectedModel) return;
    this.running = true;

    this.http.post<SimulationRun>(`${this.backendUrl}/simulations/run/${this.selectedModel.id}`, {
      parameters: this.params
    }).subscribe({
      next: (run) => {
        this.activeRun = run;
        this.startPolling(run.id);
      },
      error: () => {
        this.running = false;
      }
    });
  }

  startPolling(runId: string): void {
    this.stopPolling();
    
    this.pollingSub = interval(1500).pipe(
      switchMap(() => this.http.get<SimulationRun>(`${this.backendUrl}/simulations/runs/${runId}`)),
      takeWhile(run => run.status === 'PENDING' || run.status === 'RUNNING', true)
    ).subscribe({
      next: (run) => {
        this.activeRun = run;
        if (run.status === 'COMPLETED' || run.status === 'FAILED') {
          this.running = false;
          this.loadHistory();
        }
      },
      error: () => {
        this.running = false;
      }
    });
  }

  stopPolling(): void {
    if (this.pollingSub) {
      this.pollingSub.unsubscribe();
      this.pollingSub = null;
    }
  }

  getPlotUrl(runId: string): string {
    return `http://localhost:8000/data/simulations/${runId}.png`;
  }

  formatParams(params: Record<string, any>): string {
    return Object.entries(params).map(([k, v]) => `${k}:${v}`).join(', ');
  }

  viewHistoryRun(run: SimulationRun): void {
    this.activeRun = run;
    this.selectedModel = this.models.find(m => m.id === run.simulation_id) || null;
    this.params = { ...run.parameters };
  }
}
