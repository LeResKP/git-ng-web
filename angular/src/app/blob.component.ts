import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import 'rxjs/add/operator/switchMap';

import { GitService } from './git.service';


@Component({
  template: `
  <div class="container-fluid">
    <br>
    <br>
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

  constructor(private route: ActivatedRoute, private gitService: GitService) {}

  ngOnInit() {
    const projectId = +this.route.snapshot.params['projectId'];
    const hash = this.route.snapshot.params['sha'];
    const path = this.route.snapshot.url.map((seg) => seg.path).join('/');
    this.data$ = this.gitService.blob(projectId, hash, path);
  }

}
