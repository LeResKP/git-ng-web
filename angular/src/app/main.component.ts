import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap } from '@angular/router';

import 'rxjs/add/operator/switchMap';

import { GitService } from './git.service';


@Component({
  selector: 'app-main',
  template: `
    <div class="container-fuild">
      <div class="row">
        <div class="col-md-2 bg-light">
          <h5>Projects</h5>
          <ul class="nav flex-column">
            <li *ngFor="let project of projects">
              <a [routerLink]="['/p', project.id]">{{project.name}}</a>
            </li>
          </ul>

          <div *ngIf="project$ | async as project">
            <h5>Local branches</h5>
            <ul class="nav flex-column">
              <li *ngFor="let branch of project?.local_branches">
              <a [routerLink]="['/p', project.id, 'b', branch]">{{branch}}</a>
              </li>
            </ul>

            <h5>Remote branches</h5>
            <ul class="nav flex-column">
              <li *ngFor="let branch of project?.remote_branches">
                <a [routerLink]="['/p', project.id, 'b', branch]">{{branch}}</a>
              </li>
            </ul>
          </div>
        </div>
        <div class="col-md-10">
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
