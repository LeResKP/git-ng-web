import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

import 'rxjs/add/operator/switchMap';

import { GitService } from './git.service';


@Component({
  selector: 'app-commit',
  templateUrl: `./diff.component.html`,
})
export class CommitComponent implements OnDestroy, OnInit {

  public data$;

  constructor(private route: ActivatedRoute, private gitService: GitService, private router: Router) {}

  ngOnInit() {
    this.data$ = this.route.paramMap
        .switchMap((params: ParamMap) => {
          this.gitService.setCommitHash(params.get('hash'));
          document.querySelector('.autoscroll-right').scrollTop = 0;
          return this.gitService.getDiff(
            this.route.parent.parent.snapshot.params['id'], params.get('hash'));
        });
  }

  expand(line) {
    line.lines.map(l => l.type = 'context');
    line.type = 'hidden';
    return false;
  }

  ngOnDestroy() {
    this.gitService.setCommitHash(null);
  }

  close() {
    this.router.navigate([{outlets: {commit: null}} ], {relativeTo: this.route.parent});
  }

}
