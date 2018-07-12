import { Component, Input } from '@angular/core';


export interface SelectorChoice {
  label: string;
  routerLink: (string|number)[];
}


@Component({
  selector: 'app-selector, [app-selector]',
  template: `
	<span ngbDropdown>
		<a id="dropdownBasic1" ngbDropdownToggle>{{choice || label}}</a>
		<div ngbDropdownMenu aria-labelledby="dropdownBasic1">
			<a [routerLink]="c.routerLink" routerLinkActive="active" class="dropdown-item" *ngFor="let c of choices">{{c.label}}</a>
		</div>
	</span>
  `,
})
export class SelectorComponent {
  @Input() label: string;
  @Input() choices: SelectorChoice[];
  @Input() choice: string;

}
