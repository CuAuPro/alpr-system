import { ApplicationConfig, importProvidersFrom } from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { HttpClientModule } from '@angular/common/http';
import { AuthService } from './auth/auth.service';

import { BrowserAnimationsModule, provideAnimations } from '@angular/platform-browser/animations';
import { ConfirmationService, MessageService } from 'primeng/api';
import { DatePipe } from '@angular/common';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    importProvidersFrom(HttpClientModule),
    AuthService,
    BrowserAnimationsModule,
    provideAnimations(),
    MessageService,
    ConfirmationService,
    DatePipe
  ]
};
