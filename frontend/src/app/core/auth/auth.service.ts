import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap, map } from 'rxjs';
import { Router } from '@angular/router';

export interface UserResponse {
  email: string;
  role: { id: string; name: string };
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  private baseUrl = 'http://localhost:8000/api/v1/auth';

  private currentUserSubject = new BehaviorSubject<UserResponse | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor() {
    // Reload user if token is present
    const savedUser = localStorage.getItem('user_details');
    if (savedUser) {
      try {
        this.currentUserSubject.next(JSON.parse(savedUser));
      } catch (e) {
        this.logout();
      }
    }
  }

  public get currentUserValue(): UserResponse | null {
    return this.currentUserSubject.value;
  }

  public get isLoggedIn(): boolean {
    return !!localStorage.getItem('access_token');
  }

  public get userRole(): string {
    return this.currentUserValue?.role?.name || 'Employee';
  }

  login(email: string, password: string): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${this.baseUrl}/login`, { email, password }).pipe(
      tap(res => {
        localStorage.setItem('access_token', res.access_token);
        localStorage.setItem('user_details', JSON.stringify(res.user));
        this.currentUserSubject.next(res.user);
      })
    );
  }

  register(email: string, password: string, roleName: string = 'Employee'): Observable<UserResponse> {
    return this.http.post<UserResponse>(`${this.baseUrl}/register`, {
      email,
      password,
      role_name: roleName
    });
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_details');
    this.currentUserSubject.next(null);
    this.router.navigate(['/login']);
  }
}
