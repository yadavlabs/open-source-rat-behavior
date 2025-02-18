import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RunTrialComponent } from './run-trial.component';

describe('RunTrialComponent', () => {
  let component: RunTrialComponent;
  let fixture: ComponentFixture<RunTrialComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RunTrialComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RunTrialComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
