import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap } from '@angular/router';

import 'rxjs/add/operator/switchMap';

import { GitService } from '../git.service';


@Component({
  selector: 'app-log-list',
  template: `
    <ul class="list-group">
      <li class="list-group-item" *ngFor="let log of logs$ | async">
        {{log.author}}<br>
        {{log.date}}<br>
        {{log.hash}}<br>
        <pre>{{log.message}}</pre>
      </li>
    </ul>
  `,
})
export class LogListComponent implements OnInit {

  public logs$;

  constructor(private route: ActivatedRoute, private gitService: GitService) {}

  ngOnInit() {
    this.logs$ = this.route.paramMap
        .switchMap((params: ParamMap) =>
          this.gitService.getLogs(
            this.route.parent.snapshot.params['id'],
            params.get('branch')));
  }

}
