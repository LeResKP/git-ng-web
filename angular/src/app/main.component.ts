import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

import 'rxjs/add/operator/switchMap';

import { GitService } from './git.service';


@Component({
  selector: 'app-main',
  template: `
    <nav class="navbar navbar-dark bg-dark p-0">
      <a class="navbar-brand col-md-2" href="#">Git ngWeb</a>
    </nav>
    <div class="container-fluid">
      <div class="row">
        <nav class="col-md-2 bg-light sidebar p-0">
          <div class="p-1">Projects</div>
          <ul class="nav flex-column">
            <li *ngFor="let project of projects" class="nav-item">
              <small>
                <a [routerLink]="['/p', project.id]" routerLinkActive="active" class="nav-link px-2 py-1">{{project.name}}</a>
              </small>
            </li>
          </ul>

          <div *ngIf="project$ | async as project">
            <div class="p-1 mt-3">Local branches</div>
            <ul class="nav flex-column">
              <li *ngFor="let branch of project?.local_branches">
              <small>
              <a [routerLink]="['/p', project.id, 'b', branch]" routerLinkActive="active" class="nav-link px-2 py-1">{{branch}}</a>
              </small>
              </li>
            </ul>

            <div class="p-1 mt-3">Remote branches</div>
            <ul class="nav flex-column">
              <li *ngFor="let branch of project?.remote_branches">
              <small>
                <a [routerLink]="['/p', project.id, 'b', branch]" routerLinkActive="active" class="nav-link px-2 py-1">{{branch}}</a>
              </small>
              </li>
            </ul>
          </div>
        </nav>
        <div class="col-md-10 pt-3">
          <router-outlet></router-outlet>
        </div>
      </div>
    </div>
  `,
})
export class MainComponent implements OnInit {

  public projects;
  public project$;

  constructor(private route: ActivatedRoute, private gitService: GitService) {}

  ngOnInit() {
    this.project$ = this.route.paramMap
        .switchMap((params: ParamMap) =>
          this.gitService.getProject(params.get('id')));

    this.gitService.getProjects().subscribe(projects => {
      this.projects = projects;
    });
  }
}


@Component({
  template: '',
})
export class RedirectBranchComponent implements OnInit {

  private project$;

  constructor(private route: ActivatedRoute, private router: Router, private gitService: GitService) {}

  ngOnInit() {
    const projectId = this.route.parent.snapshot.params['id'];
    this.project$ = this.route.paramMap
        .switchMap((params: ParamMap) =>
          this.gitService.getProject(projectId));

    this.project$.subscribe(project => {
      this.router.navigate(['/p', projectId, 'b', project.current_branch || project.local_branches[0]]);
    });
  }
}
