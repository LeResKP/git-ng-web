import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import 'rxjs/add/operator/switchMap';

import { GitService } from './git.service';


@Component({
  template: `
  <div class="container-fluid">
    <app-breadcrumb [items]="breadcrumbItems"></app-breadcrumb>
    <div class="card" *ngIf="data$ | async as data">
      <div class="card-body">
        <div class="card-title">{{data.path}}</div>
        <table class="table-code">
          <tr *ngFor="let line of data.lines">
            <td class="code-line-number">{{line.line_num}}</td>
            <td class="code-pre">{{line.content}}</td>
          </tr>
        </table>
      </div>
    </div>
  </div>
  `,
})
export class BlobComponent implements OnInit {

  public data$;
  public breadcrumbItems = [];
  private projectId;
  private hash;

  constructor(private route: ActivatedRoute, private gitService: GitService) {}

  ngOnInit() {
    this.projectId = +this.route.parent.parent.snapshot.params['projectId'];
    this.hash = this.route.parent.parent.snapshot.params['sha'];
    const paths = this.route.snapshot.url.map((seg) => seg.path);
    const path = paths.join('/');
    this.data$ = this.gitService.blob(this.projectId, this.hash, path);
    this.updateBreadcrumb(paths);
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
    this.breadcrumbItems = n;
  }

}
