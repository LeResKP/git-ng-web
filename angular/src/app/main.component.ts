import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

import 'rxjs/add/operator/switchMap';
import { Subscription } from 'rxjs/Subscription';

import { GitService } from './git.service';
import { SelectorChoice } from './selector.component';


@Component({
  template: '',
})
export class RedirectComponent implements OnInit {

  constructor(private route: ActivatedRoute, private router: Router, private gitService: GitService) {}

  ngOnInit() {

    this.gitService.projects$.first().subscribe(projects => {
      this.router.navigate(['/', projects[0].id, projects[0].branches.default, 'commits']);
    });
  }
}


@Component({
  template: `
    <nav class="navbar navbar-expand-sm navbar-light bg-light p-0">
      <a class="navbar-brand col-md-2" href="#">Git ngWeb</a>
      <ul class="navbar-nav mr-auto">
        <li class="nav-item dropdown" app-selector label="Project" [choices]="projectChoices" [value]="projectId"></li>
        <li class="nav-item dropdown" app-selector label="Branch" [choices]="branchChoices" [value]="hash"></li>
        <li class="nav-item">
          <a class="nav-link" href="#" routerLinkActive="active" [routerLink]="['/', projectId, hash, 'tree']" [routerLinkActiveOptions]="{ exact: false, __change_detection_hack__: [projectId, hash] }">Tree</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="#" routerLinkActive="active" [routerLink]="['/', projectId, hash, 'commits']"  [routerLinkActiveOptions]="{ exact: false, __change_detection_hack__: [projectId, hash] }">Commits</a>
        </li>
      </ul>
    </nav>
    <router-outlet></router-outlet>
  `
})
export class MainComponent implements OnInit {

  public projectId;
  public hash;

  public projectChoices: SelectorChoice[] = [];
  public branchChoices: SelectorChoice[] = [];

  constructor(private route: ActivatedRoute, private gitService: GitService) {}

  ngOnInit() {
    this.gitService.projects$.subscribe(projects => {
      this.projectChoices = [];
      projects.map(project => {
        this.projectChoices.push({
          label: project.name,
          value: project.id,
          routerLink: ['/', project.id, project.branches.default, 'commits'],
        });
      });
    });

    this.route.paramMap.subscribe((params) => {
      this.projectId = +params.get('projectId');
      this.hash = params.get('sha');

      this.gitService.getProject(this.projectId).subscribe(project => {
        this.branchChoices = [];
        project.branches.local.map(branch => {
          this.branchChoices.push({
            label: branch,
            value: branch,
            routerLink: ['/', this.projectId, branch, 'commits'],
          });
        });
      });

    });
  }

}
