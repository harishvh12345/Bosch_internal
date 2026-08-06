import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, Router } from '@angular/router';

interface Task {
  id: string;
  title: string;
  type: string;
  content: string;
  duration_minutes: number;
  simulation_id: string | null;
  quiz_id: string | null;
  status: string;
}

interface Topic {
  id: string;
  title: string;
  description: string;
  tasks: Task[];
}

interface ModuleDetail {
  id: string;
  title: string;
  description: string;
  status: string;
  difficulty: string;
  topics: Topic[];
}

interface QuizQuestion {
  id: string;
  question_text: string;
  question_type: string;
  options: string[] | null;
}

interface Quiz {
  id: string;
  title: string;
  difficulty: string;
  questions: QuizQuestion[];
}

interface QuizResult {
  score: number;
  correct_answers: Record<string, string>;
  explanations: Record<string, string>;
}

@Component({
  selector: 'app-curriculum-detail',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="curriculum-container animate-fade-in" *ngIf="module">
      <header class="module-header glass-panel">
        <button class="back-btn" (click)="goBack()">
          <span class="material-symbols-outlined">arrow_back</span>
        </button>
        <div class="module-info">
          <span class="badge badge-progress">{{ module.difficulty }}</span>
          <h1>{{ module.title }}</h1>
          <p>{{ module.description }}</p>
        </div>
      </header>

      <div class="curriculum-body">
        <!-- Left: Topics and Tasks list -->
        <section class="topics-column">
          <div class="topic-box glass-panel" *ngFor="let topic of module.topics">
            <h3>{{ topic.title }}</h3>
            <p class="topic-desc">{{ topic.description }}</p>
            
            <div class="tasks-list">
              <div 
                *ngFor="let task of topic.tasks" 
                class="task-row" 
                [class.active]="selectedTask?.id === task.id"
                [class.completed]="task.status === 'COMPLETED'"
                (click)="selectTask(task)"
              >
                <span class="material-symbols-outlined type-icon">
                  {{ getTaskIcon(task.type) }}
                </span>
                <div class="task-meta">
                  <h5>{{ task.title }}</h5>
                  <span class="task-duration">{{ task.duration_minutes }} mins</span>
                </div>
                <span class="material-symbols-outlined status-indicator">
                  {{ task.status === 'COMPLETED' ? 'check_circle' : 'radio_button_unchecked' }}
                </span>
              </div>
            </div>
          </div>
        </section>

        <!-- Right: Task Detail Panel -->
        <section class="detail-column glass-panel">
          <div class="task-detail-wrapper" *ngIf="selectedTask">
            <header class="detail-header">
              <div class="detail-title-box">
                <span class="material-symbols-outlined">
                  {{ getTaskIcon(selectedTask.type) }}
                </span>
                <h2>{{ selectedTask.title }}</h2>
              </div>
              <span class="badge badge-progress">{{ selectedTask.type }}</span>
            </header>

            <div class="divider"></div>

            <!-- Reading Task Content -->
            <div class="content-reading" *ngIf="selectedTask.type === 'READING' || selectedTask.type === 'LAB'">
              <div class="markdown-body" [innerHTML]="selectedTask.content"></div>
              <button 
                class="btn-primary complete-task-btn" 
                (click)="markTaskComplete(selectedTask.id)"
                *ngIf="selectedTask.status !== 'COMPLETED'"
              >
                <span>Mark as Completed</span>
                <span class="material-symbols-outlined">check_circle</span>
              </button>
            </div>

            <!-- Simulation Task Link -->
            <div class="content-simulation" *ngIf="selectedTask.type === 'SIMULATION'">
              <p>This topic includes a hands-on modeling challenge using MATLAB Simulink.</p>
              <div class="sim-card glass-panel">
                <span class="material-symbols-outlined sim-icon">developer_board</span>
                <div>
                  <h4>Interactive Control Loop Testing</h4>
                  <p>Open the Simulation workspace to tune parameters and monitor signals.</p>
                </div>
              </div>
              <button class="btn-primary open-sim-btn" (click)="goToSimulations()">
                <span>Go to Simulation Tool</span>
                <span class="material-symbols-outlined">arrow_forward</span>
              </button>
            </div>

            <!-- Quiz Task Layout -->
            <div class="content-quiz" *ngIf="selectedTask.type === 'QUIZ'">
              <div *ngIf="!quizLoaded && !quizResult" class="quiz-loading">
                <button class="btn-primary" (click)="loadQuiz(selectedTask.quiz_id)">
                  <span>Load AI Quiz</span>
                  <span class="material-symbols-outlined">auto_awesome</span>
                </button>
              </div>

              <!-- Quiz active questioning -->
              <div class="quiz-box" *ngIf="quizLoaded && !quizResult">
                <h4>{{ quiz?.title }}</h4>
                <div class="quiz-question" *ngFor="let q of quiz?.questions; let i = index">
                  <p class="q-text"><strong>Q{{ i+1 }}:</strong> {{ q.question_text }}</p>
                  
                  <!-- MCQ options -->
                  <div class="q-options" *ngIf="q.question_type === 'MCQ'">
                    <label class="option-label" *ngFor="let opt of q.options">
                      <input 
                        type="radio" 
                        [name]="'q_' + q.id" 
                        [value]="opt" 
                        [(ngModel)]="quizAnswers[q.id]"
                      >
                      <span>{{ opt }}</span>
                    </label>
                  </div>

                  <!-- Coding / Text inputs -->
                  <div class="q-input" *ngIf="q.question_type !== 'MCQ'">
                    <textarea 
                      [(ngModel)]="quizAnswers[q.id]" 
                      class="form-input text-answer-field"
                      placeholder="Type your answer, command line, or code here..."
                      rows="3"
                    ></textarea>
                  </div>
                </div>

                <button class="btn-primary submit-quiz-btn" (click)="submitQuiz()">
                  <span>Submit Answers</span>
                  <span class="material-symbols-outlined">send</span>
                </button>
              </div>

              <!-- Quiz result details -->
              <div class="quiz-result-panel" *ngIf="quizResult">
                <div class="score-card glass-panel" [class.pass]="quizResult.score >= 70">
                  <span class="material-symbols-outlined score-icon">
                    {{ quizResult.score >= 70 ? 'emoji_events' : 'error' }}
                  </span>
                  <div>
                    <h3>Quiz Score: {{ quizResult.score }}%</h3>
                    <p>{{ quizResult.score >= 70 ? 'Excellent! You passed the topic assessment.' : 'You scored below passing rate. Tweak and review reading logs before retrying.' }}</p>
                  </div>
                </div>

                <div class="questions-review">
                  <div class="review-item glass-panel" *ngFor="let q of quiz?.questions; let idx = index">
                    <p class="review-q"><strong>Q{{ idx+1 }}:</strong> {{ q.question_text }}</p>
                    <p class="user-ans"><strong>Your Answer:</strong> {{ quizAnswers[q.id] || 'Skipped' }}</p>
                    <p class="correct-ans"><strong>Expected Answer:</strong> {{ quizResult.correct_answers[q.id] }}</p>
                    <div class="explanation-box">
                      <p><strong>Explanation:</strong> {{ quizResult.explanations[q.id] }}</p>
                    </div>
                  </div>
                </div>

                <button class="btn-primary retry-btn" (click)="resetQuiz()" *ngIf="quizResult.score < 70">
                  <span>Retry Quiz</span>
                  <span class="material-symbols-outlined">refresh</span>
                </button>
              </div>
            </div>
          </div>

          <div class="task-detail-empty" *ngIf="!selectedTask">
            <span class="material-symbols-outlined select-icon">touch_app</span>
            <p>Select a learning task on the left column to display details and begin training.</p>
          </div>
        </section>
      </div>
    </div>
  `,
  styles: [`
    .curriculum-container {
      max-width: 1400px;
      margin: 0 auto;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 2rem;
    }

    .module-header {
      display: flex;
      align-items: center;
      gap: 1.5rem;
    }

    .back-btn {
      background: none;
      border: none;
      color: var(--text-secondary);
      cursor: pointer;
      display: flex;
      align-items: center;
      padding: 0.5rem;
      border-radius: 50%;
      transition: var(--transition-smooth);
    }

    .back-btn:hover {
      color: var(--text-primary);
      background: rgba(255, 255, 255, 0.05);
    }

    .module-info h1 {
      font-size: 2rem;
      margin: 0.25rem 0;
    }

    .module-info p {
      color: var(--text-secondary);
    }

    .curriculum-body {
      display: grid;
      grid-template-columns: 1fr 1.3fr;
      gap: 2rem;
      align-items: start;
    }

    .topics-column {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .topic-box h3 {
      font-size: 1.25rem;
      margin-bottom: 0.25rem;
    }

    .topic-desc {
      color: var(--text-secondary);
      font-size: 0.85rem;
      margin-bottom: 1.25rem;
    }

    .tasks-list {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .task-row {
      display: flex;
      align-items: center;
      gap: 1rem;
      padding: 0.85rem 1rem;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--glass-border);
      cursor: pointer;
      transition: var(--transition-smooth);
    }

    .task-row:hover {
      background: rgba(255, 255, 255, 0.04);
      border-color: rgba(0, 124, 190, 0.3);
    }

    .task-row.active {
      background: rgba(0, 124, 190, 0.1);
      border-color: var(--color-primary);
    }

    .task-row.completed .status-indicator {
      color: var(--color-success);
    }

    .type-icon {
      color: var(--text-muted);
    }

    .task-row.active .type-icon {
      color: var(--color-primary);
    }

    .task-meta {
      flex-grow: 1;
    }

    .task-meta h5 {
      font-size: 0.95rem;
      margin-bottom: 0.15rem;
    }

    .task-duration {
      font-size: 0.75rem;
      color: var(--text-muted);
    }

    .status-indicator {
      font-size: 20px;
      color: var(--text-muted);
    }

    /* Detail Column Styles */
    .detail-column {
      min-height: 500px;
      position: sticky;
      top: 2rem;
    }

    .detail-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .detail-title-box {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    .divider {
      height: 1px;
      background: var(--glass-border);
      margin: 1.5rem 0;
    }

    .markdown-body {
      color: var(--text-secondary);
      line-height: 1.6;
      margin-bottom: 2rem;
      white-space: pre-wrap;
    }

    .complete-task-btn, .open-sim-btn, .submit-quiz-btn {
      width: 100%;
      justify-content: center;
    }

    .sim-card {
      display: flex;
      align-items: center;
      gap: 1.25rem;
      padding: 1.5rem;
      margin: 1.5rem 0;
    }

    .sim-icon {
      font-size: 42px;
      color: var(--color-accent);
    }

    /* Quiz Taker Styles */
    .quiz-loading {
      text-align: center;
      padding: 3rem;
    }

    .quiz-box {
      display: flex;
      flex-direction: column;
      gap: 2rem;
    }

    .quiz-question {
      padding: 1.25rem;
      background: rgba(255, 255, 255, 0.01);
      border: 1px solid var(--glass-border);
      border-radius: 8px;
    }

    .q-text {
      font-size: 1rem;
      margin-bottom: 1rem;
    }

    .q-options {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .option-label {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      cursor: pointer;
      padding: 0.5rem;
      border-radius: 6px;
      transition: var(--transition-smooth);
    }

    .option-label:hover {
      background: rgba(255, 255, 255, 0.03);
    }

    .text-answer-field {
      width: 100%;
      resize: none;
    }

    .quiz-result-panel {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .score-card {
      display: flex;
      align-items: center;
      gap: 1.25rem;
      padding: 1.5rem;
      border-left: 4px solid var(--color-danger);
    }

    .score-card.pass {
      border-left-color: var(--color-success);
    }

    .score-icon {
      font-size: 48px;
      color: var(--color-danger);
    }

    .score-card.pass .score-icon {
      color: var(--color-success);
    }

    .questions-review {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .review-item {
      padding: 1.25rem;
    }

    .review-q {
      margin-bottom: 0.5rem;
    }

    .user-ans {
      color: var(--text-secondary);
      font-size: 0.9rem;
    }

    .correct-ans {
      color: var(--color-success);
      font-size: 0.9rem;
      margin-bottom: 0.5rem;
    }

    .explanation-box {
      background: rgba(255, 255, 255, 0.02);
      padding: 0.75rem;
      border-radius: 6px;
      font-size: 0.85rem;
      border: 1px solid var(--glass-border);
    }

    .retry-btn {
      width: 100%;
      justify-content: center;
    }

    .task-detail-empty {
      text-align: center;
      padding: 5rem;
      color: var(--text-muted);
    }

    .select-icon {
      font-size: 48px;
      margin-bottom: 1rem;
    }
  `]
})
export class CurriculumDetailComponent implements OnInit {
  module: ModuleDetail | null = null;
  selectedTask: Task | null = null;
  
  // Quiz states
  quizLoaded = false;
  quiz: Quiz | null = null;
  quizAnswers: Record<string, string> = {};
  quizResult: QuizResult | null = null;

  private http = inject(HttpClient);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private backendUrl = 'http://localhost:8000/api/v1';

  ngOnInit(): void {
    this.loadModule();
  }

  loadModule(): void {
    const moduleId = this.route.snapshot.paramMap.get('moduleId');
    if (!moduleId) return;

    this.http.get<ModuleDetail>(`${this.backendUrl}/learning/modules/${moduleId}`).subscribe({
      next: (res) => this.module = res,
      error: () => {}
    });
  }

  selectTask(task: Task): void {
    this.selectedTask = task;
    // Reset quiz state when switching tasks
    this.quizLoaded = false;
    this.quiz = null;
    this.quizAnswers = {};
    this.quizResult = null;
  }

  getTaskIcon(type: string): string {
    switch (type) {
      case 'READING': return 'menu_book';
      case 'LAB': return 'terminal';
      case 'SIMULATION': return 'developer_board';
      case 'QUIZ': return 'quiz';
      default: return 'help';
    }
  }

  markTaskComplete(taskId: string): void {
    this.http.put<Task>(`${this.backendUrl}/learning/tasks/${taskId}/status`, { status: 'COMPLETED' }).subscribe({
      next: (updatedTask) => {
        if (this.selectedTask && this.selectedTask.id === taskId) {
          this.selectedTask.status = 'COMPLETED';
        }
        // Reload parent module status
        this.loadModule();
      },
      error: () => {}
    });
  }

  loadQuiz(quizId: string | null): void {
    if (!quizId) return;
    this.http.get<Quiz>(`${this.backendUrl}/quizzes/${quizId}`).subscribe({
      next: (res) => {
        this.quiz = res;
        this.quizLoaded = true;
      },
      error: () => {}
    });
  }

  submitQuiz(): void {
    if (!this.selectedTask || !this.selectedTask.quiz_id) return;
    
    this.http.post<QuizResult>(`${this.backendUrl}/quizzes/${this.selectedTask.quiz_id}/submit`, {
      answers: this.quizAnswers
    }).subscribe({
      next: (res) => {
        this.quizResult = res;
        if (res.score >= 70 && this.selectedTask) {
          // Completed task
          this.markTaskComplete(this.selectedTask.id);
        }
      },
      error: () => {}
    });
  }

  resetQuiz(): void {
    this.quizResult = null;
    this.quizAnswers = {};
  }

  goToSimulations(): void {
    this.router.navigate(['/simulations']);
  }

  goBack(): void {
    this.router.navigate(['/dashboard']);
  }
}
