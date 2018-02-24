import { AfterViewInit, Component, ContentChildren, Input, OnDestroy, QueryList, ViewChildren } from '@angular/core';
import { NavigationEnd, Router, RouterLinkActive } from '@angular/router';

import { Subscription } from 'rxjs/Subscription';


export interface SelectorChoice {
  label: string;
  routerLink: (string|number)[];
}


@Component({
  selector: 'app-selector',
  template: `
	<span ngbDropdown>
		<a class="nav-link" id="dropdownBasic1" ngbDropdownToggle>{{choice || label}}</a>
		<div ngbDropdownMenu aria-labelledby="dropdownBasic1">
			<a [routerLink]="c.routerLink" routerLinkActive="active" class="dropdown-item" *ngFor="let c of choices">{{c.label}}</a>
		</div>
	</span>
  `,
})
export class SelectorComponent implements AfterViewInit, OnDestroy {
  @Input() label: string;
  @Input() choices: SelectorChoice[];
  private choice: string;

  private subscription: Subscription;
  private linksSubscription: Subscription;


  @ViewChildren(RouterLinkActive) links: QueryList<RouterLinkActive>;

  constructor(router: Router) {
    this.subscription = router.events.subscribe(s => {
      if (s instanceof NavigationEnd) {
        this.update();
      }
    });
  }

  ngAfterViewInit() {
    this.linksSubscription = this.links.changes.subscribe(_ => this.update());
    this.update();
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
    this.linksSubscription.unsubscribe();
  }

  update() {
    if (! this.links) { return; }
    Promise.resolve().then(() => {
      const actives = this.links.filter((link: RouterLinkActive) => (<any>link).hasActiveLinks());
      const active = actives.length ? actives[0] : null;
      if (active) {
        this.choice = (<any>active).element.nativeElement.innerHTML;
      }
    });
  }

}
