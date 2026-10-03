import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RiskClassificationList } from './risk-classification-list';

describe('RiskClassificationList', () => {
  let component: RiskClassificationList;
  let fixture: ComponentFixture<RiskClassificationList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RiskClassificationList],
    }).compileComponents();

    fixture = TestBed.createComponent(RiskClassificationList);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
