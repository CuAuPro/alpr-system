import { Component } from '@angular/core';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from '../../../auth/auth.service';
import { Router, RouterModule } from '@angular/router';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';

@Component({
  selector: 'app-change-password',
  standalone: true,
  imports: [FormsModule, ReactiveFormsModule, RouterModule, ToastModule],
  templateUrl: './change-password.component.html',
  styleUrl: './change-password.component.scss'
})
export class ChangePasswordComponent {
  changePasswordForm!: FormGroup;

  constructor(
    private authService: AuthService,
    private router: Router,
    private formBuilder: FormBuilder,
    private toastr: MessageService
  ) {}

  ngOnInit(): void {

    this.changePasswordForm = this.formBuilder.group({
      oldPassword: ['', Validators.required],
      newPassword: ['', Validators.required],
      confirmPassword: ['', Validators.required]
    });
  }

  changePassword(): void {
    if (this.changePasswordForm.valid) {
      const username = this.authService.getUserData()?.username;
      if (!username) {
        throw new Error('Unknown username.');
      }
      const oldPassword = this.changePasswordForm.get('oldPassword')!.value;
      const newPassword = this.changePasswordForm.get('newPassword')!.value;
      const confirmPassword = this.changePasswordForm.get('confirmPassword')!.value;

      // Check if new password and confirm password match
      if (newPassword !== confirmPassword) {
        this.toastr.add({severity: 'error', summary: 'Error', detail: 'Password and confirm password do not match.', life: 2000});
        return;
      }

      this.authService.changePassword(username, oldPassword, newPassword).subscribe(
        success => {
          if (success) {
            // Registration successful
            this.toastr.add({severity: 'success', summary: 'Success', detail: 'Password changed successfully.', life: 2000});
          } else {
            // Registration failed
            this.toastr.add({severity: 'error', summary: 'Error', detail: 'Failed to change password. Please try again.', life: 2000});
          }
        },
        error => {
          // Handle error
          console.error(error);
          this.toastr.add({severity: 'error', summary: 'Error', detail: 'Failed to change password. Please try again.', life: 2000});
        }
      );
    }
  }
}
