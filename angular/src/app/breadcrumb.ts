import { Component, Injectable, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap, Router, NavigationEnd } from '@angular/router';

import { GitService } from './git.service';
import { SelectorChoice } from './selector.component';


@Injectable()
export class BreadcrumbService {

  projectId;
  project;
  hash;
  paths;
  action;

  public projectChoices: SelectorChoice[] = [];
  public branchChoices: SelectorChoice[] = [];

  constructor(private route: ActivatedRoute, private router: Router, private gitService: GitService) {
    const breadcrumbs$ = this.router.events
      .filter(event => event instanceof NavigationEnd)
      .distinctUntilChanged().subscribe(() => {
        this.build();
      });
  }

  build() {
    const mainRoute = this.route.root.children[0];
    this.projectId = mainRoute.snapshot.params['id'];

    this.gitService.getProject(this.projectId)
    .subscribe(project => {
      this.project = project.name;
      this.branchChoices = [];
      project.branches.local.map(branch => {
        this.branchChoices.push({
          label: branch,
          routerLink: ['/p', project.id, 'tree', branch],
        });
      });

      project.branches.remote.map(branch => {
        this.branchChoices.push({
          label: branch,
          routerLink: ['/p', project.id, 'tree', branch],
        });
      });
    });

    this.gitService.getProjects().subscribe(projects => {
      this.projectChoices = [];
      projects.map(project => {
        this.projectChoices.push({
          label: project.name,
          routerLink: ['/p', project.id],
        });
      });
    });


    if (mainRoute.children.length) {
      const hashRoute = mainRoute.children[0];
      this.hash = hashRoute.snapshot.params['hash'];
      // TODO: better handling of children routes
      if (hashRoute.snapshot.url.length) {
        this.action = hashRoute.snapshot.url[0]['path'];
        if (this.action === 'commits') {
          this.paths = null;
          return;
        }
      }

      if (hashRoute.children.length) {
        const pathRoute = hashRoute.children[0];
        const paths = pathRoute.snapshot.url;

        const lis = [];
        let n = [];
        if (paths) {
          n = [{
            'name': 'root',
            'path': '',
          }];
        }
        paths.map(path => {

          if (!path.path) {
            return;
          }

          lis.push(path.path);
          n.push({
            'name': path.path,
            'path': lis.slice(),
          });
        });

        this.paths = n;
      } else {
        this.paths = null;
      }
    }
  }
}



@Component({
  selector: 'breadcrumb',
  template: `
  <nav aria-label="breadcrumb">
    <ol class="breadcrumb">
    <li class="breadcrumb-item" app-selector label="Project" [choices]="breadcrumbService.projectChoices" [choice]="breadcrumbService.project">
      </li>
    <li class="breadcrumb-item" app-selector label="Branch" [choices]="breadcrumbService.branchChoices" [choice]="breadcrumbService.hash">
      </li>
      <li class="breadcrumb-item" *ngFor="let path of breadcrumbService.paths; let last=last;">
        <a href="#" [routerLink]="treeUrl(path)" *ngIf="!last">{{path.name}}</a>
        <span *ngIf="last">{{path.name}}</span>
      </li>
    </ol>
  </nav>
  `,
})
export class BreadcrumbComponent {


  constructor(public breadcrumbService: BreadcrumbService) {
  }

  treeUrl(path) {
    const lis = ['/p', this.breadcrumbService.projectId, 'tree', this.breadcrumbService.hash];
    return lis.concat(path.path);
  }

}
