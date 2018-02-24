import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap } from '@angular/router';

import 'rxjs/add/operator/switchMap';

import { GitService } from '../git.service';


@Component({
  selector: 'app-log-list',
  template: `
  <div class="container-fluid">
    <div class="row app-log-list">
      <div [class.col-md-4]="hash" [class.col-md-12]="!hash">
        <div class="app-log-groups">
        <div *ngFor="let log of logs$ | async">
          <div class="log-date small text-secondary"><i class="far fa-clock"></i> {{log[0] | date}}</div>
            <ul class="list-group">
              <li class="list-group-item" *ngFor="let log of log[1]" [class.active]="hash === log.hash">
                <a [routerLink]="['/p', projectId, 'b', branch, 'commits', log.hash]" class="nostyle d-block">
                  {{log.short_message}}
                  <div class="clearfix small">
                    <div class="float-left">{{log.author.name || log.author.email}}</div>
                    <div class="float-right"><a [routerLink]="['/p', projectId, 'b', branch, 'commits', log.hash]">{{log.short_hash}}</a></div>
                  </div>
                  <div class="small">
                    <span *ngFor="let label of log.labels" class="badge badge-secondary">{{label}}</span>
                  </div>
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>
      <div class="col-md-8" *ngIf="hash">
        <div class="clearfix">
          <a class="btn btn-default btn-sm float-right" (click)="hash=null"><i class="far fa-window-close"></i> Close diff</a>
        </div>
        <app-diff [hash]="hash"></app-diff>
      </div>
    </div>
  </div>
  `,
})
export class LogListComponent implements OnInit {

  public logs$;
  public projectId;
  public branch;

  public hash;

  constructor(private route: ActivatedRoute, private gitService: GitService) {}

  ngOnInit() {
    this.projectId = this.route.parent.snapshot.params['id'];
    this.logs$ = this.route.paramMap
        .switchMap((params: ParamMap) => {
          this.hash = params.get('hash');
          this.branch = params.get('branch');
          return this.gitService.getLogs(
            this.projectId,
            this.branch);
        });
  }

}
