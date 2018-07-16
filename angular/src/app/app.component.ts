import { Component } from '@angular/core';


@Component({
  selector: 'app-root',
  template: `
    <nav class="navbar navbar-expand-sm navbar-light bg-light p-0">
      <a class="navbar-brand col-md-2" href="#">Git ngWeb</a>
    </nav>
    <breadcrumb></breadcrumb>
    <router-outlet></router-outlet>
  `
})
export class AppComponent { }
