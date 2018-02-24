import { Component, Input } from '@angular/core';
import { ActivatedRoute, ParamMap } from '@angular/router';

import 'rxjs/add/operator/switchMap';

import { GitService } from './git.service';


@Component({
  selector: 'app-diff',
  templateUrl: `./diff.component.html`,
})
export class DiffComponent {

  public data$;
  private _hash;

  @Input()
  set hash(value) {
    if (value) {
      this._hash = value;
      this.load();
    }
  }

  get hash() {
    return this._hash;
  }

  constructor(private route: ActivatedRoute, private gitService: GitService) {}

  load() {
    this.data$ = this.route.paramMap
        .switchMap((params: ParamMap) =>
          this.gitService.getDiff(
            this.route.parent.snapshot.params['id'],
            this.hash));
  }

  expand(line) {
    line.lines.map(l => l.type = 'context');
    line.type = 'hidden';
    return false;
  }

}
