import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap } from '@angular/router';

import 'rxjs/add/operator/switchMap';

import { GitService } from '../git.service';


@Component({
  selector: 'app-log-list',
  template: `
    <ul class="list-group">
      <li class="list-group-item" *ngFor="let log of logs$ | async">
        <div class="clearfix small">
          <div class="float-left">{{log.author.name || log.author.email}}</div>
          <div class="float-left">
            <span *ngFor="let label of log.labels" class="badge badge-secondary ml-2">{{label}}</span>
          </div>
          <div class="float-right"><a [routerLink]="['/p', projectId, 'd', log.hash]">{{log.short_hash}}</a></div>
          <div class="float-right mr-2">{{log.date | date:'short'}}</div>
        </div>
        <a [routerLink]="['/p', projectId, 'd', log.hash]" class="nostyle">
          {{log.short_message}}
        </a>
      </li>
    </ul>
  `,
})
export class LogListComponent implements OnInit {

  public logs$;
  public projectId;

  constructor(private route: ActivatedRoute, private gitService: GitService) {}

  ngOnInit() {
    this.projectId = this.route.parent.snapshot.params['id'];
    this.logs$ = this.route.paramMap
        .switchMap((params: ParamMap) =>
          this.gitService.getLogs(
            this.projectId,
            params.get('branch')));
  }

}
