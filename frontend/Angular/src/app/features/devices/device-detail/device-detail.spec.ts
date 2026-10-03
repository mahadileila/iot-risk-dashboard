import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DeviceDetail } from './device-detail';

describe('DeviceDetail', () => {
  let component: DeviceDetail;
  let fixture: ComponentFixture<DeviceDetail>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DeviceDetail],
    }).compileComponents();

    fixture = TestBed.createComponent(DeviceDetail);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
