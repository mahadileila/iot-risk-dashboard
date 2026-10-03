import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RiskFactorList } from './risk-factor-list';

describe('RiskFactorList', () => {
  let component: RiskFactorList;
  let fixture: ComponentFixture<RiskFactorList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RiskFactorList],
    }).compileComponents();

    fixture = TestBed.createComponent(RiskFactorList);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
