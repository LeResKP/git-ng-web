import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/switchMap';

import { GitService } from '../git.service';


@Component({
  selector: 'app-log-list',
  template: `
  <div class="container-fluid">
    <div class="row app-log-list" *ngIf="logs as data">
      <div [class.sidebar]="hash" [class.col-md-12]="!hash" class="autoscroll" [class.hide]="!showLogs" [class.show]="showLogs" (mouseleave)="showLogs=false">
      <div class="text-right" *ngIf="hash"><a [routerLink]="[{ outlets: { commit: null } }]"><i class="fas fa-external-link-alt"></i></a></div>
        <a class="btn btn-sm float-right" [class.text-muted]="!details" (click)="toggleDetails()" *ngIf="!hash"><i class="fas fa-list"></i> Details</a>
        <div class="app-log-groups">
          <div *ngFor="let log of data.logs">
            <div class="log-date small text-secondary"><i class="far fa-clock"></i> {{log[0] | date}}</div>
              <ul class="list-group">
                <li class="list-group-item" *ngFor="let log of log[1]" [class.active]="hash === log.hash">
                  <a [routerLink]="[{ outlets: { commit: ['h', log.hash] } }]" queryParamsHandling="preserve" class="nostyle d-block" (click)="showLogs=false">
                    {{log.summary}}
                    <div class="clearfix small">
                      <div class="float-left">{{log.author.name || log.author.email}}</div>
                      <div class="float-right">{{log.short_hash}}</div>
                    </div>
                    <div class="small">
                      <span *ngFor="let branch of log.branches" class="badge badge-secondary mr-2">{{branch}}</span>
                    </div>
                  </a>
                  <ng-template [ngIf]="!hash && details">
                  <ul class="small list-unstyled stats" *ngIf="log.stats$ | async as stats">
                    <li *ngFor="let stat of stats.files">{{stat.filename}} <span class="color-added">+ {{stat.data.insertions}}</span> <span class="color-deleted">- {{stat.data.deletions}}</span></li>
                  </ul>
                  </ng-template>
                </li>
              </ul>
            </div>
          </div>
        <br>
        <br>
        <div class="text-center">
          <a class="btn btn-secondary btn-sm" [routerLink]="" [queryParams]="{r: data.rev, s: data.skip_newer}" *ngIf="data.skip_newer !== null">Newer</a>
          <a class="btn btn-secondary btn-sm" [routerLink]="" [queryParams]="{r: data.rev, s: data.skip_older}" *ngIf="data.skip_older !== null">Older</a>
        </div>
        <br>
        <br>
      </div>
      <div class="col-md-12 autoscroll autoscroll-right">
        <button class="btn btn-light btn-sm" (mouseover)="showLogs=true"><i class="fas fa-bars"></i></button>
        <router-outlet name="commit"></router-outlet>
      </div>
    </div>
  </div>
  `,
})
export class LogListComponent implements OnInit {

  public logs$: Observable<any>;
  public projectId: number;
  public hash: string;
  public details = false;
  public logs: any;
  private detailsLoaded = false;

  public showLogs = false;

  constructor(private route: ActivatedRoute, private cdr: ChangeDetectorRef, private gitService: GitService, private router: Router) {}

  ngOnInit() {

    this.projectId = +this.route.parent.snapshot.params['id'];

    const obsCombined = Observable.combineLatest(
      this.route.paramMap, this.route.queryParamMap,
      (params, qparams) => ({params, qparams}));

    obsCombined.switchMap(ap => this.gitService.getLogs(
      this.projectId,
      ap.params.get('branch'),
      ap.qparams.get('r'),
      ap.qparams.get('s'))
    ).subscribe((logs => {
      this.logs = logs;
      this.detailsLoaded = false;
    }));

    this.gitService.commitHash.subscribe((hash: string) => {
      setTimeout(() => this.hash = hash);
    });
  }

  toggleDetails() {
    if (!this.detailsLoaded) {
      this.logs.logs.map(l => {
        l[1].map(log => {
          log.stats$ = this.gitService.getLogDetails(this.projectId, log.hash);
        });
      });
      this.detailsLoaded = true;
    }
    this.details = ! this.details;
  }

}
