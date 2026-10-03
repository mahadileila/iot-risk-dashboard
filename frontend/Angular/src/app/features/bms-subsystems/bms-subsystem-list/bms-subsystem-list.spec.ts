import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BmsSubsystemList } from './bms-subsystem-list';

describe('BmsSubsystemList', () => {
  let component: BmsSubsystemList;
  let fixture: ComponentFixture<BmsSubsystemList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BmsSubsystemList],
    }).compileComponents();

    fixture = TestBed.createComponent(BmsSubsystemList);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
