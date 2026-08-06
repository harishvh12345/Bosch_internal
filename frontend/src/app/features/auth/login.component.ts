import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/auth/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="login-page">
      <div class="login-card glass-panel animate-fade-in">
        <div class="header">
          <span class="material-symbols-outlined logo">insights</span>
          <h1>BOSCH</h1>
          <p>Personalized AI Learning Platform</p>
        </div>

        <form (ngSubmit)="onSubmit()" #loginForm="ngForm" class="login-form">
          <div class="form-group">
            <label for="email">Corporate Email</label>
            <input 
              type="email" 
              id="email" 
              name="email"
              [(ngModel)]="email" 
              required 
              class="form-input"
              placeholder="username@bosch.com"
            >
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <input 
              type="password" 
              id="password" 
              name="password"
              [(ngModel)]="password" 
              required 
              class="form-input"
              placeholder="••••••••"
            >
          </div>

          <div class="error-msg" *ngIf="error">
            <span class="material-symbols-outlined error-icon">error</span>
            <span>{{ error }}</span>
          </div>

          <button type="submit" class="btn-primary submit-btn" [disabled]="loading || !loginForm.form.valid">
            <span>{{ loading ? 'Authenticating...' : 'Sign In' }}</span>
            <span class="material-symbols-outlined">login</span>
          </button>
        </form>

        <div class="divider">
          <span>Testing Accounts Seeding</span>
        </div>

        <div class="quick-logins">
          <button (click)="quickLogin('employee@bosch.com', 'employee123')" class="quick-btn">
            <span>Employee</span>
            <span class="material-symbols-outlined">engineering</span>
          </button>
          <button (click)="quickLogin('manager@bosch.com', 'manager123')" class="quick-btn">
            <span>Manager</span>
            <span class="material-symbols-outlined">groups</span>
          </button>
          <button (click)="quickLogin('admin@bosch.com', 'admin123')" class="quick-btn">
            <span>Administrator</span>
            <span class="material-symbols-outlined">admin_panel_settings</span>
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .login-page {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 96vh;
      width: 100%;
      background: radial-gradient(circle at 10% 20%, rgba(0, 124, 190, 0.15) 0%, transparent 40%),
                  radial-gradient(circle at 90% 80%, rgba(0, 240, 255, 0.1) 0%, transparent 40%);
    }

    .login-card {
      width: 450px;
      padding: 3rem;
      border-radius: var(--border-radius-lg);
    }

    .header {
      text-align: center;
      margin-bottom: 2rem;
    }

    .logo {
      font-size: 48px;
      background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 0.5rem;
    }

    .header h1 {
      font-size: 2rem;
      letter-spacing: 0.15em;
      line-height: 1;
      margin-bottom: 0.5rem;
    }

    .header p {
      color: var(--text-secondary);
      font-size: 0.9rem;
    }

    .login-form {
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .form-group label {
      font-size: 0.85rem;
      font-weight: 500;
      color: var(--text-secondary);
    }

    .submit-btn {
      width: 100%;
      justify-content: center;
      padding: 0.85rem;
      margin-top: 0.5rem;
    }

    .error-msg {
      background: rgba(255, 23, 68, 0.1);
      border: 1px solid rgba(255, 23, 68, 0.3);
      color: var(--color-danger);
      padding: 0.75rem 1rem;
      border-radius: 8px;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.85rem;
    }

    .error-icon {
      font-size: 18px;
    }

    .divider {
      position: relative;
      text-align: center;
      margin: 2rem 0 1.5rem;
    }

    .divider::before {
      content: "";
      position: absolute;
      left: 0;
      top: 50%;
      width: 100%;
      height: 1px;
      background: var(--glass-border);
      z-index: 1;
    }

    .divider span {
      position: relative;
      background: var(--bg-secondary);
      padding: 0 1rem;
      color: var(--text-muted);
      font-size: 0.75rem;
      z-index: 2;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .quick-logins {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.75rem;
    }

    .quick-logins button:last-child {
      grid-column: span 2;
    }

    .quick-btn {
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--glass-border);
      border-radius: 8px;
      padding: 0.6rem;
      color: var(--text-secondary);
      font-family: var(--font-title);
      font-size: 0.85rem;
      font-weight: 500;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      transition: var(--transition-smooth);
    }

    .quick-btn:hover {
      background: rgba(255, 255, 255, 0.05);
      color: var(--text-primary);
      border-color: var(--color-primary);
    }
  `]
})
export class LoginComponent {
  email = '';
  password = '';
  loading = false;
  error = '';

  private authService = inject(AuthService);
  private router = inject(Router);

  onSubmit(): void {
    this.loading = true;
    this.error = '';

    this.authService.login(this.email, this.password).subscribe({
      next: () => {
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.loading = false;
        this.error = err.error?.detail || 'Authentication failed. Please verify credentials.';
      }
    });
  }

  quickLogin(email: string, pass: string): void {
    this.email = email;
    this.password = pass;
    this.onSubmit();
  }
}
