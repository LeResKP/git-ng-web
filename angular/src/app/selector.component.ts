import { Component, Input, SimpleChanges, OnChanges } from '@angular/core';


export interface SelectorChoice {
  label: string;
  value: any;
  routerLink: (string|number)[];
}


@Component({
  selector: 'app-selector, [app-selector]',
  template: `
	<span ngbDropdown>
		<a id="dropdownBasic1" ngbDropdownToggle class="nav-link active">{{choice || label}}</a>
		<div ngbDropdownMenu aria-labelledby="dropdownBasic1">
			<a [routerLink]="c.routerLink" routerLinkActive="active" class="dropdown-item" *ngFor="let c of choices">{{c.label}}</a>
		</div>
	</span>
  `,
})
export class SelectorComponent implements OnChanges {
  @Input() label: string;
  @Input() choices: SelectorChoice[] = null;
  @Input() value: any = null;
  choice: string;


  ngOnChanges(changes: SimpleChanges) {
    if (this.value !== null && this.choices !== null)  {
      const choices = this.choices.filter((c) => c.value === this.value);
      if (choices.length === 1) {
        this.choice = choices[0].label;
      }
    }
  }

}
