import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/switchMap';

import { GitService } from './git.service';


@Component({
  template: `
    <div *ngIf="projectId !== null"><a [routerLink]="['/p', projectId, 'commits', hash]" href="#">Commits</a></div>
    <ul *ngIf="data$ | async as data" class="list-unstyled">
      <li *ngFor="let file of data">
        <i [class.fa-folder]="file.type === 'tree'" [class.fa-file]="file.type === 'blob'" class="far"></i>
        <a *ngIf="file.type === 'tree'" [routerLink]="treeUrl(file)">{{file.name}}</a>
        <a *ngIf="file.type === 'blob'" [routerLink]="blobUrl(file)">{{file.name}}</a>
      </li>
    </ul>
  `,
})
export class TreeComponent implements OnInit {

  public data$;
  public projectId;
  public hash;

  constructor(private route: ActivatedRoute, private gitService: GitService, private router: Router) {}


  ngOnInit() {

    const obsCombined = Observable.combineLatest(
      this.route.paramMap, this.route.url,
      (params, url) => ({params, url}));

    this.data$ = obsCombined.switchMap((ap) => {
      this.projectId = this.route.parent.parent.snapshot.params['id'];
      this.hash = ap.params.get('hash');
      let path = ap.url.map((seg) => seg.path).join('/');
      if (path) {
        path += '/';
      }
      return this.gitService.tree(
        this.projectId, this.hash, path);
    });
  }

  treeUrl(file) {
    const paths = ['/p', this.projectId, 'tree', this.hash];
    if (!file.path) {
      return paths;
    }
    return paths.concat(file.path.split('/'));
  }

  blobUrl(file) {
    const paths = ['/p', this.projectId, 'blob', this.hash];
    if (!file.path) {
      return paths;
    }
    return paths.concat(file.path.split('/'));
  }
}
