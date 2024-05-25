import { Component } from '@angular/core';
import { AuthService } from '../../../auth/auth.service';
import { Router, RouterModule } from '@angular/router';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';

@Component({
  selector: 'app-signin',
  standalone: true,
  imports: [FormsModule, ReactiveFormsModule, RouterModule, ToastModule],
  templateUrl: './signin.component.html',
  styleUrl: './signin.component.scss'
})
export class SignInComponent {
  signInForm!: FormGroup;

  constructor(
    private authService: AuthService,
    private router: Router,
    private formBuilder: FormBuilder,
    public toastr: MessageService) {}

  ngOnInit(): void {
    if (this.authService.isLoggedIn()) {
      this.router.navigate(['/dashboard']);
    }
    this.signInForm = this.formBuilder.group({
      username: ['', Validators.required],
      password: ['', Validators.required]
    });
  }
  
  signIn(): void {
    if (this.signInForm.valid) {
      const username = this.signInForm.get('username')!.value;
      const password = this.signInForm.get('password')!.value;
  
      // Call signIn method from AuthService
      this.authService.signIn(username, password).subscribe(
        (response: any) => {
          // signIn successful
          this.toastr.add({severity: 'success', summary: 'Success', detail: 'Signed in!', life: 2000});
          this.router.navigate(['/dashboard']);
        },
        (error: any) => {
          // signIn failed
          console.error('Sign-in failed:', error);
          this.toastr.add({severity: 'error', summary: 'Error', detail: 'Failed to Sign In. Please try again...', life: 2000});
        }
      );
    } else {
      // Form is invalid
      this.toastr.add({severity: 'warning', summary: 'Warning', detail:' Please fill out all required fields...', life: 2000});
    }
  }
}