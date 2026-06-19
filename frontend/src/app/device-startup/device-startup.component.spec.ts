import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DeviceStartupComponent } from './device-startup.component';

describe('DeviceStartupComponent', () => {
  let component: DeviceStartupComponent;
  let fixture: ComponentFixture<DeviceStartupComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DeviceStartupComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DeviceStartupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
