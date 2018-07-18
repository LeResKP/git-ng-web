import { Component, Input } from '@angular/core';


@Component({
  selector: 'app-breadcrumb',
  template: `
    <nav aria-label="breadcrumb" *ngIf="items">
      <ol class="breadcrumb breadcrumb-tree">
        <li class="breadcrumb-item" *ngFor="let item of items; let last=last">
          <a *ngIf="!last" href="#" [routerLink]="item.paths">{{item.name}}</a>
          <span *ngIf="last">{{item.name}}</span>
        </li>
      </ol>
    </nav>
  `,
})
export class BreadcrumbComponent {

  @Input() items;
  @Input() base;
  @Input() paths;

  getItems() {
    if (! this.base || ! this.paths) {
      return null;
    }
    const lis = this.base.slice();
    const n = [{
      'name': 'Home',
      'paths': lis.slice(),
    }];

    this.paths.map(path => {
      lis.push(path);
      n.push({
          'name': path,
          'paths': lis.slice(),
        });
    });
    return n;
  }

}
