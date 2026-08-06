import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { AuthService } from '../../core/auth/auth.service';

interface DocumentFile {
  id: string;
  filename: string;
  filepath: string;
  file_type: string;
  uploaded_at: string;
}

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="admin-container animate-fade-in">
      <header class="page-header">
        <h1>Administrator Dashboard & Control Panel</h1>
        <p>Manage system training assets, index manuals, and analyze platform records.</p>
      </header>

      <div class="admin-grid">
        <!-- Left: Upload manuals & Seed settings -->
        <section class="left-col">
          <!-- Document Upload Box -->
          <div class="glass-panel upload-card">
            <h3>Upload Bosch Internal Training Manuals</h3>
            <p class="section-desc">Select PDF engineering files to index in the Vector search database (RAG).</p>
            
            <div class="upload-zone" (click)="fileInput.click()">
              <span class="material-symbols-outlined upload-icon">cloud_upload</span>
              <p *ngIf="!selectedFile">Click to select PDF manual</p>
              <p *ngIf="selectedFile" class="selected-name">{{ selectedFile.name }}</p>
              <input 
                #fileInput 
                type="file" 
                (change)="onFileSelect($event)" 
                accept=".pdf" 
                style="display: none"
              >
            </div>

            <div class="upload-actions" *ngIf="selectedFile">
              <button class="btn-primary" (click)="onUpload()" [disabled]="uploading">
                <span>{{ uploading ? 'Uploading & Indexing Chunks...' : 'Confirm Upload' }}</span>
                <span class="material-symbols-outlined">send</span>
              </button>
              <button class="cancel-btn" (click)="cancelSelect()" [disabled]="uploading">Cancel</button>
            </div>

            <div class="progress-bar-loading" *ngIf="uploading">
              <div class="progress-bar-fill"></div>
            </div>
            
            <div class="success-msg" *ngIf="successMsg">
              <span class="material-symbols-outlined">check_circle</span>
              <span>{{ successMsg }}</span>
            </div>
            <div class="error-msg" *ngIf="errorMsg">
              <span class="material-symbols-outlined">error</span>
              <span>{{ errorMsg }}</span>
            </div>
          </div>

          <!-- Quick Seed Actions -->
          <div class="glass-panel seed-card">
            <h3>Quick Seeding Utilities</h3>
            <p class="section-desc">Seed basic system database records to begin evaluation immediately.</p>
            
            <div class="seed-actions">
              <button class="seed-btn" (click)="seedSkills()" [disabled]="seedingSkills">
                <span class="material-symbols-outlined">account_tree</span>
                <span>{{ seedingSkills ? 'Seeding...' : 'Seed Engineering Skills' }}</span>
              </button>
              
              <button class="seed-btn" (click)="seedSimulations()" [disabled]="seedingSims">
                <span class="material-symbols-outlined">developer_board</span>
                <span>{{ seedingSims ? 'Seeding...' : 'Seed Simulation Models' }}</span>
              </button>
            </div>
            
            <div class="seed-success" *ngIf="seedStatus">{{ seedStatus }}</div>
          </div>
        </section>

        <!-- Right: Uploaded Manuals table -->
        <section class="right-col glass-panel documents-card">
          <h3>Indexed Knowledge Base Manuals</h3>
          <p class="section-desc">List of internal manuals chunked and indexed for AI course context generation.</p>

          <div class="docs-table-wrapper" *ngIf="documents.length > 0">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>Manual Name</th>
                  <th>Type</th>
                  <th>Indexed Date</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let doc of documents">
                  <td class="filename-cell">
                    <span class="material-symbols-outlined pdf-icon">description</span>
                    <span>{{ doc.filename }}</span>
                  </td>
                  <td><span class="type-tag">{{ doc.file_type }}</span></td>
                  <td>{{ doc.uploaded_at | date:'shortDate' }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="docs-empty" *ngIf="documents.length === 0">
            <span class="material-symbols-outlined">folder_open</span>
            <p>No training manuals have been uploaded. Upload a PDF on the left to begin compiling standard libraries.</p>
          </div>
        </section>
      </div>
    </div>
  `,
  styles: [`
    .admin-container {
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

    .admin-grid {
      display: grid;
      grid-template-columns: 1fr 1.3fr;
      gap: 2rem;
      align-items: start;
    }

    .left-col, .right-col {
      display: flex;
      flex-direction: column;
      gap: 2rem;
    }

    .section-desc {
      color: var(--text-secondary);
      font-size: 0.85rem;
      margin-bottom: 1.25rem;
    }

    .upload-zone {
      border: 2px dashed var(--glass-border);
      border-radius: var(--border-radius);
      padding: 2.5rem;
      text-align: center;
      cursor: pointer;
      transition: var(--transition-smooth);
      background: rgba(255, 255, 255, 0.005);
    }

    .upload-zone:hover {
      border-color: var(--color-primary);
      background: rgba(0, 124, 190, 0.05);
    }

    .upload-icon {
      font-size: 48px;
      color: var(--text-muted);
      margin-bottom: 0.5rem;
    }

    .selected-name {
      color: var(--color-accent) !important;
      font-weight: 500;
    }

    .upload-actions {
      display: flex;
      gap: 0.75rem;
      margin-top: 1rem;
    }

    .upload-actions button {
      flex-grow: 1;
    }

    .cancel-btn {
      background: rgba(255, 255, 255, 0.05);
      color: var(--text-secondary);
      border: 1px solid var(--glass-border);
      border-radius: 8px;
      padding: 0.75rem;
      cursor: pointer;
      font-family: var(--font-title);
      transition: var(--transition-smooth);
    }

    .cancel-btn:hover {
      background: rgba(255, 255, 255, 0.08);
      color: var(--text-primary);
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

    .success-msg {
      background: rgba(0, 230, 118, 0.1);
      border: 1px solid rgba(0, 230, 118, 0.3);
      color: var(--color-success);
      padding: 0.75rem 1rem;
      border-radius: 8px;
      margin-top: 1rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.85rem;
    }

    .error-msg {
      background: rgba(255, 23, 68, 0.1);
      border: 1px solid rgba(255, 23, 68, 0.3);
      color: var(--color-danger);
      padding: 0.75rem 1rem;
      border-radius: 8px;
      margin-top: 1rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.85rem;
    }

    /* Seed Utilities */
    .seed-actions {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .seed-btn {
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--glass-border);
      color: var(--text-primary);
      border-radius: 8px;
      padding: 0.85rem;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.75rem;
      font-family: var(--font-title);
      font-weight: 500;
      cursor: pointer;
      transition: var(--transition-smooth);
    }

    .seed-btn:hover {
      background: rgba(255, 255, 255, 0.05);
      border-color: var(--color-primary);
    }

    .seed-success {
      margin-top: 1rem;
      font-size: 0.85rem;
      color: var(--color-accent);
      text-align: center;
    }

    /* Documents Card Panel */
    .documents-card {
      min-height: 480px;
    }

    .docs-table-wrapper {
      margin-top: 1rem;
      width: 100%;
    }

    .admin-table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }

    .admin-table th, .admin-table td {
      padding: 0.85rem 1rem;
      border-bottom: 1px solid var(--glass-border);
    }

    .admin-table th {
      font-family: var(--font-title);
      font-size: 0.9rem;
      color: var(--text-secondary);
    }

    .filename-cell {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-weight: 500;
    }

    .pdf-icon {
      color: var(--color-danger);
    }

    .type-tag {
      font-size: 0.7rem;
      background: rgba(255, 255, 255, 0.05);
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      text-transform: uppercase;
      font-weight: 600;
      color: var(--text-secondary);
    }

    .docs-empty {
      text-align: center;
      padding: 6rem;
      color: var(--text-muted);
    }

    .docs-empty span {
      font-size: 48px;
      margin-bottom: 1rem;
    }
  `]
})
export class AdminComponent implements OnInit {
  documents: DocumentFile[] = [];
  selectedFile: File | null = null;
  
  uploading = false;
  successMsg = '';
  errorMsg = '';

  seedingSkills = false;
  seedingSims = false;
  seedStatus = '';

  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private backendUrl = 'http://localhost:8000/api/v1';

  ngOnInit(): void {
    this.loadDocuments();
  }

  loadDocuments(): void {
    this.http.get<DocumentFile[]>(`${this.backendUrl}/knowledge/documents`).subscribe({
      next: (res) => this.documents = res,
      error: () => {}
    });
  }

  onFileSelect(event: any): void {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      this.selectedFile = file;
      this.successMsg = '';
      this.errorMsg = '';
    } else {
      this.errorMsg = 'Please select a valid PDF file.';
      this.selectedFile = null;
    }
  }

  cancelSelect(): void {
    this.selectedFile = null;
  }

  onUpload(): void {
    if (!this.selectedFile) return;
    this.uploading = true;
    this.successMsg = '';
    this.errorMsg = '';

    const formData = new FormData();
    formData.append('file', this.selectedFile);

    this.http.post<DocumentFile>(`${this.backendUrl}/knowledge/upload`, formData).subscribe({
      next: (res) => {
        this.uploading = false;
        this.selectedFile = null;
        this.successMsg = `Document "${res.filename}" successfully uploaded, split, and indexed.`;
        this.loadDocuments();
      },
      error: (err) => {
        this.uploading = false;
        this.errorMsg = err.error?.detail || 'Failed to complete document index processing.';
      }
    });
  }

  seedSkills(): void {
    this.seedingSkills = true;
    this.seedStatus = '';

    this.http.post(`${this.backendUrl}/employees/skills/seed`, {}).subscribe({
      next: () => {
        this.seedingSkills = false;
        this.seedStatus = 'Skills database seeded successfully.';
      },
      error: () => {
        this.seedingSkills = false;
        this.seedStatus = 'Failed to seed skills.';
      }
    });
  }

  seedSimulations(): void {
    this.seedingSims = true;
    this.seedStatus = '';

    this.http.post(`${this.backendUrl}/simulations/seed`, {}).subscribe({
      next: () => {
        this.seedingSims = false;
        this.seedStatus = 'Simulation models seeded successfully.';
      },
      error: () => {
        this.seedingSims = false;
        this.seedStatus = 'Failed to seed simulation models.';
      }
    });
  }
}
