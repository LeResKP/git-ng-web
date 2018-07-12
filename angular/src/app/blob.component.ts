import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

import { Observable } from 'rxjs/Observable';
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
  private projectId;
  private hash;
  private filename: string;

  constructor(private route: ActivatedRoute, private gitService: GitService, private router: Router) {}

  ngOnInit() {

    this.data$ = this.route.paramMap.switchMap((params) => {
      this.projectId = this.route.parent.parent.snapshot.params['id'];
      this.hash = params.get('hash');
      const path = this.route.snapshot.url.map((seg) => seg.path).join('/');
      return this.gitService.blob(
        this.projectId, this.hash, path);
    });
  }

}
