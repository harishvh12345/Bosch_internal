import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from './core/auth/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <div class="app-container" [class.authenticated]="authService.isLoggedIn">
      <!-- Sidebar navigation shown only when logged in -->
      <aside class="sidebar glass-panel" *ngIf="authService.isLoggedIn">
        <div class="brand">
          <div class="logo-box">
            <span class="material-symbols-outlined logo-icon">insights</span>
          </div>
          <div class="brand-text">
            <h2>BOSCH</h2>
            <p>AI Learning Platform</p>
          </div>
        </div>

        <nav class="nav-links">
          <a routerLink="/dashboard" routerLinkActive="active" class="nav-item">
            <span class="material-symbols-outlined">dashboard</span>
            <span>Dashboard</span>
          </a>
          
          <a routerLink="/simulations" routerLinkActive="active" class="nav-item">
            <span class="material-symbols-outlined">analytics</span>
            <span>Simulations</span>
          </a>

          <a routerLink="/admin" routerLinkActive="active" class="nav-item" *ngIf="isAdminOrManager">
            <span class="material-symbols-outlined">admin_panel_settings</span>
            <span>Admin Control</span>
          </a>
        </nav>

        <div class="user-profile-footer">
          <div class="user-avatar">
            <span class="material-symbols-outlined">account_circle</span>
          </div>
          <div class="user-meta">
            <p class="user-email">{{ authService.currentUserValue?.email }}</p>
            <span class="user-role-tag">{{ authService.userRole }}</span>
          </div>
          <button class="logout-btn" (click)="authService.logout()">
            <span class="material-symbols-outlined">logout</span>
          </button>
        </div>
      </aside>

      <!-- Main content container -->
      <main class="main-content">
        <router-outlet></router-outlet>
      </main>
    </div>
  `,
  styles: [`
    .app-container {
      display: flex;
      height: 100vh;
      width: 100vw;
      background-color: var(--bg-primary);
    }

    .sidebar {
      width: 280px;
      height: 96vh;
      margin: 2vh 0 2vh 2vh;
      border-radius: var(--border-radius-lg);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      z-index: 100;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 1rem;
      padding-bottom: 2rem;
      border-bottom: 1px solid var(--glass-border);
    }

    .logo-box {
      width: 42px;
      height: 42px;
      background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 12px rgba(0, 124, 190, 0.4);
    }

    .logo-icon {
      color: white;
      font-size: 24px;
    }

    .brand-text h2 {
      font-size: 1.25rem;
      font-weight: 700;
      letter-spacing: 0.1em;
      line-height: 1.2;
    }

    .brand-text p {
      font-size: 0.75rem;
      color: var(--text-secondary);
    }

    .nav-links {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      margin-top: 2rem;
      flex-grow: 1;
    }

    .nav-item {
      display: flex;
      align-items: center;
      gap: 1rem;
      padding: 0.85rem 1.25rem;
      border-radius: 8px;
      color: var(--text-secondary);
      text-decoration: none;
      font-family: var(--font-title);
      font-weight: 500;
      transition: var(--transition-smooth);
    }

    .nav-item:hover {
      color: var(--text-primary);
      background: rgba(255, 255, 255, 0.04);
    }

    .nav-item.active {
      color: white;
      background: linear-gradient(90deg, rgba(0, 124, 190, 0.25) 0%, rgba(0, 240, 255, 0.05) 100%);
      border-left: 3px solid var(--color-primary);
    }

    .nav-item span.material-symbols-outlined {
      font-size: 22px;
    }

    .user-profile-footer {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding-top: 1.5rem;
      border-top: 1px solid var(--glass-border);
    }

    .user-avatar span {
      font-size: 36px;
      color: var(--text-secondary);
    }

    .user-meta {
      flex-grow: 1;
      overflow: hidden;
    }

    .user-email {
      font-size: 0.8rem;
      font-weight: 500;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .user-role-tag {
      font-size: 0.65rem;
      font-weight: 600;
      color: var(--color-accent);
      background: rgba(0, 240, 255, 0.1);
      padding: 0.1rem 0.4rem;
      border-radius: 4px;
      text-transform: uppercase;
    }

    .logout-btn {
      background: none;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      display: flex;
      align-items: center;
      transition: var(--transition-smooth);
    }

    .logout-btn:hover {
      color: var(--color-danger);
    }

    .main-content {
      flex-grow: 1;
      height: 100vh;
      overflow-y: auto;
      padding: 2vh;
    }
  `]
})
export class AppComponent {
  authService = inject(AuthService);

  get isAdminOrManager(): boolean {
    const role = this.authService.userRole;
    return role === 'Admin' || role === 'Manager';
  }
}
