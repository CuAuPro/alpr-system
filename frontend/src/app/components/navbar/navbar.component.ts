import { NgIf } from '@angular/common';
import { AppService } from './../../services/app.service';
import { Component, Input, OnInit } from '@angular/core';
import { CollapseModule } from 'ngx-bootstrap/collapse';
import { AuthService } from '../../auth/auth.service';
import { Router } from '@angular/router';

import { BsDropdownModule } from 'ngx-bootstrap/dropdown';


@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [NgIf, CollapseModule, BsDropdownModule],
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent implements OnInit {
  @Input() isLoggedIn: boolean = false; // Input property to determine if the user is logged in

  constructor(
    private router: Router,
    private appService: AppService,
    private authService: AuthService
  ) { }
  isCollapsed = true;
  ngOnInit() {
  }

  toggleSidebarPin() {
    this.appService.toggleSidebarPin();
  }
  toggleSidebar() {
    this.appService.toggleSidebar();
  }

  
  logout() {
    this.authService.logout();
    this.router.navigate(['/welcome']);
  }

  navigateChangePassword() {
    this.router.navigate(['/change-password']);
  }

}
