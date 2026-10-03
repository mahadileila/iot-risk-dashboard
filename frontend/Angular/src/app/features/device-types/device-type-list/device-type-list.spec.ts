import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DeviceTypeList } from './device-type-list';

describe('DeviceTypeList', () => {
  let component: DeviceTypeList;
  let fixture: ComponentFixture<DeviceTypeList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DeviceTypeList],
    }).compileComponents();

    fixture = TestBed.createComponent(DeviceTypeList);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
