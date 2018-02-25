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
      <ul class="navbar-nav mr-auto">
        <li class="nav-item dropdown">
          <app-selector label="Project" [choices]="projectChoices"></app-selector>
        </li>
        <li class="nav-item dropdown">
          <app-selector label="Branch" [choices]="branchChoices"></app-selector>
        </li>
      </ul>
    </nav>
    <router-outlet></router-outlet>
  `,
})
export class MainComponent implements OnInit {

  public projectChoices: SelectorChoice[] = [];
  public branchChoices: SelectorChoice[];

  constructor(private route: ActivatedRoute, private gitService: GitService) {}

  ngOnInit() {
    // NOTE: no need to unsubscribe here since the component is never destroyed
    this.route.paramMap
        .switchMap((params: ParamMap) =>
          this.gitService.getProject(params.get('id')))
        .subscribe(project => {
          this.branchChoices = [];
          project.branches.local.map(branch => {
            this.branchChoices.push({
              label: branch,
              routerLink: ['/p', project.id, 'b', branch, 'commits'],
            });
          });

          project.branches.remote.map(branch => {
            this.branchChoices.push({
              label: branch,
              routerLink: ['/p', project.id, 'b', branch, 'commits'],
            });
          });
        });

    this.gitService.getProjects().subscribe(projects => {
      projects.map(project => {
        this.projectChoices.push({
          label: project.name,
          routerLink: ['/p', project.id],
        });
      });
    });
  }
}


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
          this.router.navigate(['/p', projectId, 'b', project.branches.default, 'commits']);
        });
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }
}
