import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet, ActivatedRoute, NavigationEnd, Router } from '@angular/router';
import { filter, map } from 'rxjs';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './layout.html'
})
export class Layout {
  mobileMenuOpen = false;
  breadcrumb = 'Dashboard';

  constructor(
    private router: Router, 
    private route: ActivatedRoute,
    private authService: AuthService
  ) {
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd),
      map(() => {
        let child = this.route.firstChild;
        while (child?.firstChild) child = child.firstChild;
        return child?.snapshot.data['breadcrumb'] ?? 'Dashboard';
      })
    ).subscribe(label => this.breadcrumb = label);
  }

  toggleMobileMenu() {
    this.mobileMenuOpen = !this.mobileMenuOpen;
  }

  closeMobileMenu() {
    this.mobileMenuOpen = false;
  }

    logout() {
    this.authService.logout();
  }
}