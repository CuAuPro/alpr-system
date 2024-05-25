import { Routes } from '@angular/router';
import { authGuard } from './auth/auth.guard';
// import { DashboardComponent } from './pages/secure/dashboard/dashboard.component';
import { WelcomeComponent } from './pages/public/welcome/welcome.component';
import { SignupComponent } from './pages/public/signup/signup.component';

import { AnalyticsComponent } from './pages/secure/analytics/analytics.component';
import { SignInComponent } from './pages/public/signin/signin.component';
import { ChangePasswordComponent } from './pages/secure/change-password/change-password.component';
import { DashboardComponent } from './pages/secure/dashboard/dashboard.component';
import { MonitorComponent } from './pages/secure/monitor/monitor.component';

// export const routes: Routes = [
//     { path: 'welcome', component: WelcomeComponent },
//     { path: 'login', component: LoginComponent },
//     { path: 'signup', component: SignupComponent },

//     { path: 'change-password', component: ChangePasswordComponent},
//     // { path: 'dashboard', component: DashboardComponent, canActivate: [authGuard] },
//     { path: 'dashboard', component: DashboardComponent},
//     { path: '**', redirectTo: 'welcome' }

// ];

export const routes: Routes = [
    {path: '',   redirectTo: '/welcome', pathMatch: 'full'},

    { path: 'welcome', component: WelcomeComponent },
    { path: 'signin', component: SignInComponent },
    { path: 'signup', component: SignupComponent },
    { path: 'change-password', component: ChangePasswordComponent, canActivate: [authGuard] },


    {path: 'dashboard', component: DashboardComponent, canActivate: [authGuard]},
    {path: 'analytics', component: AnalyticsComponent, canActivate: [authGuard]},
    {path: 'monitor', component: MonitorComponent, canActivate: [authGuard]},

  ];