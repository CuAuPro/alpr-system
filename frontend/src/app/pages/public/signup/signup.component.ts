import { Component, OnInit } from '@angular/core';
import { AuthService } from '../../../auth/auth.service';
import { Router, RouterModule } from '@angular/router';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';

@Component({
  selector: 'app-signup',
  standalone: true,
  imports: [FormsModule, ReactiveFormsModule, RouterModule, ToastModule],
  templateUrl: './signup.component.html',
  styleUrl: './signup.component.scss'
})
export class SignupComponent implements OnInit {
  signUpForm!: FormGroup;

  constructor(
    private authService: AuthService,
    private router: Router,
    private formBuilder: FormBuilder,
    private toastr: MessageService
  ) {}

  ngOnInit(): void {
    if (this.authService.isLoggedIn()) {
      this.router.navigate(['/dashboard']);
    }
    this.signUpForm = this.formBuilder.group({
      firstName: ['', Validators.required],
      lastName: ['', Validators.required],
      username: ['', Validators.required],
      password: ['', Validators.required],
      confirmPassword: ['', Validators.required]
    });
  }

  signUp(): void {
    if (this.signUpForm.valid) {
      const firstName = this.signUpForm.get('firstName')!.value;
      const lastName = this.signUpForm.get('lastName')!.value;
      const username = this.signUpForm.get('username')!.value;
      const password = this.signUpForm.get('password')!.value;
      const confirmPassword = this.signUpForm.get('confirmPassword')!.value;

      // Check if new password and confirm password match
      if (password !== confirmPassword) {
        this.toastr.add({severity: 'error', summary: 'Error', detail: 'Password and confirm password do not match.', life: 2000});
        return;
      }

      this.authService.signUp(firstName, lastName, username, password).subscribe(
        success => {
          if (success) {
            // Registration successful
            this.toastr.add({severity: 'success', summary: 'Success', detail: 'Registration successful. Please login.', life: 2000});
            this.router.navigate(['/signin']);
          } else {
            // Registration failed
            this.toastr.add({severity: 'error', summary: 'Error', detail: 'Failed to register. Please try again.', life: 2000});
          }
        },
        error => {
          // Handle error
          console.error(error);
          this.toastr.add({severity: 'error', summary: 'Error', detail: 'Failed to register. Please try again.', life: 2000});
        }
      );
    }
  }
}