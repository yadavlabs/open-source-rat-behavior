// Import core modules
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';

// Import components
import { AppComponent } from './app.component';
import { DeviceStartupComponent } from './device-startup/device-startup.component';
import { RunTrialComponent } from './run-trial/run-trial.component';

// Import supporting modules to make the Angular Materials UI
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatListModule } from '@angular/material/list';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';

@NgModule({
  declarations: [
    AppComponent,
    DeviceStartupComponent,
    RunTrialComponent
  ],
  imports: [
    BrowserModule,
    MatButtonModule,
    NoopAnimationsModule,
    MatSelectModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
    MatInputModule,
    MatFormFieldModule,
    MatListModule,
    MatTooltipModule,
    MatSlideToggleModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
