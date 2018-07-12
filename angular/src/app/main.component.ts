import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

import 'rxjs/add/operator/switchMap';
import { Subscription } from 'rxjs/Subscription';

import { GitService } from './git.service';
import { SelectorChoice } from './selector.component';


@Component({
  selector: 'app-main',
  template: `
    <nav class="navbar navbar-expand-sm navbar-light bg-light p-0">
      <a class="navbar-brand col-md-2" href="#">Git ngWeb</a>
    </nav>
    <breadcrumb></breadcrumb>
    <router-outlet></router-outlet>
  `,
})
export class MainComponent {}


@Component({
  template: '',
})
export class RedirectBranchComponent implements OnDestroy, OnInit {

  private subscription: Subscription;

  constructor(private route: ActivatedRoute, private router: Router, private gitService: GitService) {}

  ngOnInit() {
    const projectId = this.route.parent.snapshot.params['id'];
    this.subscription = this.route.paramMap
        .switchMap((params: ParamMap) =>
          this.gitService.getProject(projectId))
        .subscribe(project => {
          this.router.navigate(['/p', projectId, 'tree', project.branches.default]);
        });
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }
}
