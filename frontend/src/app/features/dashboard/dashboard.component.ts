import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

interface Skill {
  skill: { id: string; name: string; category: string };
  level: number;
}

interface Profile {
  id: string;
  first_name: string;
  last_name: string;
  experience_years: number;
  skills_association: Skill[];
}

interface Goal {
  id: string;
  goal_text: string;
  created_at: string;
}

interface Module {
  id: string;
  title: string;
  description: string;
  difficulty: string;
  estimated_hours: number;
  order_index: number;
  status: string;
}

interface Recommendation {
  id: string;
  rec_type: string;
  title: string;
  reasoning: string;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="dashboard-container animate-fade-in">
      <header class="dashboard-header">
        <div class="welcome">
          <h1>Welcome back, {{ profile?.first_name || 'Engineer' }}</h1>
          <p>Optimize your skills and explore automotive control simulations.</p>
        </div>
      </header>

      <!-- Main Columns -->
      <div class="dashboard-grid">
        <!-- Left: Goals & Curriculum -->
        <section class="left-section">
          <!-- Generate New Goal Card -->
          <div class="glass-panel search-card">
            <h3>Establish New Learning Goal</h3>
            <p class="section-desc">Type your learning target to generate a custom curriculum mapping topics to simulations.</p>
            <div class="goal-form">
              <div class="form-group">
                <label for="goalInput">Learning Goal</label>
                <input 
                  id="goalInput"
                  type="text" 
                  [(ngModel)]="newGoalText" 
                  placeholder="e.g., I want to learn ECU Kit, or Switch from Backend to Embedded"
                  class="form-input search-input"
                  [disabled]="generating"
                >
              </div>
              <div class="form-group">
                <label for="simInput">Simulation Focus / Target (Optional)</label>
                <input 
                  id="simInput"
                  type="text" 
                  [(ngModel)]="newSimulationFocus" 
                  placeholder="e.g., test CAN delays, evaluate engine throttle step-response tuning"
                  class="form-input search-input"
                  [disabled]="generating"
                >
              </div>
              <button 
                class="btn-primary generate-btn" 
                (click)="onGenerateGoal()" 
                [disabled]="generating || !newGoalText"
                style="margin-top: 0.5rem; width: 100%; justify-content: center;"
              >
                <span>{{ generating ? 'Generating...' : 'Build Path' }}</span>
                <span class="material-symbols-outlined">auto_awesome</span>
              </button>
            </div>
            <div class="progress-bar-loading" *ngIf="generating">
              <div class="progress-bar-fill"></div>
            </div>
          </div>

          <!-- Active Goals & Modules -->
          <div class="goals-card" *ngIf="activeGoals.length > 0">
            <div class="goals-header">
              <h3>Active Training Path</h3>
              <select class="goal-select" [(ngModel)]="selectedGoalId" (change)="onGoalChange()">
                <option *ngFor="let g of activeGoals" [value]="g.id">{{ g.goal_text }}</option>
              </select>
            </div>

            <!-- Path Progress -->
            <div class="progress-panel glass-panel" *ngIf="selectedGoalProgress !== null">
              <div class="progress-info">
                <span>Course Completion Progress</span>
                <span class="progress-pct">{{ selectedGoalProgress }}%</span>
              </div>
              <div class="progress-track">
                <div class="progress-fill" [style.width.%]="selectedGoalProgress"></div>
              </div>
            </div>

            <!-- Modules list -->
            <div class="modules-list">
              <div 
                *ngFor="let m of modules" 
                class="module-item glass-panel"
                [class.completed]="m.status === 'COMPLETED'"
                [class.in-progress]="m.status === 'IN_PROGRESS'"
                (click)="openModule(m.id)"
              >
                <div class="module-left">
                  <div class="module-num">{{ m.order_index }}</div>
                  <div class="module-meta">
                    <h4>{{ m.title }}</h4>
                    <p>{{ m.description }}</p>
                  </div>
                </div>
                <div class="module-right">
                  <span class="badge" [class.badge-completed]="m.status === 'COMPLETED'" [class.badge-progress]="m.status === 'IN_PROGRESS'" [class.badge-pending]="m.status === 'NOT_STARTED'">
                    {{ m.status.replace('_', ' ') }}
                  </span>
                  <div class="module-stats">
                    <span class="material-symbols-outlined">schedule</span>
                    <span>{{ m.estimated_hours }}h</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Right: Profile, Skills, Recommendations -->
        <section class="right-section">
          <!-- Profile Card -->
          <div class="glass-panel profile-card">
            <div class="profile-header">
              <span class="material-symbols-outlined profile-avatar">account_box</span>
              <div class="profile-meta">
                <h3>{{ profile?.first_name }} {{ profile?.last_name }}</h3>
                <p>{{ profile?.experience_years }} Years Experience</p>
              </div>
            </div>
            
            <div class="divider"></div>
            
            <div class="skills-section">
              <h4>Skill Matrix Ratings</h4>
              <div class="skills-list">
                <div class="skill-item" *ngFor="let s of profile?.skills_association">
                  <div class="skill-info">
                    <span>{{ s.skill.name }}</span>
                    <span class="skill-level">Lvl {{ s.level }}/5</span>
                  </div>
                  <div class="skill-track">
                    <div class="skill-fill" [style.width.%]="s.level * 20"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Recommendations Card -->
          <div class="glass-panel recs-card">
            <div class="recs-header">
              <h3>AI-Generated Study Advice</h3>
              <button class="refresh-recs-btn" (click)="refreshRecommendations()" title="Refresh Suggestions">
                <span class="material-symbols-outlined">refresh</span>
              </button>
            </div>
            
            <div class="recs-list" *ngIf="recommendations.length > 0">
              <div class="rec-item" *ngFor="let r of recommendations">
                <div class="rec-type-badge" [class.rec-sim]="r.rec_type === 'SIMULATION'" [class.rec-course]="r.rec_type === 'COURSE'">
                  <span class="material-symbols-outlined">
                    {{ r.rec_type === 'SIMULATION' ? 'analytics' : 'school' }}
                  </span>
                  <span>{{ r.rec_type }}</span>
                </div>
                <div class="rec-content">
                  <h5>{{ r.title }}</h5>
                  <p>{{ r.reasoning }}</p>
                </div>
              </div>
            </div>
            <div class="recs-empty" *ngIf="recommendations.length === 0">
              <span class="material-symbols-outlined">lightbulb</span>
              <p>No advice parsed. Refreshed advice suggestions will display here based on quiz scoring achievements.</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-container {
      max-width: 1400px;
      margin: 0 auto;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 2rem;
    }

    .dashboard-header h1 {
      font-size: 2.25rem;
      margin-bottom: 0.25rem;
    }

    .dashboard-header p {
      color: var(--text-secondary);
    }

    .dashboard-grid {
      display: grid;
      grid-template-columns: 1.6fr 1fr;
      gap: 2rem;
    }

    .left-section, .right-section {
      display: flex;
      flex-direction: column;
      gap: 2rem;
    }

    .search-card {
      border-radius: var(--border-radius-lg);
    }

    .search-card h3 {
      font-size: 1.4rem;
      margin-bottom: 0.5rem;
    }

    .section-desc {
      color: var(--text-secondary);
      font-size: 0.9rem;
      margin-bottom: 1.25rem;
    }

    .goal-form {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
    }

    .form-group label {
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .search-input {
      flex-grow: 1;
    }

    .progress-bar-loading {
      margin-top: 1rem;
      height: 4px;
      width: 100%;
      background: var(--bg-tertiary);
      border-radius: 2px;
      overflow: hidden;
    }

    .progress-bar-fill {
      height: 100%;
      width: 30%;
      background: var(--color-primary);
      animation: loadingAnim 1.5s infinite linear;
    }

    @keyframes loadingAnim {
      0% { transform: translateX(-100%); }
      100% { transform: translateX(330%); }
    }

    .goals-card {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .goals-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .goal-select {
      background: var(--bg-secondary);
      color: var(--text-primary);
      border: 1px solid var(--glass-border);
      padding: 0.5rem 1rem;
      border-radius: 8px;
      font-family: var(--font-title);
      font-weight: 500;
    }

    .progress-panel {
      padding: 1.25rem;
    }

    .progress-info {
      display: flex;
      justify-content: space-between;
      margin-bottom: 0.5rem;
      font-size: 0.9rem;
      font-weight: 500;
    }

    .progress-pct {
      color: var(--color-primary);
    }

    .progress-track {
      height: 8px;
      background: var(--bg-tertiary);
      border-radius: 4px;
      overflow: hidden;
    }

    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--color-primary) 0%, var(--color-accent) 100%);
      border-radius: 4px;
      transition: width 0.5s ease-out;
    }

    .modules-list {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .module-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: pointer;
      transition: var(--transition-smooth);
    }

    .module-item:hover {
      transform: translateX(4px);
    }

    .module-left {
      display: flex;
      align-items: center;
      gap: 1.25rem;
      flex-grow: 1;
    }

    .module-num {
      width: 40px;
      height: 40px;
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--glass-border);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: var(--font-title);
      font-size: 1.1rem;
      font-weight: 600;
    }

    .module-item.in-progress .module-num {
      border-color: var(--color-primary);
      color: var(--color-primary);
      background: rgba(0, 124, 190, 0.1);
    }

    .module-item.completed .module-num {
      border-color: var(--color-success);
      color: var(--color-success);
      background: rgba(0, 230, 118, 0.1);
    }

    .module-meta h4 {
      font-size: 1.1rem;
      margin-bottom: 0.25rem;
    }

    .module-meta p {
      font-size: 0.85rem;
      color: var(--text-secondary);
    }

    .module-right {
      display: flex;
      align-items: center;
      gap: 1.5rem;
    }

    .module-stats {
      display: flex;
      align-items: center;
      gap: 0.35rem;
      color: var(--text-muted);
      font-size: 0.85rem;
    }

    .module-stats span.material-symbols-outlined {
      font-size: 16px;
    }

    /* Right Section Styles */
    .profile-card {
      border-radius: var(--border-radius-lg);
    }

    .profile-header {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .profile-avatar {
      font-size: 54px;
      color: var(--color-primary);
    }

    .profile-meta h3 {
      font-size: 1.25rem;
    }

    .profile-meta p {
      font-size: 0.85rem;
      color: var(--text-secondary);
    }

    .divider {
      height: 1px;
      background: var(--glass-border);
      margin: 1.5rem 0;
    }

    .skills-section h4 {
      font-size: 0.95rem;
      text-transform: uppercase;
      letter-spacing: 0.05rem;
      color: var(--text-secondary);
      margin-bottom: 1.25rem;
    }

    .skills-list {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .skill-item {
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
    }

    .skill-info {
      display: flex;
      justify-content: space-between;
      font-size: 0.85rem;
      font-weight: 500;
    }

    .skill-level {
      color: var(--color-accent);
    }

    .skill-track {
      height: 6px;
      background: rgba(255, 255, 255, 0.03);
      border-radius: 3px;
      overflow: hidden;
    }

    .skill-fill {
      height: 100%;
      background: var(--color-primary);
      border-radius: 3px;
    }

    /* Recommendations Styles */
    .recs-card {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .recs-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .refresh-recs-btn {
      background: none;
      border: none;
      color: var(--text-secondary);
      cursor: pointer;
      display: flex;
      align-items: center;
      transition: var(--transition-smooth);
    }

    .refresh-recs-btn:hover {
      color: var(--color-primary);
      transform: rotate(180deg);
    }

    .recs-list {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .rec-item {
      display: flex;
      gap: 1rem;
      padding: 1rem;
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--glass-border);
      border-radius: 8px;
    }

    .rec-type-badge {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      font-size: 0.65rem;
      font-weight: 600;
      color: var(--color-primary);
      background: rgba(0, 124, 190, 0.1);
      width: 70px;
      height: 70px;
      border-radius: 8px;
      gap: 0.25rem;
    }

    .rec-type-badge.rec-sim {
      color: var(--color-accent);
      background: rgba(0, 240, 255, 0.1);
    }

    .rec-type-badge span.material-symbols-outlined {
      font-size: 24px;
    }

    .rec-content {
      flex-grow: 1;
    }

    .rec-content h5 {
      font-size: 0.95rem;
      margin-bottom: 0.25rem;
    }

    .rec-content p {
      font-size: 0.8rem;
      color: var(--text-secondary);
      line-height: 1.4;
    }

    .recs-empty {
      text-align: center;
      padding: 2rem;
      color: var(--text-muted);
    }

    .recs-empty span {
      font-size: 36px;
      margin-bottom: 0.5rem;
    }
  `]
})
export class DashboardComponent implements OnInit {
  profile: Profile | null = null;
  activeGoals: Goal[] = [];
  modules: Module[] = [];
  recommendations: Recommendation[] = [];
  
  newGoalText = '';
  newSimulationFocus = '';
  selectedGoalId = '';
  selectedGoalProgress: number | null = null;
  
  generating = false;
  loadingRecs = false;

  private http = inject(HttpClient);
  private router = inject(Router);
  private backendUrl = 'http://localhost:8000/api/v1';

  ngOnInit(): void {
    this.loadProfile();
    this.loadGoals();
    this.loadRecommendations();
  }

  loadProfile(): void {
    this.http.get<Profile>(`${this.backendUrl}/employees/profile`).subscribe({
      next: (res) => this.profile = res,
      error: () => {}
    });
  }

  loadGoals(): void {
    this.http.get<Goal[]>(`${this.backendUrl}/learning/goals`).subscribe({
      next: (res) => {
        this.activeGoals = res;
        if (res.length > 0) {
          this.selectedGoalId = res[0].id;
          this.onGoalChange();
        }
      },
      error: () => {}
    });
  }

  onGoalChange(): void {
    if (!this.selectedGoalId) return;
    
    // Load modules
    this.http.get<Module[]>(`${this.backendUrl}/learning/goals/${this.selectedGoalId}/modules`).subscribe({
      next: (res) => this.modules = res.sort((a, b) => a.order_index - b.order_index),
      error: () => {}
    });

    // Load progress
    this.http.get<{ percent_completed: number }>(`${this.backendUrl}/learning/goals/${this.selectedGoalId}/progress`).subscribe({
      next: (res) => this.selectedGoalProgress = Math.round(res.percent_completed),
      error: () => {}
    });
  }

  onGenerateGoal(): void {
    if (!this.newGoalText) return;
    this.generating = true;

    this.http.post<Goal>(`${this.backendUrl}/learning/goals`, {
      goal_text: this.newGoalText,
      simulation_focus: this.newSimulationFocus
    }).subscribe({
      next: (goal) => {
        this.newGoalText = '';
        this.newSimulationFocus = '';
        this.generating = false;
        this.loadGoals();
      },
      error: () => {
        this.generating = false;
      }
    });
  }

  loadRecommendations(): void {
    this.http.get<Recommendation[]>(`${this.backendUrl}/recommendations`).subscribe({
      next: (res) => this.recommendations = res,
      error: () => {}
    });
  }

  refreshRecommendations(): void {
    this.loadingRecs = true;
    this.http.post<Recommendation[]>(`${this.backendUrl}/recommendations/refresh`, {}).subscribe({
      next: (res) => {
        this.recommendations = res;
        this.loadingRecs = false;
      },
      error: () => this.loadingRecs = false
    });
  }


  openModule(moduleId: string): void {
    this.router.navigate(['/curriculum', moduleId]);
  }
}
