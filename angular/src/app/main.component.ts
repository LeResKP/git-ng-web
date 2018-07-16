import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

import 'rxjs/add/operator/switchMap';
import { Subscription } from 'rxjs/Subscription';

import { GitService } from './git.service';
import { SelectorChoice } from './selector.component';


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
