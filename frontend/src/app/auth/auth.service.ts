import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { map, catchError, tap } from 'rxjs/operators';
import * as bcrypt from 'bcryptjs';
import { JwtHelperService } from '@auth0/angular-jwt';
import { PostAuthSigninData, AuthenticationService, SigninResponse, SigninRequest, ChangePasswordRequest, PostAuthChangePasswordData, SignupRequest, PostAuthSignupData } from '../rest-api';
import { OpenAPI } from '../rest-api/core/OpenAPI';

export interface UserData {
  firstName?: string;
  lastName?: string;
  username?: string;
  role?: string;
}


@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private authUrl = 'https://localhost/auth';  // Replace with your API URL
  private tokenKey = 'auth-token';
  private userKey = 'auth-user';
  private jwtHelper = new JwtHelperService();

  private user!: SigninResponse;

  constructor(
    private http: HttpClient,
    private authService: AuthenticationService
  ) {}


  // Save user data to localStorage
  setUserData(userData: UserData) {
    localStorage.setItem(this.userKey, JSON.stringify(userData));
  }

  // Retrieve user data from localStorage
  getUserData(): UserData | null {
    const userData = localStorage.getItem(this.userKey);
    return userData ? JSON.parse(userData) : null;
  }

  // Clear user data from localStorage
  clearUserData() {
    localStorage.removeItem(this.userKey);
  }


  signIn(username: string, password: string) {

    const form: SigninRequest = {
      username: username,
      password: password
    }
    const request: PostAuthSigninData = {
      requestBody: form
    };
    // Return the observable from authService.postAuthSignin
    return this.authService.postAuthSignin(request).pipe(
      tap((response: SigninResponse) => {
        // Save token and user details in localStorage
        // Ensure the token is defined
        if (!response.token) {
          throw new Error('Authentication token is missing in the response');
        }

        // Save token and user details in localStorage
        localStorage.setItem(this.tokenKey, response.token);
        const userData: UserData = {
          firstName: response.firstName,
          lastName: response.lastName,
          username: response.username,
          role: response.role,
        };
        this.setUserData(userData);
      })
    );
  }


  signUp(firstName: string, lastName: string, username: string, password: string){

    const form: SignupRequest = {
      firstName: firstName,
      lastName: lastName,
      username: username,
      password: password,
    }
    const request: PostAuthSignupData = {
      requestBody: form
    };
    // Return the observable from authService.postAuthSignin
    return this.authService.postAuthSignup(request).pipe(
      tap((response: SigninResponse) => {

      })
    );
  }


  changePassword(username:string, oldPassword: string, newPassword: string){

    const form: ChangePasswordRequest = {
      username: username,
      oldPassword: oldPassword,
      newPassword: newPassword,
    }
    const request: PostAuthChangePasswordData = {
      requestBody: form
    };
    // Return the observable from authService.postAuthSignin
    return this.authService.postAuthChangePassword(request).pipe(
      tap((response: SigninResponse) => {

      })
    );
  }
  
  logout(): void {
    localStorage.removeItem(this.tokenKey);
    this.clearUserData();
  }

  isLoggedIn(): boolean {
    const token = localStorage.getItem(this.tokenKey);
    if (token !== null){
      OpenAPI.TOKEN = token;
    }
    return !!(token && !this.jwtHelper.isTokenExpired(token));
  }

  getUser(): any {
    return this.getUserData();
  }

}