import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/switchMap';

import { GitService } from './git.service';


@Component({
  template: `
  <div class="container-fluid">
    <app-breadcrumb [items]="breadcrumbItems"></app-breadcrumb>
    <div *ngIf="data$ | async as data" class="list-group list-group-tree">
      <a  [routerLink]="url(file)" *ngFor="let file of data" class="list-group-item list-group-item-action">
        <i [class.fa-folder]="file.type === 'tree'" [class.fa-file]="file.type === 'blob'" class="far"></i>
        {{file.name}}
      </a>
    </div>
  </div>
  `,
})
export class TreeComponent implements OnInit {


  public data$;
  public projectId;
  public hash;
  public breadcrumbItems = [];

  constructor(private route: ActivatedRoute, private gitService: GitService, private router: Router) {}


  ngOnInit() {
    const obsCombined = Observable.combineLatest(
      this.route.parent.parent.paramMap, this.route.url,
      (params, url) => ({params, url}));

    this.data$ = obsCombined.switchMap((ap) => {
      const url = ap.url;
      const params = ap.params;
      const paths = url.map((seg) => seg.path);
      let path = paths.join('/');
      this.projectId = ap.params.get('projectId');
      this.hash = ap.params.get('sha');
      this.updateBreadcrumb(paths);
      if (path) {
        path += '/';
      }
      return this.gitService.tree(
        this.projectId, this.hash, path);
    });
  }

  url(file) {
    const paths = ['/', this.projectId, this.hash, file.type];
    if (!file.path) {
      return paths;
    }
    return paths.concat(file.path.split('/'));
  }

  updateBreadcrumb(paths) {
    const lis = ['/', this.projectId, this.hash, 'tree'];
    const n = [{
      'name': 'Home',
      'paths': lis.slice(),
    }];

    paths.map(path => {
      lis.push(path);
      n.push({
          'name': path,
          'paths': lis.slice(),
        });
    });
    // Change detection issue
    setTimeout(() => {
      this.breadcrumbItems = n;
    });
  }
}
