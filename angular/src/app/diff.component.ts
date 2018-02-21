import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap } from '@angular/router';

import 'rxjs/add/operator/switchMap';

import { GitService } from './git.service';


@Component({
  selector: 'app-diff',
  templateUrl: `./diff.component.html`,
})
export class DiffComponent implements OnInit {

  public data$;

  constructor(private route: ActivatedRoute, private gitService: GitService) {}

  ngOnInit() {
    this.data$ = this.route.paramMap
        .switchMap((params: ParamMap) =>
          this.gitService.getDiff(
            this.route.parent.snapshot.params['id'],
            params.get('hash')));
  }

  expand(line) {
    line.lines.map(l => l.type = 'context');
    line.type = 'hidden';
    return false;
  }

}
